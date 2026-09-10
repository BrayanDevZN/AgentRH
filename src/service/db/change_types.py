"""
Muda os tipos dos dados antes de salvar no cache e restaura ao ler.
"""

import base64
import json
from datetime import datetime
from uuid import UUID


class ChangeTypes:

    @staticmethod
    def to_cache(data:dict) -> dict:

        result = {}
        types = {}

        for field, value in data.items():

            if value is None:
                result[field] = ""
                types[field] = "none"

            elif isinstance(value, bool):
                result[field] = "1" if value else "0"
                types[field] = "bool"

            elif isinstance(value, int):
                result[field] = str(value)
                types[field] = "int"

            elif isinstance(value, float):
                result[field] = str(value)
                types[field] = "float"

            elif isinstance(value, UUID):
                result[field] = str(value)
                types[field] = "uuid"

            elif isinstance(value, datetime):
                result[field] = value.isoformat()
                types[field] = "datetime"

            elif isinstance(value, bytes):
                result[field] = base64.b64encode(value).decode("ascii")
                types[field] = "bytes"

            else:
                result[field] = value

        result["__types__"] = json.dumps(types)
        return result

    @staticmethod
    def from_cache(data:dict) -> dict:

        result = data.copy()
        types = json.loads(result.pop("__types__", "{}"))

        for field, type_name in types.items():

            value = result[field]

            match type_name:

                case "none":
                    result[field] = None

                case "bool":
                    result[field] = value == "1"

                case "int":
                    result[field] = int(value)

                case "float":
                    result[field] = float(value)

                case "uuid":
                    result[field] = UUID(value)

                case "datetime":
                    result[field] = datetime.fromisoformat(value)

                case "bytes":
                    result[field] = base64.b64decode(value)

        return result
