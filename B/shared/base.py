# shared/base.py
# SQLAlchemy declarative base shared by all models.
# Why: Single Base avoids circular imports and ensures one metadata for migrations.
# Relevant files: experiments/models.py, runs/models.py, shared/db.py

from sqlalchemy.orm import declarative_base

Base = declarative_base()
