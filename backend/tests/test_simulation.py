import time

from conftest import ids, login


def wait_done(client, headers, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        st = client.get("/api/simulation", headers=headers).json()
        if not st["running"]:
            return st
        time.sleep(0.1)
    raise AssertionError("simulation trop longue")


def test_astronaut_cannot_start_simulation(client):
    h = login(client, "astro_a")
    assert client.post("/api/simulation/start", json={}, headers=h).status_code == 403
    assert client.get("/api/simulation", headers=h).status_code == 200


def test_simulation_requires_login(client):
    assert client.get("/api/simulation").status_code == 401


def test_simulation_from_the_interface_fills_the_dashboard(empty_client):
    c = empty_client
    h = login(c, "medecin")
    assert c.post("/api/simulation/start", json={"speed": "rapide", "days": 30}, headers=h).status_code == 202
    st = wait_done(c, h)
    assert st["finished"] is True and st["error"] is None and st["progress"] == 1.0
    out = {a["code"]: a["status"] for a in c.get("/api/astronauts", headers=h).json()}
    assert out == {"A": "vert", "B": "rouge", "C": "orange"}


def test_simulation_replaces_previous_data(client):
    h = login(client, "medecin")
    client.post("/api/simulation/start", json={"speed": "rapide", "days": 10}, headers=h)
    wait_done(client, h)
    a = ids(client, h)["A"]
    daily = client.get(f"/api/astronauts/{a}/daily", headers=h).json()
    assert max(p["day"] for p in daily["spo2"]) == 10


def test_stop_simulation(empty_client):
    from app.simulation import runner
    c = empty_client
    h = login(c, "medecin")
    c.post("/api/simulation/start", json={"speed": "lente", "days": 30}, headers=h)
    time.sleep(0.2)
    assert c.post("/api/simulation/stop", headers=h).status_code == 200
    runner.wait(10)
    st = c.get("/api/simulation", headers=h).json()
    assert st["running"] is False and st["finished"] is False
