#!/usr/bin/env python3
"""Rebuild data/money.json from the FEC's free bulk-download files.

For every candidate in data/candidates.json (matched by fec_id) it records money raised,
spent and cash on hand this cycle, the largest PAC and party contributions, and outside
(independent expenditure) spending for and against them. Run from the project root:

  python3 scripts/money.py                 download today's files into /tmp/fec-bulk-YYYY-MM-DD and rebuild
  python3 scripts/money.py --cache DIR     use (or fill) a different download folder
"""
import argparse
import csv
import io
import json
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE = "https://www.fec.gov/files/bulk-downloads/2026/"
FILES = {"weball": "weball26.zip", "cm": "cm26.zip", "pas2": "pas226.zip", "ie": "independent_expenditure_2026.csv"}


def fetch(cache, name):
    path = cache / FILES[name]
    if not path.exists():
        req = urllib.request.Request(BASE + FILES[name], headers={"User-Agent": "2026-midterm-tracker (github.com/slycann/2026-midterm-tracker)"})
        path.write_bytes(urllib.request.urlopen(req, timeout=300).read())
    return path


def lines(cache, name):
    with zipfile.ZipFile(fetch(cache, name)) as z:
        with z.open(z.namelist()[0]) as f:
            yield from io.TextIOWrapper(f, encoding="latin-1")


def main():
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, default=Path(f"/tmp/fec-bulk-{datetime.now():%Y-%m-%d}"))
    args = ap.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    cands = json.loads((root / "data/candidates.json").read_text(encoding="utf-8"))
    want = {c["fec_id"] for c in cands}

    totals = {f[0]: f for f in (l.rstrip("\n").split("|") for l in lines(args.cache, "weball")) if f[0] in want}
    names = {f[0]: f[1] for f in (l.split("|") for l in lines(args.cache, "cm"))}

    pacs = defaultdict(lambda: defaultdict(float))  # direct contributions from PACs and party committees (type 24K)
    for l in lines(args.cache, "pas2"):
        f = l.rstrip("\n").split("|")
        if f[16] in want and f[5] == "24K" and f[19] != "X":
            pacs[f[16]][f[0]] += float(f[14] or 0)

    # Outside spending: the same expenditure can appear in a 24/48-hour report and again in a
    # periodic report, so count each (spender, candidate, side, amount, date, payee) once.
    seen, ie, latest = set(), defaultdict(lambda: {"S": 0.0, "O": 0.0, "by": defaultdict(float)}), None
    with open(fetch(args.cache, "ie"), encoding="latin-1", newline="") as f:
        for r in csv.DictReader(f):
            c = r["cand_id"]
            if c not in want or r["sup_opp"] not in ("S", "O"):
                continue
            key = (r["spe_id"], c, r["sup_opp"], r["exp_amo"], r["dissem_dt"] or r["exp_date"], r["pay"].strip().upper())
            if key in seen:
                continue
            seen.add(key)
            amt = float(r["exp_amo"] or 0)
            ie[c][r["sup_opp"]] += amt
            if r["sup_opp"] == "O":
                ie[c]["by"][r["spe_nam"].strip()] += amt
            try:
                d = datetime.strptime(r["receipt_dat"], "%d-%b-%y")
                latest = max(latest, d) if latest else d
            except ValueError:
                pass

    to_day = lambda mdy: datetime.strptime(mdy, "%m/%d/%Y").strftime("%Y-%m-%d") if mdy else ""
    out = []
    for c in cands:
        fid, t = c["fec_id"], totals.get(c["fec_id"])
        top = lambda d: [{"name": n, "amount": round(a)} for n, a in sorted(d.items(), key=lambda x: -x[1])[:3]]
        out.append({
            "id": c["id"], "fec_id": fid,
            "raised": round(float(t[5])) if t else None, "spent": round(float(t[7])) if t else None,
            "cash": round(float(t[10])) if t else None, "through": to_day(t[27]) if t else "",
            "pac_total": round(sum(pacs[fid].values())), "top_pacs": top({names.get(k, k): v for k, v in pacs[fid].items()}),
            "outside_for": round(ie[fid]["S"]), "outside_against": round(ie[fid]["O"]), "top_against": top(ie[fid]["by"]),
            "outside_through": latest.strftime("%Y-%m-%d") if latest else "",
        })
    (root / "data/money.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote data/money.json for {len(out)} candidates; outside spending filed through {out[0]['outside_through']}")


if __name__ == "__main__":
    main()
