import importlib
import pkgutil
import logging
import threading
import time
from typing import List, Any, Dict

from core.plugins.protocols import (
    PluginProtocol,
    CallbackPluginProtocol,
    PluginStatus,
)

from core.container import Container as DIContainer
from config.config import ConfigManager


logger = logging.getLogger(__name__)


class PluginManager:
    """Simple plugin manager that loads plugins from the 'plugins' package."""

    def __init__(
        self,
        container: DIContainer,
        config_manager: ConfigManager,
        package: str = "plugins",
        health_check_interval: int = 60,
    ):
        self.container = container
        self.config_manager = config_manager
        self.package = package
        self.loaded_plugins: List[Any] = []
        self.plugins: Dict[str, PluginProtocol] = {}
        self.plugin_status: Dict[str, PluginStatus] = {}
        self.health_snapshot: Dict[str, Any] = {}
        self._health_check_interval = health_check_interval
        self._health_monitor_active = True
        self._health_thread = threading.Thread(
            target=self._health_monitor_loop, daemon=True
        )
        self._health_thread.start()

    def load_all_plugins(self) -> List[Any]:
        """Dynamically load all plugins from the configured package."""
        try:
            pkg = importlib.import_module(self.package)
        except ModuleNotFoundError:
            logger.info("Plugins package '%s' not found", self.package)
            return []

        results = []
        for loader, name, is_pkg in pkgutil.iter_modules(pkg.__path__):
            module_name = f"{self.package}.{name}"
            try:
                module = importlib.import_module(module_name)
                plugin = None
                if hasattr(module, "create_plugin"):
                    plugin = module.create_plugin()
                elif hasattr(module, "plugin"):
                    plugin = module.plugin
                elif hasattr(module, "init_plugin"):
                    plugin = module.init_plugin(self.container, self.config_manager)

                if plugin:
                    self.load_plugin(plugin)
                    results.append(plugin)
                self.loaded_plugins.append(module)
                logger.info("Loaded plugin %s", module_name)
            except Exception as exc:
                logger.error("Failed to load plugin %s: %s", module_name, exc)
        return results

    def load_plugin(self, plugin: PluginProtocol) -> bool:
        """Load a specific plugin instance"""
        try:
            config = {}
            if hasattr(plugin, "metadata"):
                name = plugin.metadata.name
            else:
                name = plugin.__class__.__name__

            if not callable(getattr(plugin, "health_check", None)):
                logger.error("Plugin %s does not implement health_check", name)
                self.plugin_status[name] = PluginStatus.FAILED
                return False

            success = plugin.load(self.container, config)
            if success:
                plugin.start()
                self.plugins[name] = plugin
                self.plugin_status[name] = PluginStatus.STARTED
                logger.info("Loaded plugin %s", name)
                return True
            self.plugin_status[name] = PluginStatus.FAILED
            return False
        except Exception as exc:
            logger.error(
                "Failed to load plugin %s: %s", getattr(plugin, "metadata", plugin), exc
            )
            return False

    def register_plugin_callbacks(self, app: Any) -> List[Any]:
        """Register callbacks for all loaded plugins"""
        results = []
        # expose health endpoint on first registration
        try:
            self.register_health_endpoint(app)
        except Exception as exc:
            logger.error("Failed to register plugin health endpoint: %s", exc)
        for plugin in self.plugins.values():
            if isinstance(plugin, CallbackPluginProtocol) or hasattr(
                plugin, "register_callbacks"
            ):
                try:
                    result = plugin.register_callbacks(app, self.container)
                    results.append(result)
                except Exception as exc:
                    logger.error("Failed to register callbacks for %s: %s", plugin, exc)
                    results.append(False)
        return results

    def get_plugin_health(self) -> Dict[str, Any]:
        """Return health status for all loaded plugins"""
        health = {}
        for name, plugin in self.plugins.items():
            try:
                plugin_health = plugin.health_check()
            except Exception as exc:
                plugin_health = {"healthy": False, "error": str(exc)}
            health[name] = {
                "health": plugin_health,
                "status": self.plugin_status.get(name),
            }
        return health

    def _health_monitor_loop(self) -> None:
        """Background loop to periodically collect plugin health"""
        while self._health_monitor_active:
            try:
                self.health_snapshot = self.get_plugin_health()
            except Exception as exc:
                logger.error("Health monitoring error: %s", exc)
            time.sleep(self._health_check_interval)

    def stop_health_monitor(self) -> None:
        """Stop the background health monitor thread"""
        self._health_monitor_active = False
        if self._health_thread.is_alive():
            self._health_thread.join(timeout=1)

    def register_health_endpoint(self, app: Any) -> None:
        """Expose aggregated plugin health via /health/plugins"""
        server = app.server if hasattr(app, "server") else app

        @server.route("/health/plugins", methods=["GET"])
        def plugin_health():
            return self.health_snapshot or self.get_plugin_health()
