from datetime import datetime
from typing import Any


def to_data(x: Any) -> Any:
    if hasattr(x, "to_data"):
        return x.to_data()
    if isinstance(x, int):
        return str(x)
    if isinstance(x, list):
        return [to_data(g) for g in x]
    if isinstance(x, dict):
        return dict_to_data(x)
    if isinstance(x, datetime):
        return x.isoformat(timespec="milliseconds").replace("+00:00", "Z").replace(".000Z", "Z")
    return x


def dict_to_data(d: dict) -> dict:
    return {key: to_data(d[key]) for key in d}
