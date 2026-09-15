from typing import Any

from sqlalchemy.inspection import inspect


def model_to_dict(instance: Any) -> dict[str, Any]:
    """Converte apenas as colunas de um modelo SQLAlchemy em dicionário."""
    return {
        column.key: getattr(instance, column.key)
        for column in inspect(instance).mapper.column_attrs
    }
