import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_content(client):
    response = client.get("/")
    assert b"SecurePipeline DevSecOps Demo" in response.data


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_content(client):
    response = client.get("/health")
    assert b"Application is healthy" in response.data


def test_unknown_route_returns_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
