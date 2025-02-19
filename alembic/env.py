import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# Cargar las variables de entorno
load_dotenv(override=True)
DATABASE_URL = os.getenv("DATABASE_URL")

# Importa la Base y los modelos necesarios
from app.db.db import Base
from app.models import *

# este es el objeto Config de Alembic, que provee
# acceso a los valores del archivo .ini en uso.
config = context.config

# interpretar el archivo de configuración para el log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Se le asigna a target_metadata el metadata de la Base para soporte de 'autogenerate'
target_metadata = Base.metadata


# Agregar función para limitar los objetos a incluir en las migraciones autogeneradas
def include_object(object, name, type_, reflected, compare_to):
    # Solo incluir tablas que estén definidas en el metadata (es decir, en tus models)
    if type_ == "table":
        return name in target_metadata.tables
    return True


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
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        {"sqlalchemy.url": DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
