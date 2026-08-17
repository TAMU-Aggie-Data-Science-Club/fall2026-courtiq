# Data

This file explains **PlayPulse's** suggested data sources — where they come from, how to get them, and how to think about using them.

> **`DATA.md` is tracked in git. The `data/` folder is not.** Raw data is often large or governed by ToS, and must never be committed. Clone the repo, then populate `data/` locally.

## Suggested sources (starting point)

| Source | Origin / URL | Access method | License | Sensitivity | Notes |
|--------|--------------|---------------|---------|-------------|-------|
| NBA Stats API (unofficial) | https://github.com/swar/nba_api | `pip install nba_api` | Unofficial — respect rate limits | None | Box scores, play-by-play, shot charts back to the 1940s |
| Basketball-Reference | https://www.basketball-reference.com | HTML scrape via `basketball_reference_scraper` | Personal / educational use — **respect robots.txt** | None | Great for advanced stats and coaches / historical detail |
| Kaggle NBA datasets | https://www.kaggle.com/datasets?search=nba | Kaggle download | Per-dataset | None | Pre-assembled CSVs — fine for prototyping, verify vintage |
| NBA API stats.nba.com direct | https://stats.nba.com | HTTP (via `nba_api`) | Unofficial | None | Same source `nba_api` wraps; go here only if the wrapper misses an endpoint |

## How to think about using each source

- **Rate limits.** `nba_api` and stats.nba.com will hard-block a naive scraper. Use the wrapper's built-in throttling and cache aggressively to `data/raw/`.
- **Vintage.** NBA definitions change (e.g., how "assist" is scored). If you're comparing eras, note it.
- **Fitness.** Play-by-play is huge but noisy. Box scores are compact and usually enough for v1.
- **License / ToS.** The NBA hasn't published a formal API license — stay conservative: don't republish full raw dumps, don't build anything commercial off this repo.

Choosing and vetting a source is a **judgment call** — surface it to a PM rather than deciding a major data direction alone.

## Local layout convention

```
data/
├── raw/          # exactly as fetched from the API — never edit by hand
├── interim/      # cleaned + joined game logs, per-season parquets
└── processed/    # feature tables and model-ready splits
```

Because `data/` isn't in git, the **pipeline that fetches and builds these folders** is what must be committed and reproducible — not the data itself.
