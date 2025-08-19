# FIX-125
# alembic/env.py

import os
import sys
import re
from logging.config import fileConfig
from sqlalchemy import pool, create_engine
from alembic import context
from dotenv import load_dotenv

# Loyiha asosiy papkasini sys.path'ga qo'shamiz
sys.path.append(os.getcwd())

# .env faylini yuklash
load_dotenv()

# settings.py faylidan sozlamalarni import qilish
from app.config.settings import settings
from app.db.models import Base
target_metadata = Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def _get_sync_db_url(db_url: str) -> str:
    """Asinxron URL'ni sinxron URL'ga o'tkazadi."""
    if "postgresql+asyncpg" in db_url:
        return db_url.replace("postgresql+asyncpg", "postgresql")
    elif "mysql+aiomysql" in db_url:
        return db_url.replace("mysql+aiomysql", "mysql")
    elif "sqlite+aiosqlite" in db_url:
        return db_url.replace("sqlite+aiosqlite", "sqlite")
    return db_url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = _get_sync_db_url(settings.DB_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Alembic uchun sinxron engine yaratamiz
    sync_db_url = _get_sync_db_url(settings.DB_URL)
    connectable = create_engine(
        sync_db_url,
        poolclass=pool.NullPool,
        future=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()