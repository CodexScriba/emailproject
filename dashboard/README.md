# Email Dashboard Generator

Automated dashboard generation for email metrics and SLA tracking.

## Quick Start

Generate the latest dashboard:
```bash
python3 dashboard/scripts/generate_dashboard.py
```

The dashboard will be automatically generated using the most recent day with complete data from `email_database.json` and saved to `dashboard/output/email_dashboard_YYYY-MM-DD.html`.

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

## Configuration

Business hours are configurable in `config/sla_config.json` under:

- `sla_thresholds.business_hours.start_hour` (default: 7)
- `sla_thresholds.business_hours.end_hour` (default: 21)

These values drive the x-axis labels, business-hours filtering, and 2-hour aggregation windows.

## Data Source

The script reads from the unified JSON database (`email_database.json`) created by the email classification system.