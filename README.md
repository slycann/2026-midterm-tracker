# 2026 Midterms Tracker

A one-page tracker for the key 2026 Senate and House races: a state map, race ratings, recent polls, a daily news brief, upcoming dates, and an Odds tab with the chance Democrats win both chambers (computed from the ratings and polling averages; the tab explains how). It's a static site, so any static host can serve it.

```
index.html            the page
data/*.json           everything the page shows (edit these to update it)
vendor/               d3 and the fonts, bundled so the site has no outside dependencies
scripts/validate.py   checks the data files before you publish
CLAUDE.md             instructions Claude Code follows for the daily update
```

## Preview on your Mac

```bash
cd 2026-midterm-tracker
python3 -m http.server 8000
```

Open http://localhost:8000. The page loads its data with `fetch`, so opening `index.html` directly from Finder won't work.

## Publish with GitHub Pages

1. Create the repo and push:
   ```bash
   git init -b main && git add . && git commit -m "Initial tracker"
   gh repo create 2026-midterm-tracker --public --source=. --push
   ```
   (Without the GitHub CLI, create an empty repo on github.com, then `git remote add origin …` and `git push -u origin main`.)
2. On GitHub, open the repo's **Settings → Pages**, set **Source** to "Deploy from a branch", choose `main` and `/ (root)`, and save.
3. After a minute or two the site is live at `https://<your-username>.github.io/2026-midterm-tracker/`. Anyone can open it; no account needed.

Publishing Pages from a private repo requires a paid GitHub plan. The `.nojekyll` file tells Pages to serve the files as they are.

Other hosts work the same way: Cloudflare Pages or Netlify (connect the repo, no build command, output directory `/`), or an S3 bucket behind CloudFront if you want it in your own AWS account with a custom domain.

## Daily update with Claude Code

```bash
cd 2026-midterm-tracker
claude
```

Then type `/daily-update` (or just say "run the daily update"). Claude researches the day's changes, edits `data/`, runs the validator and stops to show you what changed. Review the diff and sources, then tell it to commit and push. Pages redeploys automatically, usually within a couple of minutes.

To change data by hand, edit the JSON files and run `python3 scripts/validate.py` before pushing.

## Notes before sharing widely

- Every item names its source, and news is summarized rather than quoted. Keep it that way.
- The About section says the tracker is compiled with AI help and may contain errors. Keep that note.
- Ratings and polls change quickly; the header shows the date of the latest brief so readers can tell how fresh it is.

## Licenses

d3 is ISC-licensed (`vendor/LICENSE-d3.txt`). Public Sans and Source Serif 4 are under the SIL Open Font License (`vendor/fonts/`).
