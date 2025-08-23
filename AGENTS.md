# Repository Guidelines

## Project Structure & Modules
- `daily/scripts/`: Python utilities for ingestion, classification, and daily dashboard generation.
- `weekly/scripts/`: Weekly dashboard generator and helpers.
- `daily/dashboard/` and `weekly/dashboard/`: Jinja templates and `output/` HTML.
- `data/ingest/`: Place CSV inputs (`Complete_List_Raw.csv`, `UnreadCount.csv`). `data/backup/`: auto‑created backups.
- `database/`: Unified JSON DB (`email_database.json`).
- `config/sla_config.json`: Business hours, thresholds, targets.
- `documentation/` and `agents/`: Architecture and planning notes.

## Build, Test, and Development
- Install deps: `pip install -r requirements.txt`
- Update DB (Linux/macOS): `./update_database.sh`
- Update DB (Windows): `update_database.bat`
- Generate daily dashboard: `python3 daily/scripts/generate_dashboard.py`
  - List dates: `--list-dates`; Validate only: `--validate-only`; Specific date: `--date YYYY-MM-DD`
- Generate weekly dashboard: `python3 weekly/scripts/generate_weekly_dashboard.py --last-7-days`
  - Alternatives: `--week 2025-W34` or `--date-range 2025-08-17:2025-08-23`
- Outputs: `daily/dashboard/output/email_dashboard_<YYYY-MM-DD>.html` and alias `latest.html`; weekly analogs under `weekly/dashboard/output/`.

## Coding Style & Naming
- Python, PEP 8, 4‑space indentation, descriptive names.
- Functions/variables: `snake_case`; modules/files: `lowercase_with_underscores.py`.
- Prefer type hints where practical and docstrings for scripts/classes.
- Keep scripts CLI‑friendly via `argparse`; avoid hard‑coded absolute paths (use `Path`).

## Testing Guidelines
- No formal test suite yet. Use script validation modes:
  - Daily: `python3 daily/scripts/generate_dashboard.py --validate-only`
  - Weekly: `python3 weekly/scripts/generate_weekly_dashboard.py --validate-only`
- Sanity check JSON integrity and HTML outputs opening from `output/`.

## Commit & PR Guidelines
- Commit style: Conventional Commits observed in history (e.g., `feat(dashboard): ...`, `refactor(...): ...`, `chore: ...`).
- PRs should include: purpose, linked issue (if any), before/after screenshots of dashboards, and brief test/validation notes.
- Limit diffs to focused changes; update docs/templates when touching KPIs.

## Security & Configuration Tips
- Do not commit raw CSVs with sensitive data; keep in `data/ingest/` (gitignored).
- Review `config/sla_config.json` before runs; ensure thresholds/hours align with environment.
- Backups are timestamped in `data/backup/`; verify space usage periodically.

