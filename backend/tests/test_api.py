from conftest import SENSOR, ids, login


def statuses(client, h, day=None):
    out = {}
    for code, i in ids(client, h).items():
        q = f"?as_of_day={day}" if day else ""
        out[code] = client.get(f"/api/astronauts/{i}/status{q}", headers=h).json()["status"]
    return out


# ---- connexion et rôles ----

def test_health(client):
    assert client.get("/api/health").json()["simulated_data"] is True


def test_login_bad_password(client):
    r = client.post("/api/auth/login", json={"username": "medecin", "password": "faux"})
    assert r.status_code == 401 and set(r.json()) == {"code", "message"}


def test_requires_login(client):
    assert client.get("/api/astronauts").status_code == 401


def test_astronaut_sees_only_himself(client, doc):
    h = login(client, "astro_a")
    mine = client.get("/api/astronauts", headers=h).json()
    assert [a["code"] for a in mine] == ["A"]
    b = ids(client, doc)["B"]
    assert client.get(f"/api/astronauts/{b}/status", headers=h).status_code == 403


def test_notes_are_for_doctors_only(client, doc):
    a = ids(client, doc)["A"]
    resp = login(client, "responsable")
    assert client.get(f"/api/astronauts/{a}/notes", headers=resp).status_code == 403
    r = client.post(f"/api/astronauts/{a}/notes", json={"text": "Surveiller le sommeil."}, headers=doc)
    assert r.status_code == 201 and r.json()["author"] == "medecin"
    assert client.get(f"/api/astronauts/{a}/notes", headers=doc).json()[0]["text"] == "Surveiller le sommeil."
    assert client.post(f"/api/astronauts/{a}/notes", json={"text": ""}, headers=doc).status_code == 422


# ---- scénario de démonstration ----

def test_statuses_on_last_day(client, doc):
    assert statuses(client, doc) == {"A": "vert", "B": "rouge", "C": "orange"}


def test_demo_scenario_day_21(client, doc):
    assert statuses(client, doc, 21) == {"A": "vert", "B": "orange", "C": "vert"}
    b = ids(client, doc)["B"]
    reasons = client.get(f"/api/astronauts/{b}/status?as_of_day=21", headers=doc).json()["reasons"]
    assert reasons and all("Règle de démonstration" in r["explanation"] and r["recommendation"] for r in reasons)


def test_calibration_period(client, doc):
    assert set(statuses(client, doc, 5).values()) == {"calibration"}


# ---- réception automatique et agrégation ----

def test_daily_aggregation(client, doc):
    a = ids(client, doc)["A"]
    daily = client.get(f"/api/astronauts/{a}/daily", headers=doc).json()
    assert len(daily["heart_rate_rest"]) == 30
    assert daily["heart_rate_rest"][0]["readings"] == 4
    assert daily["sleep_hours"][0]["readings"] == 1
    assert daily["activity_minutes"][0]["readings"] == 2
    assert [p["day"] for p in daily["spo2"]][:3] == [1, 2, 3]


def test_users_cannot_send_measures(client, doc):
    a = ids(client, doc)["A"]
    r = client.post(f"/api/astronauts/{a}/metrics", json={"indicator": "spo2", "value": 97}, headers=doc)
    assert r.status_code == 401 and r.json()["code"] == "invalid_sensor_key"


def test_sensor_rejects_out_of_range(client, doc):
    a = ids(client, doc)["A"]
    r = client.post(f"/api/astronauts/{a}/metrics", json={"indicator": "spo2", "value": 140}, headers=SENSOR)
    assert r.status_code == 422 and r.json()["code"] == "value_out_of_range"


def test_sensor_stream_is_aggregated_automatically(empty_client):
    c = empty_client
    h = login(c, "medecin")
    a = ids(c, h)["A"]
    for hour, v in [(2, 58.0), (8, 60.0), (14, 59.0), (20, 61.0)]:
        r = c.post(f"/api/astronauts/{a}/metrics",
                   json={"indicator": "heart_rate_rest", "value": v, "recorded_at": f"2026-03-01T{hour:02d}:00:00"},
                   headers=SENSOR)
        assert r.status_code == 201 and r.json()["source"] == "simulated"
    daily = c.get(f"/api/astronauts/{a}/daily", headers=h).json()["heart_rate_rest"]
    assert len(daily) == 1 and daily[0]["readings"] == 4 and daily[0]["value"] == 59.5
    assert c.get(f"/api/astronauts/{a}/status", headers=h).json()["status"] == "calibration"


def test_sensor_list_needs_key(client):
    assert client.get("/api/sensors/astronauts").status_code == 401
    assert len(client.get("/api/sensors/astronauts", headers=SENSOR).json()) == 3


def test_silent_sensor_detection(client, doc):
    i = ids(client, doc)
    before = client.get(f"/api/astronauts/{i['B']}/status", headers=doc).json()
    assert before["sensor_silent"] is False
    client.post(f"/api/astronauts/{i['A']}/metrics",
                json={"indicator": "spo2", "value": 97.5, "recorded_at": "2026-02-10T08:00:00"}, headers=SENSOR)
    st = {c: client.get(f"/api/astronauts/{n}/status", headers=doc).json() for c, n in i.items()}
    assert st["A"]["sensor_silent"] is False
    assert st["B"]["sensor_silent"] is True and st["B"]["silent_hours"] > 24


# ---- alertes, prévision, rapport ----

def test_alerts_and_ack_stay_after_new_reading(client, doc):
    i = ids(client, doc)
    alerts = client.get(f"/api/alerts?astronaut_id={i['B']}&level=rouge", headers=doc).json()
    assert alerts and all(a["level"] == "rouge" for a in alerts)
    acked = client.post(f"/api/alerts/{alerts[0]['id']}/ack", headers=doc).json()
    assert acked["acknowledged"] is True
    client.post(f"/api/astronauts/{i['B']}/metrics",
                json={"indicator": "hrv", "value": 30, "recorded_at": "2026-01-30T22:00:00"}, headers=SENSOR)
    again = client.get(f"/api/alerts?astronaut_id={i['B']}", headers=doc).json()
    assert any(a["id"] == acked["id"] and a["acknowledged"] for a in again)


def test_astronaut_cannot_ack_others_alert(client, doc):
    b = ids(client, doc)["B"]
    alert = client.get(f"/api/alerts?astronaut_id={b}", headers=doc).json()[0]
    assert client.post(f"/api/alerts/{alert['id']}/ack", headers=login(client, "astro_a")).status_code == 403
    assert client.post(f"/api/alerts/{alert['id']}/ack", headers=login(client, "astro_b")).status_code == 200


def test_responsable_cannot_ack(client):
    assert client.post("/api/alerts/1/ack", headers=login(client, "responsable")).status_code == 403


def test_forecast(client, doc):
    b = ids(client, doc)["B"]
    r = client.get(f"/api/astronauts/{b}/forecast", headers=doc).json()
    assert "incertaine" in r["warning"]
    sleep = r["forecast"]["sleep_hours"]
    assert [p["day"] for p in sleep] == [31, 32, 33] and sleep[0]["low"] <= sleep[0]["value"] <= sleep[0]["high"]


def test_report_for_doctor_only(client, doc):
    b = ids(client, doc)["B"]
    r = client.get(f"/api/astronauts/{b}/report?as_of_day=21", headers=doc)
    assert r.status_code == 200 and "DONNÉES SIMULÉES" in r.text and "Astro-B" in r.text
    assert client.get(f"/api/astronauts/{b}/report", headers=login(client, "astro_b")).status_code == 403


def test_unknown_astronaut_error_format(client, doc):
    r = client.get("/api/astronauts/999", headers=doc)
    assert r.status_code == 404 and set(r.json()) == {"code", "message"}
