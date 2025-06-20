import os
import sys

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add the parent directory to the path so that we can import from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models and database connection from the app
from app.database import Base  # noqa: E402

# Explicitly import all model *classes* to ensure they are registered with Base.metadata
# before target_metadata is defined for Alembic autogenerate.
from app.models.admin import Admin  # noqa: F401, E402
from app.models.attorney import Attorney  # noqa: F401, E402
from app.models.attorney_court_admission import attorney_court_admission_table  # noqa: F401, E402
from app.models.client import Client  # noqa: F401, E402
from app.models.court import Court  # noqa: F401, E402
from app.models.court_county import CourtCounty  # noqa: F401, E402
from app.models.district_court_contact import DistrictCourtContact  # noqa: F401, E402
from app.models.emergency_contact import EmergencyContact  # noqa: F401, E402
from app.models.example_model import Example  # noqa: F401, E402
from app.models.ice_detention_facility import IceDetentionFacility  # noqa: F401, E402
from app.models.user import User  # noqa: F401, E402

# Get the database URL from environment variables
database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/habeas")
config.set_main_option("sqlalchemy.url", database_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
