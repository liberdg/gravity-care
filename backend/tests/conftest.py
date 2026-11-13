import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import security, simulation
from app import seed as seed_module
from app.database import Base, get_db
from app.main import app

SENSOR = {"X-Sensor-Key": "demo-sensor-key"}


def make_client(monkeypatch, with_metrics: bool):
    monkeypatch.setattr(security, "ITERATIONS", 1000)  # tests rapides
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False)
    with Session() as db:
        seed_module.seed(db, with_metrics=with_metrics)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    simulation.session_factory = Session
    return TestClient(app)


@pytest.fixture()
def client(monkeypatch):
    yield make_client(monkeypatch, True)
    app.dependency_overrides.clear()
    simulation.session_factory = None


@pytest.fixture()
def empty_client(monkeypatch):
    yield make_client(monkeypatch, False)
    app.dependency_overrides.clear()
    simulation.session_factory = None


def login(client, username):
    pwd = {"medecin": "medecin-demo", "responsable": "responsable-demo", "astro_a": "astro-a-demo",
           "astro_b": "astro-b-demo", "astro_c": "astro-c-demo"}[username]
    r = client.post("/api/auth/login", json={"username": username, "password": pwd})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture()
def doc(client):
    return login(client, "medecin")


def ids(client, headers):
    return {a["code"]: a["id"] for a in client.get("/api/astronauts", headers=headers).json()}
