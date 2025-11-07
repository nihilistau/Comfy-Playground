from __future__ import annotations

from typing import Dict, Iterable, List

from .composer import load_flow_from_drive


def assert_required_nodes(flow: Dict, required_types: Iterable[str]) -> None:
    nodes = flow.get("nodes", [])
    present = {node.get("type") for node in nodes}
    missing = [rtype for rtype in required_types if rtype not in present]
    if missing:
        raise AssertionError(f"Missing required node types: {missing}")


def load_and_validate(identifier: str, *, required_nodes: Iterable[str]) -> Dict:
    flow = load_flow_from_drive(identifier)
    assert_required_nodes(flow, required_nodes)
    return flow
