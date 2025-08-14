import types
from functools import lru_cache
from inspect import isclass

from strategy_field.utils import import_by_name  # noqa


@lru_cache(100)
def fqn(o: object, silent: bool=False) -> str:
    """Return the fully qualified class name of an object or a class."""
    parts = []
    if isinstance(o, str | bytes):
        return o
    if not hasattr(o, "__module__"):
        if silent:
            return None
        raise ValueError(f"Invalid argument `{type(o)}` {o}")
    parts.append(o.__module__)
    if isclass(o) or isinstance(o, types.FunctionType):
        parts.append(o.__name__)
    else:
        parts.append(o.__class__.__name__)
    return ".".join(parts)
