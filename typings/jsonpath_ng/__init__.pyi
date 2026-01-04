# Partial stub

from typing import Any, Self

class DatumInContext:
    context: Self | None
    value: Any
    path: JSONPath
    full_path: JSONPath

class JSONPath:
    def find(self, data: dict[str, Any]) -> list[DatumInContext]: ...
