"""Simulateur de capteurs : envoie AUTOMATIQUEMENT des mesures à l'API, comme le ferait un vrai appareil.

Les mesures sont SIMULÉES (reproductibles). Usage :
  python -m app.seed --reset --empty
  uvicorn app.main:app --reload            (dans un autre terminal)
  python -m app.sensor_simulator --interval 0.2

Options : --url, --key, --interval (secondes entre deux mesures), --days (1 à 30), --start AAAA-MM-JJ
Sans --start, la dernière journée simulée est aujourd'hui (UTC).
"""
import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

from . import simulate


def post(url: str, key: str, payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if payload is not None else "GET",
                                 headers={"Content-Type": "application/json", "X-Sensor-Key": key})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", default="http://localhost:8000")
    p.add_argument("--key", default="demo-sensor-key")
    p.add_argument("--interval", type=float, default=0.2)
    p.add_argument("--days", type=int, default=simulate.DAYS)
    p.add_argument("--start", default=None)
    args = p.parse_args()

    days = max(1, min(args.days, simulate.DAYS))
    if args.start:
        start = datetime.strptime(args.start, "%Y-%m-%d")
    else:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        start = today - timedelta(days=days - 1)

    ids = {a["code"]: a["id"] for a in post(f"{args.url}/api/sensors/astronauts", args.key)}
    stream = []
    for code in ids:
        for r in simulate.generate_readings(code):
            if r["day"] <= days:
                stream.append((r["day"], r["hour"], code, r))
    stream.sort(key=lambda x: (x[0], x[1], x[2]))
    print(f"Envoi de {len(stream)} mesures simulées pour {len(ids)} astronautes (Ctrl+C pour arrêter)...")
    sent = 0
    try:
        for day, hour, code, r in stream:
            when = simulate.reading_time(start, day, hour).isoformat()
            try:
                post(f"{args.url}/api/astronauts/{ids[code]}/metrics", args.key,
                     {"indicator": r["indicator"], "value": r["value"], "recorded_at": when})
            except urllib.error.HTTPError as e:
                print("Refusée :", e.read().decode())
                continue
            sent += 1
            if sent % 50 == 0:
                print(f"  {sent}/{len(stream)} mesures envoyées (jour {day})")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nArrêt demandé.")
    print(f"Terminé : {sent} mesures envoyées.")


if __name__ == "__main__":
    main()
