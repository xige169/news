from pathlib import Path
import sys

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.main import app


client = TestClient(app)


def test_root_endpoint_returns_hello_world():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_news_categories_endpoint_is_registered():
    response = client.get("/api/news/categories")

    assert response.status_code == 200
    assert response.json() == {"message": "分组成功"}
