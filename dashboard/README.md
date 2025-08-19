# Email Dashboard Generator

Automated dashboard generation for email metrics and SLA tracking.

## Quick Start

Generate the latest dashboard:
```bash
python3 dashboard/scripts/generate_dashboard.py
```

The dashboard will be automatically generated using the most recent day with complete data from `email_database.json` and saved to `dashboard/output/email_dashboard_YYYY-MM-DD.html`.

Generate for a specific date:
```bash
python3 dashboard/scripts/generate_dashboard.py --date 2025-08-15
```

List available dates and completeness:
```bash
python3 dashboard/scripts/generate_dashboard.py --list-dates
```

Validate data for a specific date (prints KPIs; exits non-zero if required fields are missing):
```bash
python3 dashboard/scripts/generate_dashboard.py --date 2025-08-15 --validate-only
```

## Features

- **Dynamic KPI Cards**: Total emails, average response time, SLA compliance, and average unread count
- **Interactive Line Charts**: Hourly email distribution and unread count trends (default 7 AM – 9 PM; configurable)
- **SLA Indicators**: Visual checkmarks/X marks showing hourly SLA compliance
- **Modern Design**: Professional styling with hover effects and gradients
- **Responsive Layout**: Works on desktop and mobile devices

## Output

The generated dashboard includes:
- Automatically calculated SVG line chart coordinates
- Dynamic scaling based on actual data values
- Real-time SLA compliance indicators
- Formatted business hours visualization (default 7 AM – 9 PM; configurable)

After generation, a convenient alias is also written:
- `dashboard/output/latest.html` points to the most recently generated dashboard content.

## Configuration

Business hours are configurable in `config/sla_config.json` under:

- `sla_thresholds.business_hours.start_hour` (default: 7)
- `sla_thresholds.business_hours.end_hour` (default: 21)
- `sla_thresholds.business_hours.business_days` (default: [0,1,2,3,4,5,6] where 0=Mon, 6=Sun)

These values drive the x-axis labels, business-hours filtering, and 2-hour aggregation windows.

## Troubleshooting

- If Avg Unread Count shows 0 or SLA Compliance shows N/A, run validation for the target date:
  ```bash
  python3 dashboard/scripts/generate_dashboard.py --date YYYY-MM-DD --validate-only
  ```
- Ensure `daily_summary.avg_unread_count` and `daily_summary.sla_compliance_rate` exist for that date in `email_database.json`.

## Data Source

The script reads from the unified JSON database (`email_database.json`) created by the email classification system.