# config.py - app configuration
# NOTE: some of these might be overridden in app.py directly

import os

# Database config
# Jake originally set this up, Maria changed it when we moved to FastAPI
DB_NAME = os.environ.get("TRACKER_DB", "experiments.db")  # NOTE: app.py uses "tracker.db" hardcoded
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Server config
HOST = os.environ.get("HOST", "127.0.0.1")  # NOTE: app.py hardcodes "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))   # NOTE: app.py hardcodes 8000

# Feature flags (from the time we tried feature flags, most aren't checked anywhere)
ENABLE_TAGS = os.environ.get("ENABLE_TAGS", "false").lower() == "true"
ENABLE_EXPORT = os.environ.get("ENABLE_EXPORT", "false").lower() == "true"
ENABLE_AUTH = os.environ.get("ENABLE_AUTH", "false").lower() == "true"
ENABLE_METRICS_AGG = True  # always on, but the feature is half-built

# Max results (not actually used anywhere yet)
MAX_EXPERIMENTS = 100
MAX_RUNS_PER_EXPERIMENT = 500
MAX_TAGS_PER_EXPERIMENT = 20

# API keys (for the notification feature we never built)
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK", "")
EMAIL_API_KEY = os.environ.get("EMAIL_API_KEY", "")

# Export config
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")
EXPORT_FORMATS = ["csv", "json", "xlsx"]  # xlsx requires openpyxl which isn't in requirements
