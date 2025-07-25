#!/usr/bin/env python3
"""
Complete application factory integration
"""
import dash
import logging
import os
from typing import Optional, Any
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
from core.unified_callback_coordinator import UnifiedCallbackCoordinator
import pandas as pd

# Use correct config system
from config.config import get_config

logger = logging.getLogger(__name__)


def create_app(mode: Optional[str] = None) -> dash.Dash:
    """Create a Dash application.

    Parameters
    ----------
    mode: Optional[str]
        One of ``"full"`` (default), ``"simple"`` or ``"json-safe"``. The value
        can also be provided via the ``YOSAI_APP_MODE`` environment variable.
    """

    mode = (mode or os.getenv("YOSAI_APP_MODE", "full")).lower()

    if mode == "simple":
        logger.info("Creating application in simple mode")
        return _create_simple_app()

    if mode in {"json-safe", "json_safe", "jsonsafe"}:
        logger.info("Creating application in JSON-safe mode")
        return _create_json_safe_app()

    logger.info("Creating application in full mode")
    return _create_full_app()


def _create_full_app() -> dash.Dash:
    """Create complete Dash application with full integration"""
    try:
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True,
            assets_folder="assets",
        )

        app.title = "Yōsai Intel Dashboard"

        # Use the working config system
        config_manager = get_config()

        # Skip plugin system for now (causing import issues)
        # We'll add this back after core functionality is working
        # plugin_manager = PluginManager(container, config_manager)
        # plugin_results = plugin_manager.load_all_plugins()
        # app._yosai_plugin_manager = plugin_manager

        # Set main layout
        app.layout = _create_main_layout()

        # Register all callbacks using UnifiedCallbackCoordinator
        coordinator = UnifiedCallbackCoordinator(app)
        _register_global_callbacks(coordinator)

        # Register page/component callbacks
        try:
            _register_page_callbacks(coordinator)
            from dashboard.layout.navbar import register_navbar_callbacks

            register_navbar_callbacks(coordinator)

            if config_manager.get_app_config().environment == "development":
                coordinator.print_callback_summary()
        except Exception as e:
            logger.warning(f"Failed to register module callbacks: {e}")

        # Initialize services
        _initialize_services()

        # Expose basic health check endpoint
        server = app.server

        @server.route("/health", methods=["GET"])
        def health():
            return {"status": "ok"}, 200

        logger.info("Complete Dash application created successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        raise


def _create_simple_app() -> dash.Dash:
    """Create a simplified Dash application"""
    try:
        from dash import html, dcc

        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True,
        )

        app.title = "Yōsai Intel Dashboard"

        app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                html.H1("🏯 Yōsai Intel Dashboard", className="text-center"),
                html.Hr(),
                html.Div(
                    [
                        dbc.Alert("✅ Application created successfully!", color="success"),
                        dbc.Alert("⚠️ Running in simplified mode (no auth)", color="warning"),
                        html.P("Environment configuration loaded and working."),
                        html.P("Ready for development and testing."),
                    ],
                    className="container",
                ),
            ]
        )

        # Expose basic health check endpoint
        server = app.server

        @server.route("/health", methods=["GET"])
        def health():
            return {"status": "ok"}, 200

        logger.info("Simple Dash application created successfully")
        return app

    except Exception as e:
        logger.error(f"Failed to create simple application: {e}")
        raise


def _create_json_safe_app() -> dash.Dash:
    """Create Dash application with JSON-safe layout"""
    try:
        from dash import html

        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True,
        )

        app.title = "🏯 Yōsai Intel Dashboard"

        app.layout = html.Div(
            [
                html.H1("🏯 Yōsai Intel Dashboard", className="text-center"),
                html.Hr(),
                dbc.Container(
                    [
                        dbc.Alert(
                            "✅ Application running with JSON-safe components",
                            color="success",
                        ),
                        dbc.Alert(
                            "🔧 All callbacks are wrapped for safe serialization",
                            color="info",
                        ),
                        html.P("Environment configuration loaded successfully."),
                        html.P("JSON serialization issues have been resolved."),
                    ]
                ),
            ]
        )

        # Expose basic health check endpoint
        server = app.server

        @server.route("/health", methods=["GET"])
        def health():
            return {"status": "ok"}, 200

        logger.info("JSON-safe Dash application created")
        return app

    except Exception as e:
        logger.error(f"Failed to create JSON-safe application: {e}")
        raise


def _create_main_layout() -> html.Div:
    """Simplified main layout"""
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            _create_navbar(),
            html.Div(id="page-content"),
            dcc.Store(id="global-store"),
        ]
    )


def _create_navbar() -> dbc.Navbar:
    """Create navigation bar"""
    return dbc.Navbar(
        [
            dbc.Container(
                [
                    # Brand
                    dbc.NavbarBrand(
                        [
                            html.I(className="fas fa-shield-alt me-2"),
                            "Yōsai Intel Dashboard",
                        ],
                        href="/",
                    ),
                    # Navigation links
                    dbc.Nav(
                        [
                            dbc.NavItem(
                                dbc.NavLink([
                                    html.I(className="fas fa-tachometer-alt me-1"),
                                    "Dashboard",
                                ], href="/"),
                            ),
                            dbc.NavItem(
                                dbc.NavLink([
                                    html.I(className="fas fa-chart-line me-1"),
                                    "Analytics",
                                ], href="/analytics"),
                            ),
                            dbc.NavItem(
                                dbc.NavLink([
                                    html.I(className="fas fa-chart-bar me-1"),
                                    "Graphs",
                                ], href="/graphs"),
                            ),
                            dbc.NavItem(
                                dbc.NavLink([
                                    html.I(className="fas fa-upload me-1"),
                                    "Upload",
                                ], href="/file-upload"),
                            ),
                            dbc.NavItem(
                                dbc.NavLink([
                                    html.I(className="fas fa-cog me-1"),
                                    "Settings",
                                ], href="/settings"),
                            ),
                            dbc.NavItem(
                                [
                                    dbc.Button(
                                        "🔄 Clear Cache",
                                        id="clear-cache-btn",
                                        color="outline-secondary",
                                        size="sm",
                                    )
                                ]
                            ),
                        ],
                        navbar=True,
                    ),
                ]
            )
        ],
        color="dark",
        dark=True,
        className="mb-4",
    )


def _create_placeholder_page(title: str, subtitle: str, message: str) -> html.Div:
    """Create placeholder page for missing modules"""
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(title, className="text-primary mb-3"),
                            html.P(subtitle, className="text-muted mb-4"),
                            dbc.Alert(message, color="warning"),
                        ]
                    )
                ]
            )
        ]
    )


@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    """Route pages based on URL"""
    if pathname in {"/", "/dashboard"}:
        return _get_dashboard_page()
    elif pathname == "/analytics":
        return _get_analytics_page()
    elif pathname == "/graphs":
        return _get_graphs_page()
    elif pathname == "/settings":
        return _get_settings_page()
    elif pathname == "/upload" or pathname == "/file-upload":  # Handle both paths
        return _get_upload_page()
    else:
        return html.Div(
            [
                html.H1("Page Not Found", className="text-center mt-5"),
                html.P(
                    "The page you're looking for doesn't exist.",
                    className="text-center",
                ),
                dbc.Button(
                    "Go Home", href="/", color="primary", className="d-block mx-auto"
                ),
            ]
        )


def _get_home_page() -> Any:
    """Alias for the dashboard page."""
    return _get_dashboard_page()


def _get_dashboard_page() -> Any:
    """Get dashboard page."""
    try:
        from pages.dashboard import layout

        return layout()
    except ImportError as e:
        logger.error(f"Dashboard page import failed: {e}")
        return _create_placeholder_page(
            "Dashboard",
            "Dashboard page is being loaded...",
            "The dashboard module is not available. Please check the installation.",
        )


def _get_graphs_page() -> Any:
    """Get graphs page."""
    try:
        from pages.graphs import layout

        return layout()
    except ImportError as e:
        logger.error(f"Graphs page import failed: {e}")
        return _create_placeholder_page(
            "Graphs",
            "Graphs page is being loaded...",
            "The graphs module is not available. Please check the installation.",
        )


def _get_settings_page() -> Any:
    """Get settings page."""
    try:
        from pages.settings import layout

        return layout()
    except ImportError as e:
        logger.error(f"Settings page import failed: {e}")
        return _create_placeholder_page(
            "Settings",
            "Settings page is being loaded...",
            "The settings module is not available. Please check the installation.",
        )




def _get_analytics_page() -> Any:
    """Get analytics page with complete integration"""
    try:
        from pages.deep_analytics.layout import layout

        return layout()
    except ImportError as e:
        logger.error(f"Analytics page import failed: {e}")
        return _create_placeholder_page(
            "📊 Analytics",
            "Analytics page is being loaded...",
            "The analytics module is not available. Please check the installation.",
        )


def _get_upload_page() -> Any:
    """Get upload page with complete integration"""
    try:
        from pages.file_upload.layout import layout

        return layout()
    except ImportError as e:
        logger.error(f"Upload page import failed: {e}")
        return _create_placeholder_page(
            "📁 File Upload",
            "File upload page is being loaded...",
            "The file upload module is not available. Please check the installation.",
        )


def _register_page_callbacks(coordinator: UnifiedCallbackCoordinator) -> None:
    """Simplified callback registration"""
    try:
        from pages.file_upload.callbacks import register_callbacks as register_upload
        from pages.deep_analytics.callbacks import register_callbacks as register_analytics

        register_upload(coordinator)
        register_analytics(coordinator)

        logger.info("Page callbacks registered successfully")
    except ImportError as e:
        logger.error(f"Failed to register callbacks: {e}")
        # Continue without failing


def _register_global_callbacks(manager: UnifiedCallbackCoordinator) -> None:
    """Register global application callbacks"""

    @manager.register_callback(
        Output("global-store", "data"),
        Input("clear-cache-btn", "n_clicks"),
        prevent_initial_call=True,
        callback_id="clear_cache",
        component_name="app_factory",
    )
    def clear_cache(n_clicks):
        """Clear application cache"""
        if n_clicks:
            try:
                # Clear uploaded data
                from pages.file_upload.helpers import clear_uploaded_data

                clear_uploaded_data()
                logger.info("Application cache cleared")
                return {
                    "cache_cleared": True,
                    "timestamp": pd.Timestamp.now().isoformat(),
                }
            except ImportError:
                logger.warning("Could not clear uploaded data - module not available")
                return {"cache_cleared": False}
        return {}

    # Register device learning callbacks
    from services.device_learning_service import create_learning_callbacks

    create_learning_callbacks()

    logger.info("Global callbacks registered successfully")


def _initialize_services() -> None:
    """Initialize all application services"""
    try:
        # Initialize analytics service
        from services import get_analytics_service

        analytics_service = get_analytics_service()
        health = analytics_service.health_check()
        logger.info(f"Analytics service initialized: {health}")

        # Initialize configuration
        config = get_config()
        app_config = config.get_app_config()
        logger.info(f"Configuration loaded for environment: {app_config.environment}")

    except Exception as e:
        logger.warning(f"Service initialization completed with warnings: {e}")


# Export the main function
__all__ = ["create_app"]
