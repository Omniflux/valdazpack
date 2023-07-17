# Partial stub

from typing import Any, Self
from collections.abc import Iterable

class DatumInContext:
    context: Self | None
    value: Any
    path: JSONPath
    full_path: JSONPath

class JSONPath:
    def find(self, data: dict[str, Any]) -> Iterable[DatumInContext]: ...

def parse(string: str, debug: bool = ...) -> JSONPath: ...