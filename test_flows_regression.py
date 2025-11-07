from pathlib import Path

from src.config import PlaygroundConfig
from src.flows import compose_flow, load_and_validate


def test_flow_regression_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("DRIVE_ROOT", str(tmp_path))
    cfg = PlaygroundConfig.load()
    path, _ = compose_flow("regression prompt", model_key="sd1", config=cfg)
    identifier = Path(path).name
    reloaded = load_and_validate(identifier, required_nodes=["StableDiffusion"])
    assert reloaded["meta"]["prompt"] == "regression prompt"
