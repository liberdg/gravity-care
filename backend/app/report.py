"""Rapport HTML imprimable (Ctrl+P puis « Enregistrer en PDF »)."""
from html import escape

from .engine import INDICATORS

STATUS_LABELS = {"vert": "Normal", "orange": "À surveiller", "rouge": "Attention requise", "calibration": "Calibration"}


def build_report(astronaut, status: str, reasons: list[dict], daily: dict, notes: list, as_of_day: int | None) -> str:
    e = escape
    rows = ""
    for ind, spec in INDICATORS.items():
        pts = daily.get(ind, [])[-7:]
        cells = "".join(f"<td>{p['value']:.2f}</td>" for p in pts)
        days = "".join(f"<th>J{p['day']}</th>" for p in pts)
        rows += f"<tr><th>{e(spec['label'])} ({e(spec['unit'])})</th>{cells}</tr><tr class='d'><td></td>{days.replace('th','td')}</tr>"
    alerts = "".join(
        f"<li><b>{e(r['level'].upper())}</b> – {e(r['explanation'])}<br><i>{e(r['recommendation'])}</i></li>" for r in reasons
    ) or "<li>Aucun écart détecté.</li>"
    note_items = "".join(
        f"<li><b>{e(n.author)}</b> ({n.created_at:%Y-%m-%d %H:%M}) : {e(n.text)}</li>" for n in notes
    ) or "<li>Aucune note.</li>"
    day_txt = f"jour de mission {as_of_day}" if as_of_day else "dernières données disponibles"
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Rapport {e(astronaut.alias)}</title>
<style>body{{font-family:sans-serif;max-width:900px;margin:24px auto;padding:0 12px}}
.warn{{background:#fff3cd;border:1px solid #e0b84a;padding:8px;font-weight:bold}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #bbb;padding:4px 6px;font-size:13px}}tr.d td{{color:#777;font-size:11px}}</style></head><body>
<div class="warn">DONNÉES SIMULÉES · Prototype de hackathon · Pas un dispositif médical · Aucun diagnostic</div>
<h1>Rapport de suivi : {e(astronaut.alias)}</h1>
<p>{e(astronaut.mission_role)} · {day_txt}</p>
<h2>Statut : {e(STATUS_LABELS.get(status, status))}</h2>
<h2>Alertes</h2><ul>{alerts}</ul>
<h2>Valeurs journalières récentes (7 derniers jours)</h2><table>{rows}</table>
<h2>Notes médicales</h2><ul>{note_items}</ul>
<p><small>Les règles d'alerte sont des règles de démonstration. Ce rapport ne remplace pas un avis médical.</small></p>
</body></html>"""
