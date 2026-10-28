#!/usr/bin/env python3
"""Check the tracker's data files for mistakes before publishing.

Run from the project root:  python3 scripts/validate.py
Exits with status 1 and lists every problem it finds.
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RATINGS = ["Solid D", "Likely D", "Lean D", "Toss Up", "Lean R", "Likely R", "Solid R"]
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
errors = []


def err(msg):
    errors.append(msg)


def load(name):
    try:
        rows = json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"{name}.json: can't read it ({e})")
        return []
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        err(f"{name}.json: must be a list of objects")
        return []
    return rows


def need(name, rows, fields):
    for i, r in enumerate(rows):
        for f in fields:
            if f not in r:
                err(f"{name}.json row {i}: missing '{f}'")


def unique(name, rows, key):
    seen = set()
    for r in rows:
        v = r.get(key)
        if v in seen:
            err(f"{name}.json: duplicate {key} '{v}'")
        seen.add(v)
    return seen


tiles = load("us_tiles")
need("us_tiles", tiles, ["state", "name", "col", "row"])
tile_states = unique("us_tiles", tiles, "state")
if len(tiles) != 50:
    err(f"us_tiles.json: expected 50 states, found {len(tiles)}")

races = load("senate_races")
need("senate_races", races, ["state", "name", "held_by", "seat", "status", "incumbent", "dem_side", "dem_side_party",
                             "rep", "cook", "cook_order", "avg_margin", "avg_label", "avg_source", "other_ratings", "watch"])
race_states = unique("senate_races", races, "state")
for r in races:
    s = r.get("state")
    if s not in tile_states:
        err(f"senate_races.json {s}: not a state in us_tiles.json")
    if r.get("cook") not in RATINGS:
        err(f"senate_races.json {s}: cook rating '{r.get('cook')}' must be one of {RATINGS}")
    elif r.get("cook_order") != RATINGS.index(r["cook"]) + 1:
        err(f"senate_races.json {s}: cook_order should be {RATINGS.index(r['cook']) + 1} for '{r['cook']}'")
    if r.get("held_by") not in ("D", "R"):
        err(f"senate_races.json {s}: held_by must be 'D' or 'R'")
    if r.get("dem_side_party") not in ("D", "I", ""):
        err(f"senate_races.json {s}: dem_side_party must be 'D', 'I' or ''")
    if r.get("avg_margin") is not None and not r.get("avg_label"):
        err(f"senate_races.json {s}: avg_margin is set but avg_label is empty")
    if r.get("cook") not in ("Solid D", "Solid R") and not r.get("rep"):
        err(f"senate_races.json {s}: competitive race needs a Republican candidate in 'rep'")

polls = load("senate_polls")
need("senate_polls", polls, ["id", "state", "pollster", "dates", "sample", "dem_side_pct", "rep_pct", "margin"])
unique("senate_polls", polls, "id")
for p in polls:
    pid = p.get("id")
    if p.get("state") not in race_states:
        err(f"senate_polls.json {pid}: state '{p.get('state')}' has no row in senate_races.json")
    try:
        if p["margin"] != p["dem_side_pct"] - p["rep_pct"]:
            err(f"senate_polls.json {pid}: margin should be dem_side_pct - rep_pct = {p['dem_side_pct'] - p['rep_pct']}")
    except (KeyError, TypeError):
        err(f"senate_polls.json {pid}: dem_side_pct, rep_pct and margin must be numbers")

base = load("chamber_baseline")
need("chamber_baseline", base, ["chamber", "total", "d_current", "r_current", "d_not_up", "r_not_up", "d_control", "r_control"])
sen = next((b for b in base if b.get("chamber") == "Senate"), None)
if sen and races and sen["d_not_up"] + sen["r_not_up"] + len(races) != sen["total"]:
    err(f"Senate seats don't add up: {sen['d_not_up']} D not up + {sen['r_not_up']} R not up + {len(races)} races != {sen['total']}")

hr = load("house_ratings")
need("house_ratings", hr, ["rating", "seats", "cook_order"])
if hr:
    if sorted(r.get("rating") for r in hr) != sorted(RATINGS):
        err("house_ratings.json: needs exactly one row per rating")
    total = sum(r.get("seats", 0) for r in hr)
    if total != 435:
        err(f"house_ratings.json: seats add up to {total}, not 435")

tu = load("house_tossups")
need("house_tossups", tu, ["district", "state", "held_by", "holder", "dem", "rep", "note", "headline", "headline_source", "headline_date"])
for t in tu:
    if not DAY.match(str(t.get("headline_date", ""))):
        err(f"house_tossups.json {t.get('district')}: headline_date must look like 2026-10-27")
    if not str(t.get("headline", "")).strip() or not str(t.get("headline_source", "")).strip():
        err(f"house_tossups.json {t.get('district')}: needs a headline and its source")
unique("house_tossups", tu, "district")
for t in tu:
    d = t.get("district", "")
    if not d.startswith(str(t.get("state")) + "-"):
        err(f"house_tossups.json {d}: state '{t.get('state')}' doesn't match the district")
toss = next((r.get("seats") for r in hr if r.get("rating") == "Toss Up"), None)
if toss is not None and toss != len(tu):
    err(f"house_tossups.json lists {len(tu)} districts but house_ratings.json says {toss} toss-ups")

nat = load("national_polls")
need("national_polls", nat, ["id", "pollster", "dates", "measure", "result", "margin_label"])
unique("national_polls", nat, "id")

ev = load("early_vote")
need("early_vote", ev, ["id", "place", "ballots", "qualifier", "as_of", "source"])
unique("early_vote", ev, "id")

br = load("daily_brief")
need("daily_brief", br, ["id", "date", "order", "category", "headline", "detail", "source"])
unique("daily_brief", br, "id")
for b in br:
    if not DAY.match(str(b.get("date", ""))):
        err(f"daily_brief.json {b.get('id')}: date must look like 2026-10-27")
    for f in ("headline", "detail", "source"):
        if not str(b.get(f, "")).strip():
            err(f"daily_brief.json {b.get('id')}: '{f}' is empty")

kd = load("key_dates")
need("key_dates", kd, ["id", "date", "label", "detail"])
unique("key_dates", kd, "id")
for k in kd:
    if not DAY.match(str(k.get("date", ""))):
        err(f"key_dates.json {k.get('id')}: date must look like 2026-11-03")

ROOT = DATA.parent
cands = load("candidates")
need("candidates", cands, ["id", "chamber", "race", "party", "name", "photo", "photo_credit", "photo_source", "fact", "fact_source", "fact_url"])
unique("candidates", cands, "id")
for c in cands:
    cid = c.get("id")
    if c.get("chamber") not in ("Senate", "House"):
        err(f"candidates.json {cid}: chamber must be 'Senate' or 'House'")
    if c.get("party") not in ("D", "R", "I"):
        err(f"candidates.json {cid}: party must be 'D', 'R' or 'I'")
    if c.get("photo"):
        if not (ROOT / c["photo"]).is_file():
            err(f"candidates.json {cid}: photo file {c['photo']} is missing")
        if not c.get("photo_credit") or not c.get("photo_source"):
            err(f"candidates.json {cid}: a photo needs photo_credit and photo_source")
    if not str(c.get("fact", "")).strip() or not c.get("fact_url"):
        err(f"candidates.json {cid}: needs a fact and its fact_url")
have = {(c.get("chamber"), c.get("race"), c.get("party"), c.get("name")) for c in cands}
def want(chamber, race, party, name):
    if name and (chamber, race, party, name) not in have:
        err(f"candidates.json: no row for {name} ({party}) in the {race} {chamber} toss-up; add one (photo optional)")
for r in races:
    if r.get("cook") == "Toss Up":
        want("Senate", r.get("state"), r.get("dem_side_party"), r.get("dem_side"))
        want("Senate", r.get("state"), "R", r.get("rep"))
for t in tu:
    want("House", t.get("district"), "D", t.get("dem"))
    want("House", t.get("district"), "R", t.get("rep"))

if errors:
    print(f"{len(errors)} problem(s) found:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("All data files look good.")
