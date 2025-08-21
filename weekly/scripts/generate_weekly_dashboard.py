#!/usr/bin/env python3
"""
Weekly Email Dashboard Generator
Generates a minimal weekly dashboard with title only, outputs to latest.html
"""

import json
import os
import sys
from datetime import datetime, timedelta
import argparse
from pathlib import Path

def load_sla_config():
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

def get_week_dates(week_str):
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

def get_last_7_days():
    """Get date range for last 7 days"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    return start_date, end_date

def format_week_title(start_date, end_date, is_last_7_days=False):
    """Format week title for display"""
    if is_last_7_days:
        return f"Last 7 Days • {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    else:
        # Calculate ISO week number
        year, week, _ = start_date.isocalendar()
        return f"Week {week} • {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

def generate_dashboard_html(week_title):
    """Generate minimal dashboard HTML with title only"""
    template_path = Path(__file__).parent.parent / "templates" / "weekly_kpi_cards.html"
    
    try:
        with open(template_path, 'r') as f:
            template = f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        sys.exit(1)
    
    # Replace template variables
    html_content = template.replace('{{ week_title }}', week_title)
    
    return html_content

def save_dashboard(html_content, week_identifier, is_last_7_days=False):
    """Save dashboard HTML to output directory"""
    output_dir = Path(__file__).parent.parent / "output"
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
    
    args = parser.parse_args()
    
    # Load configuration
    sla_config = load_sla_config()
    
    # Determine date range
    if args.last_7_days:
        start_date, end_date = get_last_7_days()
        week_identifier = f"last7days_{datetime.now().strftime('%Y%m%d')}"
        is_last_7_days = True
    else:
        start_date, end_date = get_week_dates(args.week)
        week_identifier = args.week.replace('-W', '-W')
        is_last_7_days = False
    
    # Format week title
    week_title = format_week_title(start_date, end_date, is_last_7_days)
    
    # Generate dashboard HTML
    html_content = generate_dashboard_html(week_title)
    
    # Save dashboard
    output_path = save_dashboard(html_content, week_identifier, is_last_7_days)
    
    print(f"Weekly dashboard generated successfully for {week_identifier}")

if __name__ == "__main__":
    main()
