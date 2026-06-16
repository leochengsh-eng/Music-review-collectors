# Album Review Weekly Digest

A Python 3.11+ tool that collects album reviews from multiple music publications and aggregators, normalizes available scores to a 10-point scale, groups recommendations by genre, renders a standalone weekly HTML digest, and emails it to `leochengsh@gmail.com`.

## Source strategy

The project follows **coverage first, then scoring**:

1. **Core discovery sources**: Pitchfork, The Guardian, AllMusic, Sputnikmusic, Resident Advisor, and The Line of Best Fit.
2. **Score/metadata supplementation**: the core sources plus Metacritic, Album of the Year, and AnyDecentMusic.
3. **Aggregator reverse lookup**: Album of the Year, Metacritic, and AnyDecentMusic can produce `aggregator_find` items when a source scan misses an album.
4. **Optional long-tail sources** can be added later if they expose RSS feeds, stable listing pages, or accessible metadata.

Pitchfork remains a discovery source even when a score is unavailable; such items are preserved with `score_status = no_score`.

## Configuration

Edit `sources.yaml` to enable, disable, or add sources. Runtime settings can be supplied in `.env` or environment variables; copy `.env.example` as a starting point.

Required SMTP secrets for GitHub Actions:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`

`EMAIL_TO` defaults to `leochengsh@gmail.com`.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m src.main --mode weekly
```

Other modes:

```bash
python -m src.main --mode weekly --lookback-days 14
python -m src.main --mode backfill --start-date 2026-04-01 --end-date 2026-04-26
python -m src.main --mode report-only --start-date 2026-06-09 --end-date 2026-06-15
python -m src.main --mode test-email
```

## Schedule and manual reruns

`.github/workflows/weekly-digest.yml` runs every Tuesday at `02:00 UTC`, which is Tuesday `10:00 UTC+8`, and keeps `workflow_dispatch` enabled for manual reruns from GitHub Actions.

## Outputs

Each run updates SQLite and writes artifacts:

- `data/album_reviews.sqlite`
- `outputs/html/album-review-digest-YYYY-MM-DD_to_YYYY-MM-DD.html`
- `outputs/csv/reviews-YYYY-MM-DD_to_YYYY-MM-DD.csv`
- `outputs/csv/recommended-YYYY-MM-DD_to_YYYY-MM-DD.csv`
- `outputs/csv/manual-check-YYYY-MM-DD_to_YYYY-MM-DD.csv`
- `outputs/json/run-summary-YYYY-MM-DD_to_YYYY-MM-DD.json`
- `logs/run-YYYY-MM-DD.log`

## Manual Check items

Inspect `outputs/csv/manual-check-*.csv`, the `Manual Check` HTML section, or the SQLite `reviews` table. Parser failures, missing release types, uncertain duplicates, blocked pages, paywalls, and missing critical metadata should be preserved instead of silently skipped.

## Adding a parser

1. Add or update a source in `sources.yaml`.
2. Add a module under `src/parsers/` or extend `src/parsers/base.py`.
3. Keep failures non-fatal and create Manual Check records when parsing is uncertain.
4. Preserve raw scores and links; never fabricate scores, genres, recommended tracks, or review opinions.
5. Add tests for parser failure handling and score conversion.

## Known limitations

- Some websites may block scraping.
- Some sources may not expose scores.
- The tool does not bypass paywalls, login restrictions, robots.txt restrictions, anti-bot systems, or technical access controls.
- Aggregator data may update with delays.
- AI summaries must only use available public information.
- 100% coverage is not guaranteed, but the layered strategy is designed to reduce omissions.
