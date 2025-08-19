# Email Dashboard Generation Backlog — Step-by-Step

This checklist explains how to generate and validate daily dashboards using the unified JSON.

- Source script: `dashboard/scripts/generate_dashboard.py`
- Data: `email_database.json`
- SLA config: `config/sla_config.json` (business hours, thresholds)
- Template: `dashboard/templates/kpi_cards.html`
- Output: `dashboard/output/email_dashboard_YYYY-MM-DD.html`

## 1) Prerequisites
- Python deps installed: `pip install -r requirements.txt`
- `email_database.json` contains the target `YYYY-MM-DD` under `days`.
- Business hours configured in `config/sla_config.json` under `sla_thresholds.business_hours.start_hour` and `end_hour` (defaults 7–21).

## 2) Generate a dashboard for a specific day
- Command:
  ```bash
  python dashboard/scripts/generate_dashboard.py --date YYYY-MM-DD
  ```
- If `--date` is omitted, the script uses the latest complete day (has both email and SLA data).

Examples:
```bash
python dashboard/scripts/generate_dashboard.py --date 2025-08-13
python dashboard/scripts/generate_dashboard.py --date 2025-08-14
python dashboard/scripts/generate_dashboard.py --date 2025-08-15
python dashboard/scripts/generate_dashboard.py --date 2025-08-16
```

## 3) Verify output file
- Confirm file exists: `dashboard/output/email_dashboard_YYYY-MM-DD.html`.
- Open in a browser and review the sections below.

## 4) Quick validation checklist
- Header
  - Date matches target day; `Generated at` shows local time.
- KPI cards (top row)
  - Total Emails = `daily_summary.total_emails` (fallback: sum of hourly `emails_received`).
  - Avg Unread Count = `daily_summary.avg_unread_count`.
  - Avg Response Time = business-hours weighted average by `emails_replied` (fallback: `daily_summary.avg_response_time_minutes`).
  - SLA Compliance = `daily_summary.sla_compliance_rate` and colored against target.
- Hourly Email Distribution chart
  - X-axis starts/ends at configured business hours from SLA config.
  - Smooth line + area fill for Emails and Unread.
  - Orange dashed SLA line at `sla_thresholds.unread_email_threshold`.
- Response Time Analytics
  - By Hour (Early Morning, Morning, Afternoon, Evening) averages and colors make sense (<=60 green, 60–120 yellow, >120 red).
  - Distribution categories (Very Fast … Critical) totals and percentages reflect composition of replied emails.
  - Percentiles P25/P50/P75/P90/P95 bars present; quartile counts sum to total responses considered.
- 2-hour Metrics Table
  - Blocks match configured business hours (e.g., 7–9 AM … 7–9 PM by default).
  - `SLA` badge is true only when all hours in block met SLA; empty/neutral when no data.
  - Avg Response/Mean Time = weighted by `emails_replied`; Median calculated from expanded weights.
  - Microbar width scales relative to max emails across blocks.

## 5) Troubleshooting
- "Date not found": ensure `YYYY-MM-DD` exists under `days` in `email_database.json`.
- Unexpected KPI values: inspect `daily_summary` vs hourly entries for that date.
- X-axis off: verify `business_hours` in `config/sla_config.json` (start/end are 0–23).
- Thresholds/colors off: review `kpi_targets` and `sla_thresholds` in SLA config.
- Re-generate after config changes by re-running the command; output files will be overwritten for the same date.

## 6) Notes
- Output filenames always include the selected `date_str`.
- Business hours drive x-axis labels, percentile scope, and 2-hour aggregation.
- Keep `requirements.txt` in sync if adding dependencies.
