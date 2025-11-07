import os
from pathlib import Path
from src import downloader

def test_normalize_server_hash():
    headers = {'ETag': '"abc123"'}
    assert downloader.normalize_server_hash(headers) == 'abc123'
    headers = {'x-goog-hash': 'crc32c=12345, md5=deadbeef'}
    assert downloader.normalize_server_hash(headers) == 'deadbeef'

def test_compute_sha256(tmp_path):
    p = tmp_path / 'f.bin'
    p.write_bytes(b'hello')
    assert downloader.compute_sha256(p) == '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
