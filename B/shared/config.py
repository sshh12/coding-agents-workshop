# shared/config.py
# Application configuration constants.
# Why: Centralizes all config so nothing is hardcoded in route or model files.
# Relevant files: shared/db.py, manage.py

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "tracker.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

HOST = "0.0.0.0"
PORT = 8000
