# 2026 Midterms Tracker

A static web page (`index.html`) that reads JSON files from `data/`. There is no build step and no server code. Every figure on the page comes from a file in `data/`, so a daily update means editing those files.

## Daily update

When asked to "run the daily update" (or `/daily-update`):

1. **Read the current data** in `data/` so you know what's already there.
2. **Research what changed since the last update** with web search. Search each item separately:
   - Cook Political Report Senate and House rating changes.
   - RealClearPolitics polling averages for the Senate toss-ups (Election Central republishes them).
   - New public polls in competitive Senate races from the last week.
   - The most important news in each competitive Senate race and in the House battle.
   - The latest report on each House toss-up district (for its "Latest" headline).
   - Early-vote totals (University of Florida Election Lab) and big-state counts.
   - New national generic-ballot and presidential-approval polls.
   - Newly scheduled campaign events and voting deadlines.
3. **Update the files** (schemas below):
   - `daily_brief.json`: add 4–7 items dated today. Continue the id sequence (`b8`, `b9`, …). Never delete earlier days; the page folds them under "Earlier updates".
   - `senate_races.json` / `house_ratings.json` / `house_tossups.json`: change ratings, averages, notes and districts in place when a source says they changed.
   - `house_tossups.json` headlines: for every toss-up district, replace `headline`, `headline_source` and `headline_date` whenever there's a newer report than the one shown. One line in your own words, 125 characters or less, about what's happening in the race (a poll, money, ads, a debate, an endorsement, a scandal), not a rating change. Keep the old headline if nothing newer turned up. The House tab shows it in the table's "Latest" column and in the map's matchup view.
   - `senate_polls.json`: add new polls with new ids; keep the three or four most recent per race.
   - `national_polls.json`, `early_vote.json`, `key_dates.json`: replace stale entries; keep past key dates (the page dims them).
   - When a rating or average changes, say when in that race's note (for example "moved to Toss Up on Oct 30").
   - `candidates.json`: every candidate in a Senate or House toss-up needs a row (the validator lists any that are missing). When a race becomes a toss-up or a nominee changes, add the candidates as described under "Candidate photos" below.
4. **Run `python3 scripts/validate.py`** and fix every problem it reports.
   Then **record today's odds** with `python3 scripts/odds.py --record YYYY-MM-DD` (today's date). It adds today's row to `data/odds_history.json`, which the Odds tab charts day by day; rerunning it the same day replaces that day's row.
5. **Stop before committing.** Show a short summary of what changed and why, with sources, plus the Odds tab number before and after, and `git diff --stat`. Commit (`Daily update YYYY-MM-DD`) and push only after the user approves.

## Editorial rules

- Every figure needs a named source. If you can't find a source for something, leave it out.
- Summarize news in your own words. Never copy more than a few words from an article.
- The site is openly pro-Democratic: the owner is a Democrat and wants Democrats to win, so it doesn't need to read as neutral. The facts still have to be right, because the tracker is only useful if it's accurate: use reputable sources from across the spectrum (including Republican-leaning pollsters with a solid record), and don't leave out news or polls that are bad for Democrats.
- Don't put your own predictions in the text; the Odds tab's number is the page's forecast, and it comes from the model.
- When sources disagree (for example Cook vs. RealClearPolitics ratings), say so instead of picking one silently.
- Verify candidate names and spellings against a current source; don't rely on memory.
- Formatting: dates in data as `YYYY-MM-DD`; date ranges in text as `Oct 10–14` with an en dash; typographic apostrophes (’) in text people read.

## Data files

| File | One row per | Key fields |
|---|---|---|
| `senate_races.json` | Senate seat on the ballot (35) | `state`, `name`, `held_by` (D/R), `seat` (Regular/Special), `status` (Open/Incumbent), `incumbent`, `dem_side` (Democrat, or independent in NE), `dem_side_party` (D/I), `rep`, `cook` (Solid D … Solid R), `cook_order` (1–7), `avg_margin` (+ means dem_side leads; null if none), `avg_label`, `avg_source`, `other_ratings`, `watch` |
| `senate_polls.json` | Poll | `id`, `state`, `pollster`, `dates`, `sample` (LV/RV/""), `dem_side_pct`, `rep_pct`, `margin` (= dem_side_pct − rep_pct) |
| `house_ratings.json` | Cook rating (7) | `rating`, `seats` (must total 435), `cook_order` |
| `house_tossups.json` | Toss-up district | `district` (e.g. `CA-22`), `state`, `held_by` (party holding the seat now), `holder` ("Name (R)" or "Open (Name)"; the incumbent's name must match `dem` or `rep` exactly so the page can shade it), `dem`, `rep`, `note` (rating history; not shown on the page), `headline`, `headline_source`, `headline_date` |
| `chamber_baseline.json` | Chamber | `total`, `d_current`, `r_current`, `d_not_up`, `r_not_up`, `d_control`, `r_control` |
| `national_polls.json` | Poll | `id`, `pollster`, `dates`, `measure`, `result`, `margin_label` |
| `early_vote.json` | Place | `id`, `place`, `ballots` (number), `qualifier` (`more than`/`nearly`/""), `as_of`, `source` |
| `daily_brief.json` | News item | `id`, `date`, `order`, `category`, `headline`, `detail`, `source` |
| `key_dates.json` | Event | `id`, `date`, `label`, `detail` |
| `us_tiles.json` | State | Map layout only (`col`, `row`). Don't edit. |
| `odds_history.json` | Day | `date`, `both`, `senate`, `house` (chances from 0 to 1), `note`. Written by `scripts/odds.py --record`; don't edit by hand. |
| `candidates.json` | Toss-up candidate | `id` (slug, also the photo's file name), `chamber` (Senate/House), `race` (state code for Senate, district for House), `party` (D/R/I), `name` (must match the race files exactly), `photo` (`img/candidates/<id>.jpg` or ""), `photo_credit` ("Artist (license)"), `photo_source` (Commons file page), `fact`, `fact_source`, `fact_url` |

Seat math on the page is computed from `senate_races.json`, `house_ratings.json` and `chamber_baseline.json`; don't hard-code totals anywhere.

The Odds tab (chance Democrats win both the House and the Senate) is also computed in `index.html` from those three files: Cook ratings become expected margins, Senate RCP averages are blended in half and half, and a nationwide error shared by both chambers ties the races together. The method is explained on the tab. `scripts/odds.py` runs the same model in Python to record each day's number; if you change the model, change both and check they give the same result. Never type a probability into a data file; keeping the ratings and averages current is what keeps the number current.

## Candidate photos

The Senate and House tabs show toss-up matchups with a headshot and one short fact for each candidate.

- **Photos:** only freely licensed images from Wikimedia Commons (public domain, CC0, CC BY, CC BY-SA, or "copyrighted free use"). Check the license on the file page, and check it's the right person: same-name traps are common (Mike Rogers of Michigan vs. Alabama; Michael Bouchard Jr. vs. his father, the sheriff). Prefer plain front-facing portraits.
- **Cropping:** download each original into its own new, empty folder under /tmp, then crop it to the standard 240×300 face-centered headshot with `swiftc -O scripts/headshot.swift -o /tmp/headshot` and `/tmp/headshot <original> img/candidates/<id>.jpg`. Look at the result before using it.
- **No free photo:** leave `photo`, `photo_credit` and `photo_source` empty; the page shows the candidate's initials.
- **Facts:** one true, interesting fact of 110 characters or less, with a link to the source (usually the person's Wikipedia article, or the district's section of the 2026 House elections article when they have no article).

## Preview

`python3 -m http.server 8000`, then open http://localhost:8000. Opening `index.html` directly from Finder won't load the data.
