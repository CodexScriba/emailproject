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
from statistics import mean, median
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


def build_week_data(
    db: Dict[str, Any],
    config: Dict[str, Any],
    start_date: date,
    end_date: date,
    specific_dates: Optional[List[date]] = None,
) -> Dict[str, Dict[str, int]]:
    """Construct heatmap-ready week_data mapping dates -> {"HH": count}.

    - Uses business hours from config; includes end hour inclusive for a 15-hour window (e.g., 07..21).
    - Falls back to 0 for missing hours or missing day/hourly data.
    - Accepts optional specific_dates to override the inclusive date range.
    """
    days_data: Dict[str, Any] = db.get('days', {}) or {}

    sla_thresholds = config.get('sla_thresholds', {}) or {}
    bh = sla_thresholds.get('business_hours', {}) or {}
    start_hour_cfg = int(bh.get('start_hour', 7))
    end_hour_cfg = int(bh.get('end_hour', 21))

    # Ensure inclusive end hour for heatmap (e.g., 07..21 -> 15 hours)
    hours_range: List[int] = list(range(start_hour_cfg, end_hour_cfg + 1))
    hours_labels: List[str] = [f"{h:02d}" for h in hours_range]

    result: Dict[str, Dict[str, int]] = {}

    date_iterable: List[date] = specific_dates if specific_dates is not None else daterange(start_date, end_date)
    for d in date_iterable:
        key = d.strftime('%Y-%m-%d')
        day_obj: Optional[Dict[str, Any]] = days_data.get(key)
        hourly_items: List[Dict[str, Any]] = []
        if day_obj and isinstance(day_obj.get('hourly_data'), list):
            hourly_items = list(day_obj.get('hourly_data') or [])

        # Build map for this day
        hour_to_count: Dict[str, int] = {hh: 0 for hh in hours_labels}
        for item in hourly_items:
            hour_val = item.get('hour')
            try:
                hour_int = int(hour_val)
            except Exception:
                continue
            if hour_int < hours_range[0] or hour_int > hours_range[-1]:
                continue
            emails_count = item.get('emails_received')
            if not isinstance(emails_count, (int, float)):
                emails_count = item.get('emails')
            if isinstance(emails_count, (int, float)):
                hour_to_count[f"{hour_int:02d}"] = int(emails_count)

        result[key] = hour_to_count

    return result

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
                rt = h.get('avg_response_time_minutes') or h.get('avg_response_time')
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


def compute_two_hour_metrics_week(
    db: Dict[str, Any],
    config: Dict[str, Any],
    start_date: date,
    end_date: date,
    specific_dates: Optional[List[date]] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """Aggregate weekly metrics into 2-hour blocks across included days.

    Output list per 2-hour block with keys:
      - label (e.g., "07:00–08:59")
      - start_hour (int)
      - emails (int) — weekly sum across days/hours in block
      - avg_unread (float | None) — mean of unread snapshots across hours/days
      - avg_response_time (float | None) — weighted avg by emails_replied, fallback to emails
      - median_response_time (float | None) — weighted median by emails_replied (fallback to emails)
    Returns (blocks, two_hour_max_emails_week)
    """
    days_data: Dict[str, Any] = db.get('days', {}) or {}

    # Business hours bounds
    sla_thresholds = config.get('sla_thresholds', {}) or {}
    bh = sla_thresholds.get('business_hours', {}) or {}
    start_hour_b = int(bh.get('start_hour', 7))
    end_hour_b = int(bh.get('end_hour', 21))

    # Helper: format block label like 07:00–08:59
    def format_block_label(h_start: int, h_end_exclusive: int) -> str:
        h_last = max(h_start, min(h_end_exclusive, 24) - 1)
        return f"{h_start:02d}:00–{h_last:02d}:59"

    # Prepare containers per 2-hour start
    blocks: List[Dict[str, Any]] = []

    # Build list of dates to include
    date_iterable: List[date] = specific_dates if specific_dates is not None else daterange(start_date, end_date)

    # Pre-collect hourly data per included date
    hourly_by_date: Dict[str, List[Dict[str, Any]]] = {}
    for d in date_iterable:
        key = d.strftime('%Y-%m-%d')
        day_obj: Optional[Dict[str, Any]] = days_data.get(key) or {}
        hourly_by_date[key] = list(day_obj.get('hourly_data') or [])

    # Iterate 2-hour blocks within business hours (end exclusive)
    # Example: 07..21 -> starts at 7,9,11,13,15,17,19
    for h_start in range(start_hour_b, end_hour_b, 2):
        h_end_exclusive = min(h_start + 2, end_hour_b)

        total_emails: int = 0
        unread_samples: List[float] = []
        rt_weighted_sum: float = 0.0
        rt_weight_total: float = 0.0
        rt_samples_for_median: List[float] = []

        for key, hourly_items in hourly_by_date.items():
            for item in hourly_items:
                try:
                    hour_int = int(item.get('hour'))
                except Exception:
                    continue
                # include hour if within current block and business hours
                if hour_int < h_start or hour_int >= h_end_exclusive:
                    continue

                emails_received = item.get('emails_received')
                if not isinstance(emails_received, (int, float)):
                    emails_received = item.get('emails')
                emails_val = int(emails_received) if isinstance(emails_received, (int, float)) else 0
                total_emails += emails_val

                unread_val = item.get('unread_count')
                if isinstance(unread_val, (int, float)):
                    unread_samples.append(float(unread_val))

                # Response time and weights
                rt = (
                    item.get('avg_response_time')
                    if item.get('avg_response_time') is not None
                    else item.get('avg_response_time_minutes')
                )
                replies = item.get('emails_replied')
                if not isinstance(replies, (int, float)):
                    replies = item.get('replies')
                weight = float(replies) if isinstance(replies, (int, float)) and replies > 0 else None

                # Fallback to emails as weight when replies missing
                if weight is None and emails_val > 0:
                    weight = float(emails_val)

                if isinstance(rt, (int, float)) and weight is not None and weight > 0:
                    rt_weighted_sum += float(rt) * weight
                    rt_weight_total += weight
                    # Median approximation by expansion
                    # Cap expansion to avoid pathological blow-up
                    capped = int(min(200, max(1, round(weight))))
                    rt_samples_for_median.extend([float(rt)] * capped)

        avg_unread: Optional[float] = round(sum(unread_samples) / len(unread_samples), 1) if unread_samples else None
        avg_rt: Optional[float] = round(rt_weighted_sum / rt_weight_total, 1) if rt_weight_total > 0 else None
        median_rt: Optional[float] = round(median(rt_samples_for_median), 1) if rt_samples_for_median else None

        blocks.append({
            'label': format_block_label(h_start, h_end_exclusive),
            'start_hour': h_start,
            'emails': int(total_emails),
            'avg_unread': avg_unread,
            'avg_response_time': avg_rt,
            'median_response_time': median_rt,
        })

    two_hour_max_emails_week = max((b['emails'] for b in blocks), default=0)
    return blocks, int(two_hour_max_emails_week)

def compute_weekly_response_time_distribution(
    db: Dict[str, Any],
    config: Dict[str, Any],
    start_date: date,
    end_date: date,
    specific_dates: Optional[List[date]] = None,
) -> List[Dict[str, Any]]:
    """Aggregate response time distribution across the entire week.
    
    Computes weekly totals for each performance category:
    - Lightning Fast: Under 30 minutes
    - Fast Response: 30-60 minutes  
    - Moderate: 60-120 minutes
    - Slow: 120-180 minutes
    - Very Slow: 180-300 minutes
    - Critical: Over 300 minutes
    
    Returns list with count, percentage, and color for each category.
    """
    days_data: Dict[str, Any] = db.get('days', {}) or {}
    
    # Initialize distribution categories with same structure as daily dashboard
    distribution = {
        'Very Fast (< 30 min)': {'count': 0, 'color': 'success'},
        'Fast (30-60 min)': {'count': 0, 'color': 'success'},
        'Moderate (60-120 min)': {'count': 0, 'color': 'warning'},
        'Slow (120-180 min)': {'count': 0, 'color': 'warning'},
        'Very Slow (180-300 min)': {'count': 0, 'color': 'danger'},
        'Critical (> 300 min)': {'count': 0, 'color': 'danger'}
    }
    
    date_iterable: List[date] = specific_dates if specific_dates is not None else daterange(start_date, end_date)
    
    for d in date_iterable:
        key = d.strftime('%Y-%m-%d')
        day_obj: Optional[Dict[str, Any]] = days_data.get(key)
        
        if not day_obj:
            continue
            
        hourly_data: List[Dict[str, Any]] = day_obj.get('hourly_data', []) or []
        
        # Process each hour's response time data
        for hour_data in hourly_data:
            response_time = hour_data.get('avg_response_time', None)
            replied_count = hour_data.get('emails_replied', 0) or 0
            
            if response_time is not None and replied_count > 0:
                # Categorize based on response time thresholds
                if response_time < 30:
                    distribution['Very Fast (< 30 min)']['count'] += replied_count
                elif response_time < 60:
                    distribution['Fast (30-60 min)']['count'] += replied_count
                elif response_time < 120:
                    distribution['Moderate (60-120 min)']['count'] += replied_count
                elif response_time < 180:
                    distribution['Slow (120-180 min)']['count'] += replied_count
                elif response_time < 300:
                    distribution['Very Slow (180-300 min)']['count'] += replied_count
                else:
                    distribution['Critical (> 300 min)']['count'] += replied_count
    
    # Convert to list format with percentages
    result = []
    total_count = sum(d['count'] for d in distribution.values())
    
    for category, data in distribution.items():
        percentage = round((data['count'] / total_count) * 100) if total_count > 0 else 0
        result.append({
            'category': category,
            'count': data['count'],
            'percentage': percentage,
            'color': data['color']
        })
    
    return result

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

    # Build heatmap week_data
    week_data: Dict[str, Dict[str, int]] = build_week_data(
        db,
        sla_config,
        start_date,
        end_date,
        specific_dates=specific_dates,
    )

    # Compose context
    context: Dict[str, Any] = {
        **kpis,
        'week_title': week_title,
        'business_hours_label': business_hours_label,
        'generated_timestamp': generated_timestamp,
        'week_data': week_data,
    }

    # Compute weekly two-hour metrics table
    two_hour_metrics_week, two_hour_max_emails_week = compute_two_hour_metrics_week(
        db,
        sla_config,
        start_date,
        end_date,
        specific_dates=specific_dates,
    )
    context['two_hour_metrics_week'] = two_hour_metrics_week
    context['two_hour_max_emails_week'] = two_hour_max_emails_week

    # Compute weekly response time distribution
    weekly_response_time_distribution = compute_weekly_response_time_distribution(
        db,
        sla_config,
        start_date,
        end_date,
        specific_dates=specific_dates,
    )
    context['weekly_response_time_distribution'] = weekly_response_time_distribution

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
