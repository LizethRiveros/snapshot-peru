"""Descarga las series de series.json (BCRPData) y las guarda como CSV en data/bcrp/.

Cada CSV se reescribe completo y ordenado por fecha; el historial (incluidas las
revisiones que haga la fuente) queda en git. Solo libreria estandar.

Uso: python scripts/snapshot.py [--desde AAAA-MM-DD]
"""
import argparse
import csv
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{code}/json/{a}/{b}"
UA = {"User-Agent": "snapshot-peru/0.1 (+historia versionada de series publicas del BCRP)"}
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8,
         "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12}


def iso(label: str) -> str:
    """'14.Oct.26' -> 2026-10-14 ; 'Sep.2026' -> 2026-09 ; '2026' -> 2026 ; otro -> tal cual."""
    p = label.split(".")
    try:
        if len(p) == 3 and p[1] in MESES:                       # diario
            y = int(p[2]); y += 2000 if y < 70 else 1900
            return f"{y:04d}-{MESES[p[1]]:02d}-{int(p[0]):02d}"
        if len(p) == 2 and p[0] in MESES:                       # mensual
            return f"{int(p[1]):04d}-{MESES[p[0]]:02d}"
    except ValueError:
        pass
    return label


def fetch(code: str, a: str, b: str) -> list[tuple[str, str, str]]:
    url = API.format(code=code, a=a, b=b)
    for intento in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                data = json.load(r)
            break
        except Exception as e:
            if intento == 3:
                raise
            time.sleep(2 ** intento)
    rows = []
    for p in data.get("periods", []):
        v = (p.get("values") or [""])[0]
        v = "" if v in ("n.d.", "n.d", None) else v
        rows.append((iso(p["name"]), v, p["name"]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="1990-01-01")
    args = ap.parse_args()
    hoy = date.today().isoformat()
    cfg = json.loads((ROOT / "series.json").read_text(encoding="utf-8"))
    out = ROOT / "data" / "bcrp"
    out.mkdir(parents=True, exist_ok=True)
    fallos = 0
    catalogo = []
    for s in cfg["bcrp"]:
        try:
            rows = fetch(s["code"], args.desde, hoy)
        except Exception as e:
            print(f"ERROR {s['code']}: {e}", file=sys.stderr)
            fallos += 1
            continue
        if not rows:
            print(f"AVISO {s['code']}: sin filas, no se sobrescribe", file=sys.stderr)
            fallos += 1
            continue
        rows.sort(key=lambda r: r[0])
        with open(out / f"{s['slug']}.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["fecha", "valor", "periodo_fuente"])
            w.writerows(rows)
        ult = next((r for r in reversed(rows) if r[1] != ""), rows[-1])
        catalogo.append({**s, "filas": len(rows), "ultima_fecha": ult[0], "ultimo_valor": ult[1]})
        print(f"{s['slug']}: {len(rows):,} filas, ultima {ult[0]} = {ult[1]}")
    (ROOT / "data" / "catalogo.json").write_text(
        json.dumps(catalogo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
