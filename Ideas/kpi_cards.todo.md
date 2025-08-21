# KPI Cards — Weekly Dashboard Todo

## User Stories
- As an operations lead, I want a weekly summary of email performance so I can quickly see trends and SLA adherence without drilling into daily views.
- As a support manager, I want threshold-colored KPI cards so I can immediately spot issues against targets.
- As a data analyst, I want accurate Monday–Sunday aggregations so weekly metrics align with reporting standards (ISO weeks or last 7 days).
- As a developer, I want the weekly dashboard to reuse the daily styles so the UI remains consistent and low-maintenance.

## Phase 1: Foundation
- [ ] Create weekly template file `weekly/dashboard/templates/weekly_kpi_cards.html` cloned from `daily/dashboard/templates/kpi_cards.html` with header and 4 KPI cards only (no charts yet).
- [ ] Add header subtitle to show ISO week and date range: "Week {ISO} — {Mon Date} – {Sun Date}".
- [ ] Set up weekly generator script using Jinja2 like the daily generator: implement `weekly/scripts/generate_weekly_dashboard.py` to load JSON and config and render the weekly template.
- [ ] Support CLI args: `--week 2025-W34` and `--last-7-days`; write output to `weekly/dashboard/output/` with `weekly_dashboard_{week}.html` or `weekly_dashboard_last7days_YYYYMMDD.html` and `latest.html` alias.

## Phase 2: Core Functionality
- [ ] Implement week selection utilities
  - [ ] Parse ISO week to Monday–Sunday dates.
  - [ ] Compute last-7-days range ending yesterday.
- [ ] Implement data aggregation from `database/email_database.json` across selected range
  - [ ] Total Emails: sum `daily_summary.total_emails`; fallback to per-day hourly sum if missing.
  - [ ] Avg per day: `total_emails / number_of_days_with_data` (1 decimal).
  - [ ] Avg Unread Count: mean of daily `daily_summary.avg_unread_count` (1 decimal); fallback to business-hour means across week ignoring nulls.
  - [ ] Avg Response Time (business hours): weighted average by `emails_replied` across all business-hour hourly entries; fallback to weekly mean of `daily_summary.avg_response_time_minutes`.
  - [ ] SLA Compliance (%): weighted average of daily `daily_summary.sla_compliance_rate` by that day's `total_emails`; fallback to unweighted mean if totals missing.
- [ ] Pull thresholds/targets from `config/sla_config.json`
  - [ ] `sla_thresholds.unread_email_threshold` (default 30)
  - [ ] `kpi_targets.response_time_target_minutes` (default 60)
  - [ ] `kpi_targets.sla_compliance_target_percent` (default 85)
- [ ] Compose template context keys (see Technical Specs) and render HTML.

## Phase 3: Enhanced Features & Polish
- [ ] Styling parity: ensure classes, layout, and color semantics match `kpi_cards.html`.
- [ ] Total Emails card shows total and a second line: "Avg: X per day".
- [ ] Card color rules:
  - [ ] Avg Unread Count: `success` if `<= unread_threshold`, else `danger`.
  - [ ] Avg Response Time: `success` if `<= target`, `warning` if `<= 2x target`, else `danger`.
  - [ ] SLA Compliance: `success` if `>= target`, else `danger`.
- [ ] Partial data handling: if fewer than 3 days with data, show a small warning badge: "Partial week — metrics computed from N day(s)".
- [ ] Add generated timestamp and business-hours label to footer summary.

## Phase 4: Testing & Validation
- [ ] Add a `--validate-only` mode mirroring the daily script to compute/print weekly KPIs and exit non-zero if required fields are missing.
- [ ] Unit tests for aggregation helpers (date boundaries; exclusions; fallbacks; weighting): place in `weekly/tests/test_weekly_aggregation.py`.
- [ ] Cross-check a known week by summing daily dashboards to ensure equality within rounding rules.
- [ ] Manual visual QA: open the generated HTML and verify styles and thresholds reflect config changes.

## Technical Specifications
- Data sources
  - `database/email_database.json` unified DB structure with `days[YYYY-MM-DD]` containing `daily_summary` and `hourly_data`.
  - Exclude days where `has_email_data == false` or `has_sla_data == false` from averages. If none remain, display N/A per card.
- Business hours
  - Read from `config/sla_config.json` → `sla_thresholds.business_hours` (`start_hour`, `end_hour`, `business_days`). Use these to select business-hour entries for response-time calculations.
- Aggregation rules (weekly)
  - Total Emails: sum of daily totals; fallback from hourly per day if daily total missing.
  - Avg per day: as defined; use `number_of_days_with_data` in denominator.
  - Avg Unread: mean of daily averages; alternative fallback: mean across business-hour `unread_count` values for the week (ignore nulls).
  - Avg Response Time: weighted by `emails_replied`; if no replies present across week, fallback to mean of `daily_summary.avg_response_time_minutes` where present.
  - SLA Compliance: weighted by per-day `total_emails`; fallback to unweighted mean.
- Rounding & display
  - Integers for totals; 1 decimal for averages and percentages (e.g., `87.4%`).
  - Response time shows `min` suffix.
- Template contract (weekly)
  - Header: `week_title` (e.g., "Week 34 — Aug 19, 2024 – Aug 25, 2024").
  - KPI variables:
    - `total_emails`, `avg_emails_per_day`
    - `avg_unread_count`, `unread_threshold`
    - `avg_response_time`, `response_time_target`
    - `sla_compliance`, `sla_compliance_target`
    - `data_days_count`, `has_partial_week`
  - Card state classes computed in Jinja using the above targets.
- File paths
  - Template: `weekly/dashboard/templates/weekly_kpi_cards.html`
  - Script: `weekly/scripts/generate_weekly_dashboard.py`
  - Output: `weekly/dashboard/output/weekly_dashboard_{W}.html`, plus `latest.html`
- Acceptance criteria (must meet all)
  - Title includes ISO week number and Monday–Sunday date range.
  - Total Emails card displays total and average per day.
  - All 4 KPI cards render with correct thresholds/targets and color semantics.
  - Excludes days without data; shows partial-week badge when < 3 days.
  - No JavaScript requirements in final output (HTML/CSS only).

## Implementation Notes
- Mirror daily generator patterns (`daily/scripts/generate_dashboard.py`) for config loading, context building, and Jinja rendering.
- Prefer small pure functions for each aggregation; add docstrings and unit tests.
- Reuse daily CSS classes to avoid duplicating styles; keep markup minimal and accessible.

## CLI Examples
- `python weekly/scripts/generate_weekly_dashboard.py --week 2025-W34`
- `python weekly/scripts/generate_weekly_dashboard.py --last-7-days`
