# Yōsai Intel Dashboard

An AI-powered modular security intelligence dashboard for physical access control monitoring.

## Architecture Overview

This project follows a fully modular design built around a dependency injection container.  Detailed diagrams explain how the pieces fit together:

- [Architecture](docs/architecture.md)
- [Data Flow](docs/data_flow.md)
- [System Diagram](docs/system_diagram.md)

The dashboard is extensible through a lightweight plugin system. Plugins live in the `plugins/` directory and are loaded by a `PluginManager`. See [docs/plugins.md](docs/plugins.md) for discovery and configuration details.

```
yosai_intel_dashboard/
├── app.py                     # Main application entry point
├── config/                    # Configuration management
│   ├── config.py              # Unified configuration loader
│   ├── database_manager.py    # Database connections and pooling
│   └── cache_manager.py       # Simple cache interface
├── models/                    # Data models and business entities
│   ├── base.py               # Base model classes
│   ├── entities.py           # Core entities (Person, Door, Facility)
│   ├── events.py             # Event models (AccessEvent, Anomaly)
│   ├── enums.py              # Enumerated types
│   └── access_events.py      # Access event operations
├── services/                  # Business logic layer
│   └── analytics_service.py  # Analytics and data processing
├── components/               # UI components
│   ├── analytics/            # Analytics-specific components
│   ├── navbar.py             # Navigation component
│   └── map_panel.py          # Map visualization
├── pages/                    # Multi-page application pages
│   ├── deep_analytics/       # Analytics package
│   └── file_upload/          # Upload package
├── utils/                    # Utility functions
└── assets/                   # Static assets and CSS
    └── css/                  # Modular CSS architecture
```

## 🚀 Quick Start

### Development Setup

1. **Clone and enter the project:**
   ```bash
   git clone <repository>
   cd yosai_intel_dashboard
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   ./scripts/setup.sh
   ```
   The script installs requirements from PyPI or a local `packages/` directory if
   present. Ensure dependencies are installed **before** running Pyright or using
   the Pylance extension. Missing packages will otherwise appear as unresolved
   imports.

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (e.g. set HOST and database info)
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the dashboard:**
   Open http://127.0.0.1:8050 in your browser

### Troubleshooting

If Pylance shows unresolved imports or type errors, your editor may not be
using the virtual environment where dependencies were installed. Try the
following steps:

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   ./scripts/setup.sh
   ```
   If you encounter errors like `module 'flask' has no attribute 'helpers'`,
   ensure there are no local directories named `flask`, `pandas`, or `yaml`
   in the project root. These placeholder packages can shadow the real
   libraries installed from `requirements.txt`. Delete them before running
   the application.

3. Restart your editor so Pylance picks up the correct interpreter.

### Production Deployment

Using Docker Compose:
```bash
docker-compose up -d
```
Docker Compose reads variables from a `.env` file in this directory. Set
`DB_PASSWORD` **and** `SECRET_KEY` there (or export them in your shell) before
starting the services.

Alternatively you can launch the app with Gunicorn:
```bash
gunicorn wsgi:server
```

## 🧪 Testing

Run the complete test suite:
```bash
# Run all unit and integration tests
pytest

# Run type checking
mypy .

# Check code quality
black . --check
flake8 .
```

The `tests/` directory contains the integration and unit tests for the
dashboard. Key entry points include `tests/test_integration.py`,
`tests/test_analytics_integration.py`, `tests/test_ai_device_generator.py` and
`tests/test_security_service.py`.

## 📋 Features

- **Real-time Security Monitoring**: Live access control event monitoring
- **AI-Powered Anomaly Detection**: Advanced pattern recognition
- **Interactive Analytics**: Deep dive data analysis with file uploads
- **Automatic Data Summaries**: Charts for numeric distributions and top categories
- **Modular Architecture**: Easy to maintain, test, and extend
- **Multi-page Interface**: Organized functionality across multiple pages
- **Type-Safe**: Full type annotations and validation
- **CSRF Protection Plugin**: Optional production-ready CSRF middleware for Dash
- **Machine-Learned Column Mapping**: Trainable model for smarter CSV header recognition

**Note:** The file upload and column mapping functionality relies on `pandas`.
If `pandas` is missing these pages will be disabled. Ensure you run
`pip install -r requirements.txt` to install all dependencies.

## 🔧 Configuration

This project uses **`config/config.py`** for application settings. It
loads defaults from `config/config.yaml` and allows environment variables to
override any value. Earlier versions used separate modules like
`app_config.py`, `simple_config.py` and `config_manager.py`; all of these are
replaced by the unified `ConfigManager` in `config/config.py`.

### Database

Configure your database in `.env`:
```
DB_TYPE=postgresql  # or 'sqlite' or 'mock'
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### Application

Key configuration options:
```
DEBUG=False           # Set to False for production
HOST=0.0.0.0         # Bind to all interfaces for production
PORT=8050            # Application port
SECRET_KEY=your-key  # Change for production
```

The secret key is not included in the default YAML files. Define
`SECRET_KEY` in your environment or a `.env` file before starting the application. This variable is accessed via the `SecretManager` helper.

When `YOSAI_ENV=production` the application will refuse to start unless both
`DB_PASSWORD` and `SECRET_KEY` are provided via environment variables or Docker
secrets.

### Environment Overrides

`ConfigManager` loads YAML files from `config/` and then checks for
environment variables. When a variable name matches a key used in the YAML
configuration (for example `DB_HOST`, `DB_USER`, `REDIS_HOST` or
`SECRET_KEY`), its value replaces the one from the file. This lets you adjust
settings without editing the YAML files.

Example:

```bash
DB_HOST=localhost
DB_USER=postgres
REDIS_HOST=localhost
SECRET_KEY=supersecret
python app.py
```

These values override `database.host`, `database.username`, `cache.host` and
`security.secret_key` from the loaded YAML.

### Additional Environment Variables

Two optional variables control which configuration file is loaded:

- `YOSAI_ENV` – set to `development`, `staging`, `production` or `test` to
  automatically load the matching file in `config/` (default: `development`).
- `YOSAI_CONFIG_FILE` – absolute path to a custom YAML configuration file. When
  set it takes precedence over `YOSAI_ENV`.
- `YOSAI_APP_MODE` – set to `full`, `simple` or `json-safe` to select the
  startup mode for `create_app()` (default: `full`).

Example:

```bash
YOSAI_ENV=production python app.py
# or
YOSAI_CONFIG_FILE=/path/to/custom.yaml python app.py
YOSAI_APP_MODE=simple python app.py
```

#### Dynamic Constants

The new `DynamicConfigManager` reads several optional environment variables to
override security and performance defaults:

- `PBKDF2_ITERATIONS` – password hashing iterations
- `RATE_LIMIT_API` – number of requests allowed per window
- `RATE_LIMIT_WINDOW` – rate limit window in minutes
- `MAX_UPLOAD_MB` – maximum allowed upload size
- `DB_POOL_SIZE` – database connection pool size

### Plugins

Plugins live in the `plugins/` directory. Place any custom plugin package inside
this folder, for example `plugins/my_plugin/plugin.py` defining a
`create_plugin()` function. Enable the plugin by adding a section under
`plugins:` in `config/config.yaml` and setting `enabled: true` plus any plugin
options. In your app factory create a `PluginManager`, call
`load_all_plugins()` and then `register_plugin_callbacks(app)` to activate all
enabled plugins. See [docs/plugins.md](docs/plugins.md) for a detailed overview
of discovery, configuration and the plugin lifecycle.

### Migration Notes

Older modules `config/app_config.py`, `config/simple_config.py` and the
previous `config_manager.py` have been removed. Replace any imports of these
files with:

```python
from config.config import ConfigManager, get_config
```

The new `ConfigManager` provides the combined functionality of the deprecated
files while maintaining backwards compatible helper functions like
`get_app_config()` and `get_database_config()`.

## 📊 Modular Components

### Database Layer (`config/`)
- **database_manager.py**: Connection pooling, multiple database support
- Supports PostgreSQL, SQLite, and Mock databases
- Type-safe connection management
- Retry logic via `connection_retry.py` with exponential backoff
- Safe Unicode handling with `unicode_handler.py`
- Connection pooling through `connection_pool.py`
```python
from config.database_manager import EnhancedPostgreSQLManager, DatabaseConfig
manager = EnhancedPostgreSQLManager(DatabaseConfig(type="postgresql"))
manager.execute_query_with_retry("SELECT 1")
```

### Models Layer (`models/`)
- **entities.py**: Core business entities
- **events.py**: Event and transaction models
- **enums.py**: Type-safe enumerations
- Full type annotations and validation
- **Guide**: [docs/models_guide.md](docs/models_guide.md) explains each model file

### Services Layer (`services/`)
- **analytics_service.py**: Business logic for analytics ([docs](docs/analytics_service.md))
- **device_learning_service.py**: Persists learned device mappings ([docs](docs/device_learning_service.md))
- Caching and performance optimization
- Modular and testable

### Components Layer (`components/`)
- Reusable UI components
- Independent and testable
- Type-safe prop interfaces

## 🔐 Authentication & Secrets

This project uses Auth0 for OIDC login. Configure the following environment
variables or Docker secrets:

- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `AUTH0_DOMAIN`
- `AUTH0_AUDIENCE`

All secrets can be provided via the `SecretManager` which supports `env`,
`aws`, and `vault` backends. Place these values in `.env` or mount them as
Docker secrets. See the [architecture diagram](docs/auth_flow.png) for
implementation details.

## 🌐 Language Toggle

Internationalization is built in with Flask-Babel. Click the language dropdown in the navigation bar to switch between English and Japanese. No additional environment variables are required.
If you encounter an error like `"Babel" object has no attribute "localeselector"` when starting the app, ensure that the `Flask-Babel` package is installed and up to date (version 4 or later). The application now falls back to the new `locale_selector_func` API when needed.

![Language Toggle Demo](docs/i18n_demo.gif)

## 📚 Documentation

See the [data model diagram](docs/data_model.md) for an overview of key entities.

## 🤝 Contributing

1. Ensure all tests pass: `pytest`
2. Format code with `black` and run `flake8`
3. Follow type safety guidelines and maintain the modular architecture
4. Add tests for new functionality and update documentation when applicable

## 📦 Versioning

This project adheres to [Semantic Versioning](https://semver.org). See
[docs/release.md](docs/release.md) for details on how releases are managed.

## 📄 License

MIT License - see LICENSE file for details.
