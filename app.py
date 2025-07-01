import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point with comprehensive error handling"""
    try:
        logger.info("🏯 Starting Yōsai Intel Dashboard...")
        from core.app_factory import create_app
        from config.config import get_config

        config = get_config()
        app_config = config.get_app_config()

        logger.info(f"Environment: {app_config.environment}")
        logger.info(f"Debug mode: {app_config.debug}")

        app = create_app()

        if app_config.debug:
            logger.info("✅ App created successfully")
            logger.info(f"📝 Registered {len(app.callback_map)} callbacks:")
            for i, cb_id in enumerate(list(app.callback_map.keys())[:10]):
                logger.info(f"   {i+1}. {cb_id}")
            if len(app.callback_map) > 10:
                logger.info(f"   ... and {len(app.callback_map) - 10} more")

        logger.info("=" * 60)
        logger.info(f"🌐 Dashboard URL: http://{app_config.host}:{app_config.port}")
        logger.info(f"📁 File Upload: http://{app_config.host}:{app_config.port}/file-upload")
        logger.info(f"📊 Analytics: http://{app_config.host}:{app_config.port}/analytics")
        logger.info("=" * 60)

        app.run_server(
            host=app_config.host,
            port=app_config.port,
            debug=app_config.debug
        )

    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        logger.error("Stack trace:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
