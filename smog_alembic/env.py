from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

from smog.dbschema import Base

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

    raise Exception("untested")

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
    from smog.file import FileStat
    from smog.const import DEFAULT_MEDIA_DB, SMOG_DB_NAME
    from smog.dbconf import SqliteConf

    f = FileStat(DEFAULT_MEDIA_DB).join([SMOG_DB_NAME])
    f.makedirs()
    # FileStat.setenv("ALEMBIC_CONFIG", ...)

    # todo
    # other database support
    # different path location get from smog cmd-line
    db = SqliteConf(SMOG_DB_NAME, DEFAULT_MEDIA_DB)
    connectable = db.open_db()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# https://alembic.sqlalchemy.org/en/latest
# ->
# https://alembic.sqlalchemy.org/en/latest/autogenerate.html

# alembic --config smog_alembic/alembic.ini revision --autogenerate -m "initial"
# alembic --config smog_alembic/alembic.ini upgrade head
# alembic --config smog_alembic/alembic.ini downgrade revision_label

# https://alembic.sqlalchemy.org/en/latest/cookbook.html

# api !!!
# https://alembic.sqlalchemy.org/en/latest/api/index.html
