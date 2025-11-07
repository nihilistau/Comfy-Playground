import multiprocessing
import time
import requests
import os
from src import composer

def _run_server():
    from flask import Flask, request, jsonify
    app = Flask('testserver')

    @app.route('/api/flow/run', methods=['POST'])
    def run_flow():
        data = request.get_json() or {}
        return jsonify({'received': True, 'len': len(str(data))})

    app.run(port=5005)

def test_prompt_to_image_integration(monkeypatch):
    p = multiprocessing.Process(target=_run_server, daemon=True)
    p.start()
    time.sleep(1)
    # compose a trivial flow
    path, flow = composer.compose_flow('integration test prompt')
    # post to the local mocked server
    r = requests.post('http://127.0.0.1:5005/api/flow/run', json={'flow': flow})
    assert r.status_code == 200
    assert r.json().get('received')
    p.terminate()
