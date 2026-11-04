#!/usr/bin/env python3
"""Compute the Odds tab's numbers and record them in data/odds_history.json.

This is the same model index.html runs (see the Odds tab and CLAUDE.md); if you change
one, change the other. Run from the project root:

  python3 scripts/odds.py                     print today's numbers
  python3 scripts/odds.py --record 2026-10-29 add or replace that day's row in the history
  python3 scripts/odds.py --data DIR          read the data files from DIR instead of data/
  python3 scripts/odds.py --seats             also print each chamber's projected Democratic seats (median, 8-in-10 range)
"""
import argparse
import json
import math
from pathlib import Path

RATING_MARGIN = {"Solid D": 17, "Likely D": 10, "Lean D": 7, "Toss Up": 0, "Lean R": -7, "Likely R": -10, "Solid R": -17}
SD_RACE, SD_NATION = 4.5, 3
GRID = [(-4 + 0.05 * j, math.exp(-((-4 + 0.05 * j) ** 2) / 2)) for j in range(161)]


def erf(x):  # Abramowitz-Stegun 7.1.26, as in index.html
    s, a = math.copysign(1, x), abs(x)
    t = 1 / (1 + 0.3275911 * a)
    return s * (1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * math.exp(-a * a))


def norm_cdf(z):
    return 0.5 * (1 + erf(z / math.sqrt(2)))


def chance_by_nation(means, base, need):
    out = []
    for z, _ in GRID:
        pmf = [1.0] + [0.0] * len(means)
        for i, m in enumerate(means):
            p = norm_cdf((m + SD_NATION * z) / SD_RACE)
            for k in range(i, -1, -1):
                pmf[k + 1] += pmf[k] * p
                pmf[k] *= 1 - p
        out.append(sum(pmf[max(0, need - base):]))
    return out


def grid_average(vals):
    return sum(w * v for (_, w), v in zip(GRID, vals)) / sum(w for _, w in GRID)


def compute(data):
    load = lambda n: json.loads((data / f"{n}.json").read_text(encoding="utf-8"))
    races, ratings = load("senate_races"), load("house_ratings")
    base = {r["chamber"]: r for r in load("chamber_baseline")}
    s, h = base["Senate"], base["House"]
    senate_means = [((r["avg_margin"] + RATING_MARGIN[r["cook"]]) / 2 if r["avg_margin"] not in (None, "") else RATING_MARGIN[r["cook"]])
                    for r in races if r["dem_side_party"] != "I"]
    house_means = [RATING_MARGIN[r["rating"]] for r in ratings for _ in range(int(r["seats"]))]
    sen = chance_by_nation(senate_means, int(s["d_not_up"]), int(s["d_control"]))
    hou = chance_by_nation(house_means, int(h["d_not_up"]), int(h["d_control"]))
    return {"both": round(grid_average([a * b for a, b in zip(sen, hou)]), 4),
            "senate": round(grid_average(sen), 4), "house": round(grid_average(hou), 4)}


def seats_by_nation(means, base):
    """Each chamber's seat-count distribution (Democratic seats), averaged over the nationwide-error grid."""
    tot = [0.0] * (len(means) + 1)
    for z, w in GRID:
        pmf = [1.0] + [0.0] * len(means)
        for i, m in enumerate(means):
            p = norm_cdf((m + SD_NATION * z) / SD_RACE)
            for k in range(i, -1, -1):
                pmf[k + 1] += pmf[k] * p
                pmf[k] *= 1 - p
        for k, v in enumerate(pmf):
            tot[k] += w * v
    W = sum(w for _, w in GRID)
    out, c = {}, 0
    for k, v in enumerate(tot):
        c += v / W
        for q, name in ((0.1, "lo"), (0.5, "median"), (0.9, "hi")):
            if name not in out and c >= q:
                out[name] = base + k
    return out


def seats(data):
    """The model's seat projection per chamber: median and the range it gave an 8-in-10 chance."""
    load = lambda n: json.loads((data / f"{n}.json").read_text(encoding="utf-8"))
    races, ratings = load("senate_races"), load("house_ratings")
    base = {r["chamber"]: r for r in load("chamber_baseline")}
    senate_means = [((r["avg_margin"] + RATING_MARGIN[r["cook"]]) / 2 if r["avg_margin"] not in (None, "") else RATING_MARGIN[r["cook"]])
                    for r in races if r["dem_side_party"] != "I"]
    house_means = [RATING_MARGIN[r["rating"]] for r in ratings for _ in range(int(r["seats"]))]
    s = seats_by_nation(senate_means, int(base["Senate"]["d_not_up"]))
    # The polls' count: races the Democrat leads in the polling average, or by rating where there's none.
    s["polls"] = int(base["Senate"]["d_not_up"]) + sum(
        1 for r in races if r["dem_side_party"] != "I"
        and (r["avg_margin"] if r["avg_margin"] not in (None, "") else RATING_MARGIN[r["cook"]]) > 0)
    return {"Senate": s, "House": seats_by_nation(house_means, int(base["House"]["d_not_up"]))}


def main():
    root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=root / "data")
    ap.add_argument("--record", metavar="YYYY-MM-DD")
    ap.add_argument("--seats", action="store_true", help="also print each chamber's projected Democratic seats as JSON")
    args = ap.parse_args()
    if args.seats:
        print(json.dumps(seats(args.data)))
    odds = compute(args.data)
    print(f"Both {odds['both']:.1%}  Senate {odds['senate']:.1%}  House {odds['house']:.1%}")
    if args.record:
        path = root / "data" / "odds_history.json"
        rows = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        rows = [r for r in rows if r["date"] != args.record] + [{"date": args.record, **odds, "note": ""}]
        rows.sort(key=lambda r: r["date"])
        path.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"Recorded {args.record} in data/odds_history.json ({len(rows)} days)")


if __name__ == "__main__":
    main()
