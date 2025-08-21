#!/usr/bin/env python3
"""
Weekly Email Dashboard Generator

Renders the weekly KPI cards template using Jinja2 and aggregated metrics
from the unified JSON database, producing a static HTML file.
"""

import json
import os
import sys
from datetime import datetime, timedelta, date
import argparse
from pathlib import Path
from statistics import mean
from typing import Dict, Any, List, Optional, Tuple
import re

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except Exception:  # pragma: no cover
    print("Error: Jinja2 is required. Install with: pip install jinja2")
    sys.exit(1)

def load_sla_config() -> Dict[str, Any]:
    """Load SLA configuration from config/sla_config.json"""
    config_path = Path(__file__).parent.parent.parent / "config" / "sla_config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: SLA config file not found at {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in SLA config: {e}")
        sys.exit(1)

def get_week_dates(week_str: str) -> Tuple[date, date]:
    """Parse ISO week string (e.g., '2025-W34') and return start/end dates"""
    try:
        year, week = week_str.split('-W')
        year = int(year)
        week = int(week)
        
        # Get first day of the year
        jan1 = datetime(year, 1, 1)
        # Find the first Monday of the year
        first_monday = jan1 + timedelta(days=(7 - jan1.weekday()) % 7)
        if jan1.weekday() > 3:  # If Jan 1 is Thu-Sun, first week starts next Monday
            first_monday += timedelta(days=7)
        
        # Calculate start of requested week
        week_start = first_monday + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=6)
        
        return week_start.date(), week_end.date()
    except (ValueError, IndexError):
        print(f"Error: Invalid week format '{week_str}'. Use format: YYYY-Www (e.g., 2025-W34)")
        sys.exit(1)

def get_last_7_days() -> Tuple[date, date]:
    """Get date range for last 7 days"""
    # End yesterday to align with reporting standards (ending yesterday)
    end_date = datetime.now().date() - timedelta(days=1)
    start_date = end_date - timedelta(days=6)
    return start_date, end_date

def format_week_title(start_date: date, end_date: date, is_last_7_days: bool = False) -> str:
    """Format week title for display"""
    if is_last_7_days:
        return f"Last 7 Days — {start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}"
    else:
        # Calculate ISO week number
        _, week, _ = start_date.isocalendar()
        return f"Week {week} — {start_date.strftime('%b %d, %Y')} – {end_date.strftime('%b %d, %Y')}"


def business_hours_label_from_config(config: Dict[str, Any]) -> str:
    sla = config.get('sla_thresholds', {})
    bh = sla.get('business_hours', {})
    start_hour = int(bh.get('start_hour', 9))
    end_hour = int(bh.get('end_hour', 17))
    business_days = bh.get('business_days', [0, 1, 2, 3, 4])
    days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    # Format like: 09:00–17:00 Mon–Fri (or individual days if custom)
    def hhmm(h: int) -> str:
        return f"{h:02d}:00"
    if business_days == [0, 1, 2, 3, 4]:
        days_label = 'Mon–Fri'
    elif business_days == [0, 1, 2, 3, 4, 5, 6]:
        days_label = 'Mon–Sun'
    else:
        days_label = '–'.join([days_map.get(min(business_days, default=0), 'Mon'), days_map.get(max(business_days, default=4), 'Fri')]) if business_days else 'Mon–Fri'
    return f"{hhmm(start_hour)} to {hhmm(end_hour)} {days_label}"


def load_database() -> Dict[str, Any]:
    db_path = Path(__file__).parent.parent.parent / "database" / "email_database.json"
    try:
        with open(db_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in database: {e}")
        sys.exit(1)


def daterange(start_date: date, end_date: date) -> List[date]:
    days: List[date] = []
    current = start_date
    while current <= end_date:
        days.append(current)
        current = current + timedelta(days=1)
    return days


def compute_weekly_kpis(
    db: Dict[str, Any],
    config: Dict[str, Any],
    start_date: date,
    end_date: date,
    specific_dates: Optional[List[date]] = None,
    daily_output_dir: Optional[Path] = None,
    fallback_daily_output: bool = True,
) -> Dict[str, Any]:
    days_data: Dict[str, Any] = db.get('days', {})

    sla_thresholds = config.get('sla_thresholds', {})
    unread_threshold = int(sla_thresholds.get('unread_email_threshold', 30))
    business_hours = sla_thresholds.get('business_hours', {})
    start_hour_b = int(business_hours.get('start_hour', 9))
    end_hour_b = int(business_hours.get('end_hour', 17))
    business_days = business_hours.get('business_days', [0, 1, 2, 3, 4])

    kpi_targets = config.get('kpi_targets', {})
    response_time_target = float(kpi_targets.get('response_time_target_minutes', 60))
    sla_compliance_target = float(kpi_targets.get('sla_compliance_target_percent', 85))

    def include_day_for_averages(day_obj: Dict[str, Any]) -> bool:
        if day_obj is None:
            return False
        if day_obj.get('has_email_data') is False:
            return False
        if day_obj.get('has_sla_data') is False:
            return False
        return True

    # Totals and accumulators
    total_emails: int = 0
    total_emails_weight_for_sla: float = 0.0
    weighted_sla_sum: float = 0.0

    daily_avg_unread_values: List[float] = []
    daily_response_time_values: List[float] = []

    # Hourly accumulators for weighted response time across business hours
    weighted_rt_numerator: float = 0.0
    weighted_rt_denominator: float = 0.0

    used_days_count: int = 0

    date_iterable: List[date] = specific_dates if specific_dates is not None else daterange(start_date, end_date)

    for d in date_iterable:
        key = d.strftime('%Y-%m-%d')
        day_obj: Optional[Dict[str, Any]] = days_data.get(key)

        # If DB missing or flagged not usable, attempt fallback from daily HTML output
        used_fallback = False
        if (not day_obj or day_obj.get('has_email_data') is False or day_obj.get('has_sla_data') is False) and fallback_daily_output and daily_output_dir is not None:
            html_path = daily_output_dir / f"email_dashboard_{key}.html"
            if html_path.exists():
                # Parse metrics from HTML
                try:
                    with open(html_path, 'r') as hf:
                        html = hf.read()
                    # Extract KPI card values by pairing value with label inside each card
                    # Pattern finds each KPI card block's value and label
                    pairs = re.findall(r'<div class="card kpi-card[\s\S]*?<div class="kpi-value">([\s\S]*?)</div>[\s\S]*?<div class="kpi-label">([^<]+)</div>', html, flags=re.IGNORECASE)
                    metrics: Dict[str, str] = {}
                    # Helper to strip tags
                    def strip_tags(s: str) -> str:
                        return re.sub(r'<[^>]*>', '', s)
                    for raw_value, label in pairs:
                        value = strip_tags(raw_value).strip()
                        metrics[label.strip()] = value

                    if metrics:
                        # Build a minimal day_obj equivalent
                        ds: Dict[str, Any] = {}
                        te = metrics.get('Total Emails')
                        if te is not None:
                            try:
                                ds['total_emails'] = int(float(te.replace(',', '').strip()))
                            except Exception:
                                pass
                        au = metrics.get('Avg Unread Count')
                        if au is not None:
                            try:
                                ds['avg_unread_count'] = float(au.replace(',', '').strip())
                            except Exception:
                                pass
                        art = metrics.get('Avg Response Time')
                        if art is not None:
                            try:
                                ds['avg_response_time_minutes'] = float(art.replace('min', '').replace(',', '').strip())
                            except Exception:
                                pass
                        sla = metrics.get('SLA Compliance')
                        if sla is not None:
                            try:
                                ds['sla_compliance_rate'] = float(sla.replace('%', '').replace(',', '').strip())
                            except Exception:
                                pass

                        # Create fallback day object
                        day_obj = {
                            'has_email_data': True,
                            'has_sla_data': True,
                            'daily_summary': ds,
                            'hourly_data': [],
                        }
                        used_fallback = True
                except Exception:
                    pass

        if not day_obj:
            continue

        daily_summary: Dict[str, Any] = day_obj.get('daily_summary', {}) or {}
        hourly_data: List[Dict[str, Any]] = day_obj.get('hourly_data', []) or []

        # Total emails (sum daily total; fallback to hourly sum)
        day_total = daily_summary.get('total_emails')
        if isinstance(day_total, (int, float)):
            total_emails += int(day_total)
        else:
            # Fallback from hourly
            hourly_total = 0
            for h in hourly_data:
                v = h.get('emails_received') or h.get('emails') or 0
                if isinstance(v, (int, float)):
                    hourly_total += int(v)
            total_emails += hourly_total

        # SLA compliance weighting (by daily total if available)
        sla_rate = daily_summary.get('sla_compliance_rate')
        if isinstance(sla_rate, (int, float)):
            weight = int(daily_summary.get('total_emails') or 0)
            if weight and weight > 0:
                weighted_sla_sum += float(sla_rate) * weight
                total_emails_weight_for_sla += weight

        # Collect daily averages for fallbacks
        avg_unread = daily_summary.get('avg_unread_count')
        if isinstance(avg_unread, (int, float)):
            daily_avg_unread_values.append(float(avg_unread))

        avg_rt_daily = daily_summary.get('avg_response_time_minutes')
        if isinstance(avg_rt_daily, (int, float)):
            daily_response_time_values.append(float(avg_rt_daily))

        # Hourly response time weighted by emails_replied within business hours and business days
        weekday_idx = d.weekday()  # 0=Mon
        is_business_day = weekday_idx in business_days
        if is_business_day:
            for h in hourly_data:
                hour_val = h.get('hour')
                try:
                    hour_int = int(hour_val)
                except Exception:
                    continue
                if hour_int < start_hour_b or hour_int >= end_hour_b:
                    continue
                replies = h.get('emails_replied') or h.get('replies')
                rt = h.get('avg_response_time_minutes') or h.get('response_time_minutes')
                if isinstance(replies, (int, float)) and replies > 0 and isinstance(rt, (int, float)):
                    weighted_rt_numerator += float(rt) * float(replies)
                    weighted_rt_denominator += float(replies)

        # Count day if it qualifies for averages (per spec exclusions)
        if include_day_for_averages(day_obj):
            used_days_count += 1

    # Compute KPIs
    avg_emails_per_day: Optional[float] = None
    if used_days_count > 0:
        avg_emails_per_day = round(total_emails / used_days_count, 1)

    # Avg unread: prefer daily averages; fallback to hourly across business hours
    avg_unread_count: Optional[float] = None
    if daily_avg_unread_values:
        avg_unread_count = round(mean(daily_avg_unread_values), 1)

    # Average response time: weighted by emails_replied across business hours
    avg_response_time: Optional[float] = None
    if weighted_rt_denominator > 0:
        avg_response_time = round(weighted_rt_numerator / weighted_rt_denominator, 1)
    elif daily_response_time_values:
        avg_response_time = round(mean(daily_response_time_values), 1)

    # SLA compliance: weighted by daily total_emails; fallback to unweighted mean
    sla_compliance: Optional[float] = None
    if total_emails_weight_for_sla > 0:
        sla_compliance = round(weighted_sla_sum / total_emails_weight_for_sla, 1)
    else:
        # Fallback: try unweighted mean from available daily summaries
        # Note: re-iterate to collect available rates if needed
        daily_rates: List[float] = []
        for d in date_iterable:
            key = d.strftime('%Y-%m-%d')
            day_obj = days_data.get(key) or {}
            rate = (day_obj.get('daily_summary') or {}).get('sla_compliance_rate')
            if isinstance(rate, (int, float)):
                daily_rates.append(float(rate))
        if daily_rates:
            sla_compliance = round(mean(daily_rates), 1)

    has_partial_week = used_days_count < 3

    context: Dict[str, Any] = {
        'total_emails': int(total_emails),
        'avg_emails_per_day': avg_emails_per_day if avg_emails_per_day is not None else None,
        'avg_unread_count': avg_unread_count,
        'unread_threshold': unread_threshold,
        'avg_response_time': avg_response_time,
        'response_time_target': response_time_target,
        'sla_compliance': sla_compliance,
        'sla_compliance_target': sla_compliance_target,
        'data_days_count': used_days_count,
        'has_partial_week': has_partial_week,
    }

    return context


def select_last_n_valid_dates(
    db: Dict[str, Any],
    config: Dict[str, Any],
    n: int,
    end_date: date,
    daily_output_dir: Optional[Path] = None,
) -> List[date]:
    """Select the last N qualifying dates scanning backwards from end_date.

    A qualifying date is one where:
      - In DB: day exists and neither has_email_data nor has_sla_data is False
        (i.e., considered usable), OR
      - A daily HTML output file exists at daily_output_dir/email_dashboard_YYYY-MM-DD.html
    """
    days_data: Dict[str, Any] = db.get('days', {})

    def qualifies(d: date) -> bool:
        key = d.strftime('%Y-%m-%d')
        day_obj = days_data.get(key)
        # DB qualifies
        db_ok = False
        if day_obj:
            if day_obj.get('has_email_data') is not False and day_obj.get('has_sla_data') is not False:
                db_ok = True
        # Daily HTML fallback qualifies
        html_ok = False
        if daily_output_dir is not None:
            html_ok = (daily_output_dir / f"email_dashboard_{key}.html").exists()
        return db_ok or html_ok

    selected: List[date] = []
    cursor = end_date
    # Scan back up to 730 days to find N valid days
    for _ in range(730):
        if qualifies(cursor):
            selected.append(cursor)
            if len(selected) >= n:
                break
        cursor = cursor - timedelta(days=1)

    selected.sort()
    return selected

def render_dashboard_html(context: Dict[str, Any]) -> str:
    """Render weekly KPI template via Jinja2 with provided context."""
    templates_dir = Path(__file__).parent.parent / "dashboard" / "templates"
    template_name = "weekly_kpi_cards.html"

    if not templates_dir.exists():
        print(f"Error: Templates directory not found at {templates_dir}")
        sys.exit(1)

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(['html', 'xml'])
    )

    try:
        template = env.get_template(template_name)
    except Exception as e:
        print(f"Error: Could not load template '{template_name}' from {templates_dir}: {e}")
        sys.exit(1)

    return template.render(**context)

def save_dashboard(html_content: str, week_identifier: str, is_last_7_days: bool = False) -> Path:
    """Save dashboard HTML to output directory"""
    output_dir = Path(__file__).parent.parent / "dashboard" / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Generate filename
    if is_last_7_days:
        filename = f"weekly_dashboard_last7days_{datetime.now().strftime('%Y%m%d')}.html"
    else:
        filename = f"weekly_dashboard_{week_identifier}.html"
    
    output_path = output_dir / filename
    latest_path = output_dir / "latest.html"
    
    # Save main file
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    # Create/update latest.html
    with open(latest_path, 'w') as f:
        f.write(html_content)
    
    print(f"Dashboard saved to: {output_path}")
    print(f"Latest dashboard: {latest_path}")
    
    return output_path

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate Weekly Email Dashboard')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--week', help='ISO week format (e.g., 2025-W34)')
    group.add_argument('--last-7-days', action='store_true', help='Generate for last 7 days')
    parser.add_argument('--validate-only', action='store_true', help='Compute KPIs and print, do not write files')
    parser.add_argument('--fill-missing-days', action='store_true', help='If enabled, selects the last 7 valid days ending at end_date when some days are missing')
    
    args = parser.parse_args()
    
    # Load configuration
    sla_config = load_sla_config()
    business_hours_label = business_hours_label_from_config(sla_config)
    
    # Determine date range
    if args.last_7_days:
        start_date, end_date = get_last_7_days()
        week_identifier = f"last7days_{datetime.now().strftime('%Y%m%d')}"
        is_last_7_days = True
    else:
        start_date, end_date = get_week_dates(args.week)
        week_identifier = args.week
        is_last_7_days = False
    
    # Format week title
    week_title = format_week_title(start_date, end_date, is_last_7_days)
    generated_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Load DB
    db = load_database()

    # Compute KPIs (optionally filling missing days by selecting last N valid)
    specific_dates = None
    daily_output_dir = Path(__file__).parent.parent.parent / 'daily' / 'dashboard' / 'output'
    if args.fill_missing_days:
        specific_dates = select_last_n_valid_dates(db, sla_config, 7, end_date, daily_output_dir=daily_output_dir)

    kpis = compute_weekly_kpis(
        db,
        sla_config,
        start_date,
        end_date,
        specific_dates=specific_dates,
        daily_output_dir=daily_output_dir,
        fallback_daily_output=True,
    )

    # Compose context
    context: Dict[str, Any] = {
        **kpis,
        'week_title': week_title,
        'business_hours_label': business_hours_label,
        'generated_timestamp': generated_timestamp,
    }

    if args.validate_only:
        # Print KPIs and exit non-zero if required fields missing
        print(json.dumps(context, indent=2, default=str))
        required_keys = ['total_emails', 'avg_emails_per_day', 'avg_unread_count', 'avg_response_time', 'sla_compliance']
        missing = [k for k in required_keys if context.get(k) is None]
        if missing:
            print(f"Missing required KPI(s): {', '.join(missing)}")
            sys.exit(2)
        return
    
    # Render dashboard HTML
    html_content = render_dashboard_html(context)
    
    # Save dashboard
    output_path = save_dashboard(html_content, week_identifier, is_last_7_days)
    
    print(f"Weekly dashboard generated successfully for {week_identifier}")

if __name__ == "__main__":
    main()
