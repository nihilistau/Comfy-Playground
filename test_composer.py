import os
from src import composer

def test_compose_flow(tmp_path, monkeypatch):
    monkeypatch.setenv('DRIVE_ROOT', str(tmp_path))
    path, flow = composer.compose_flow('a cat on a skateboard', model_key='sd-1', sampler='DDIM', steps=5)
    assert 'nodes' in flow
    assert 'prompt' in flow['nodes'][0]['params'] or 'prompt' in flow['nodes'][0].get('params', {})
