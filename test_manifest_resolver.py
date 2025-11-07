import pytest
from src import manifest_resolver

class DummyResp:
    def __init__(self, url, headers, status_code=200):
        self.url = url
        self.headers = headers
        self.status_code = status_code

def test_preview_url(monkeypatch):
    def fake_head(url, allow_redirects=True, headers=None, timeout=15):
        return DummyResp('https://example.com/final', {'content-length': '12345'}, 200)
    monkeypatch.setattr('requests.head', fake_head)
    res = manifest_resolver.preview_url('https://example.com/some')
    assert res.get('final_url') == 'https://example.com/final'
    assert res.get('headers', {}).get('content-length') == '12345'
