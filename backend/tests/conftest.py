import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


def pytest_configure() -> None:
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"  # noqa: E402


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.db.connection import Base, engine
    from app.main import app

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def room_id(client: TestClient) -> int:
    response = client.post(
        "/rooms",
        json={
            "nombre": "Aula de pruebas",
            "edificio": "Edificio de pruebas",
            "capacidad": 30,
            "equipamiento": ["proyector"],
        },
    )
    assert response.status_code == 201
    return response.json()["id"]
