from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.lifecycle import create_app


@pytest.fixture
def client(tmp_path: Path):
    settings = Settings(port=5102, internal_token="dev-token", data_dir=tmp_path)
    with TestClient(create_app(settings), base_url="http://127.0.0.1:5102") as test_client:
        yield test_client


def test_health_is_public(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "py-svc"}


@pytest.mark.parametrize("headers", [{}, {"X-Internal-Token": "wrong-token"}])
def test_analyze_requires_token(client: TestClient, headers: dict[str, str]):
    response = client.post("/analyze", json={"text": "hello"}, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "unauthorized"}


def test_analyze_english(client: TestClient):
    response = client.post("/analyze", json={"text": "Hello world. Hello again!"}, headers={"X-Internal-Token": "dev-token"})
    assert response.status_code == 200
    assert response.json() == {
        "charCount": 25,
        "wordCount": 4,
        "sentenceCount": 2,
        "topKeywords": [{"word": "hello", "count": 2}, {"word": "again", "count": 1}, {"word": "world", "count": 1}],
    }


def test_analyze_thai(client: TestClient):
    response = client.post("/analyze", json={"text": "แมวกินปลา แมวกินข้าว"}, headers={"X-Internal-Token": "dev-token"})
    assert response.status_code == 200
    assert response.json()["charCount"] == 20
    assert response.json()["sentenceCount"] == 1
    assert response.json()["wordCount"] >= 2


def test_analyze_empty_text_is_bad_request(client: TestClient):
    response = client.post("/analyze", json={"text": "   "}, headers={"X-Internal-Token": "dev-token"})
    assert response.status_code == 400


def test_analyze_text_over_limit_is_payload_too_large(client: TestClient):
    response = client.post("/analyze", json={"text": "x" * 100_001}, headers={"X-Internal-Token": "dev-token"})
    assert response.status_code == 413


def test_shutdown_requires_token(client: TestClient):
    assert client.post("/shutdown").status_code == 401

def test_invalid_host_is_rejected(client: TestClient):
    response = client.get("/health", headers={"Host": "example.com"})
    assert response.status_code == 400
