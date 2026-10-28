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
   - Early-vote totals (University of Florida Election Lab) and big-state counts.
   - New national generic-ballot and presidential-approval polls.
   - Newly scheduled campaign events and voting deadlines.
3. **Update the files** (schemas below):
   - `daily_brief.json`: add 4–7 items dated today. Continue the id sequence (`b8`, `b9`, …). Never delete earlier days; the page folds them under "Earlier updates".
   - `senate_races.json` / `house_ratings.json` / `house_tossups.json`: change ratings, averages, notes and districts in place when a source says they changed.
   - `senate_polls.json`: add new polls with new ids; keep the three or four most recent per race.
   - `national_polls.json`, `early_vote.json`, `key_dates.json`: replace stale entries; keep past key dates (the page dims them).
   - When a rating or average changes, say when in that race's note (for example "moved to Toss Up on Oct 30").
4. **Run `python3 scripts/validate.py`** and fix every problem it reports.
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
| `house_tossups.json` | Toss-up district | `district` (e.g. `CA-22`), `state`, `held_by`, `holder`, `dem`, `rep`, `note` |
| `chamber_baseline.json` | Chamber | `total`, `d_current`, `r_current`, `d_not_up`, `r_not_up`, `d_control`, `r_control` |
| `national_polls.json` | Poll | `id`, `pollster`, `dates`, `measure`, `result`, `margin_label` |
| `early_vote.json` | Place | `id`, `place`, `ballots` (number), `qualifier` (`more than`/`nearly`/""), `as_of`, `source` |
| `daily_brief.json` | News item | `id`, `date`, `order`, `category`, `headline`, `detail`, `source` |
| `key_dates.json` | Event | `id`, `date`, `label`, `detail` |
| `us_tiles.json` | State | Map layout only (`col`, `row`). Don't edit. |

Seat math on the page is computed from `senate_races.json`, `house_ratings.json` and `chamber_baseline.json`; don't hard-code totals anywhere.

The Odds tab (chance Democrats win both the House and the Senate) is also computed in `index.html` from those three files: Cook ratings become expected margins, Senate RCP averages are blended in half and half, and a nationwide error shared by both chambers ties the races together. The method is explained on the tab. Never type a probability into a data file; keeping the ratings and averages current is what keeps the number current.

## Preview

`python3 -m http.server 8000`, then open http://localhost:8000. Opening `index.html` directly from Finder won't load the data.
