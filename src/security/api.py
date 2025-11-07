from __future__ import annotations

from typing import Dict, Iterable


def set_api_key(name: str, key: str, target_globals: Dict[str, str]) -> bool:
    """Set an API key in the provided globals dict without writing to disk."""
    if not key:
        return False
    target_globals[name] = key
    return True


def mask_value(value: str, visible: int = 4) -> str:
    if not value:
        return ""
    return value[:visible] + "…" if len(value) > visible else value


def list_defined_keys(names: Iterable[str], scope: Dict[str, str]) -> Dict[str, str]:
    return {name: mask_value(scope.get(name, "")) for name in names if name in scope}
