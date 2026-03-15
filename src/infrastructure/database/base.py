from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


# Naming convention for constraints — ensures deterministic Alembic migration names
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Register all ORM models here so Alembic autogenerate detects them.
# Add imports below as new contexts are created.
def import_all_models() -> None:
    from src.contexts.accounts.infrastructure.models import account_model  # noqa: F401
    from src.contexts.transactions.infrastructure.models import transaction_model  # noqa: F401
