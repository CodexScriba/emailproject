#!/usr/bin/env python3
"""
Email Dashboard Generator

Automatically generates an email dashboard from the unified JSON database.
This script reads email and SLA data, calculates dynamic SVG coordinates,
and outputs a complete HTML dashboard.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from jinja2 import Template
import statistics
import argparse

class DashboardGenerator:
    def __init__(self, json_path, template_path, output_path, sla_config_path=None):
        self.json_path = json_path
        self.template_path = template_path
        self.output_path = output_path
        self.sla_config_path = sla_config_path
        self.sla_config = None
        
        # Load SLA configuration if provided
        if sla_config_path:
            self.load_sla_config()
        
        # Chart configuration
        self.chart_width = 900
        self.chart_height = 400
        self.chart_left_margin = 80
        self.chart_right_margin = 50
        self.chart_top_margin = 60
        self.chart_bottom_margin = 60
        
        # Calculate plotting area
        self.plot_width = self.chart_width - self.chart_left_margin - self.chart_right_margin
        self.plot_height = self.chart_height - self.chart_top_margin - self.chart_bottom_margin
        
    def get_business_hour_bounds(self):
        """Return (start_hour, end_hour) from SLA config if available, else defaults (7, 21).
        Ensures values are clamped to 0–23.
        """
        cfg = (self.sla_config or {}).get('sla_thresholds', {}).get('business_hours', {})
        start_hour = cfg.get('start_hour', 7)
        end_hour = cfg.get('end_hour', 21)
        try:
            start_hour = int(start_hour)
        except Exception:
            start_hour = 7
        try:
            end_hour = int(end_hour)
        except Exception:
            end_hour = 21
        start_hour = max(0, min(23, start_hour))
        end_hour = max(0, min(23, end_hour))
        return start_hour, end_hour
        
    def load_sla_config(self):
        """Load SLA configuration from JSON file."""
        try:
            with open(self.sla_config_path, 'r') as f:
                self.sla_config = json.load(f)
            print(f"Loaded SLA config: {self.sla_config['metadata']['version']}")
        except Exception as e:
            print(f"Warning: Could not load SLA config from {self.sla_config_path}: {e}")
            self.sla_config = None
        
    def load_data(self):
        """Load and parse the JSON database"""
        with open(self.json_path, 'r') as f:
            return json.load(f)
    
    def get_latest_complete_day(self, data):
        """Find the most recent day with both email and SLA data"""
        for date_str in sorted(data['days'].keys(), reverse=True):
            day_data = data['days'][date_str]
            if day_data.get('has_email_data', False) and day_data.get('has_sla_data', False):
                return date_str, day_data
        raise ValueError("No complete day found with both email and SLA data")
    
    def extract_business_hours_data(self, hourly_data):
        """Extract data for configured business hours (from SLA config or defaults)."""
        business_hours = []
        start_hour, end_hour = self.get_business_hour_bounds()
        for hour_data in hourly_data:
            hour = hour_data['hour']
            if start_hour <= hour <= end_hour:  # configurable business hours
                # Handle null unread_count by preserving None instead of converting to 0
                unread_count = hour_data.get('unread_count')
                business_hours.append({
                    'hour': hour,
                    'emails': hour_data.get('emails_received', 0) or 0,
                    'unread': unread_count,  # Keep None for missing data
                    'sla_met': hour_data.get('sla_met', False),
                    'avg_response_time': hour_data.get('avg_response_time', None),
                    'emails_replied': hour_data.get('emails_replied', 0) or 0
                })
        return business_hours
    
    def calculate_response_time_by_hour(self, hourly_data):
        """Calculate response time metrics grouped by hour periods"""
        periods = {
            'Early Morning (6-9 AM)': {'hours': [6, 7, 8], 'total_time': 0, 'count': 0, 'color': 'success'},
            'Morning (9 AM-1 PM)': {'hours': [9, 10, 11, 12], 'total_time': 0, 'count': 0, 'color': 'warning'},
            'Afternoon (1-5 PM)': {'hours': [13, 14, 15, 16], 'total_time': 0, 'count': 0, 'color': 'danger'},
            'Evening (5-9 PM)': {'hours': [17, 18, 19, 20, 21], 'total_time': 0, 'count': 0, 'color': 'warning'}
        }
        
        for hour_data in hourly_data:
            hour = hour_data['hour']
            response_time = hour_data.get('avg_response_time', None)
            replied_count = hour_data.get('emails_replied', 0) or 0
            
            if response_time is not None and replied_count > 0:
                for period_name, period_data in periods.items():
                    if hour in period_data['hours']:
                        period_data['total_time'] += response_time * replied_count
                        period_data['count'] += replied_count
                        break
        
        # Calculate averages and format results
        result = []
        for period_name, period_data in periods.items():
            if period_data['count'] > 0:
                avg_time = period_data['total_time'] / period_data['count']
                # Apply SLA-based coloring
                if avg_time <= 60:
                    color = 'success'
                elif avg_time <= 120:
                    color = 'warning'
                else:
                    color = 'danger'
            else:
                avg_time = 0
                color = 'muted'
            
            result.append({
                'period': period_name,
                'avg_response_time': round(avg_time, 1),
                'color': color
            })
        
        return result
    
    def calculate_response_time_distribution(self, hourly_data):
        """Calculate distribution of email response times"""
        distribution = {
            'Very Fast (< 30 min)': {'count': 0, 'color': 'success'},
            'Fast (30-60 min)': {'count': 0, 'color': 'success'},
            'Moderate (60-120 min)': {'count': 0, 'color': 'warning'},
            'Slow (120-180 min)': {'count': 0, 'color': 'warning'},
            'Very Slow (180-300 min)': {'count': 0, 'color': 'danger'},
            'Critical (> 300 min)': {'count': 0, 'color': 'danger'}
        }
        
        for hour_data in hourly_data:
            response_time = hour_data.get('avg_response_time', None)
            replied_count = hour_data.get('emails_replied', 0) or 0
            
            if response_time is not None and replied_count > 0:
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
        
        # Convert to list format
        result = []
        # Use total count for percentage so bars represent composition of all replied emails
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
    
    def calculate_response_time_percentiles(self, hourly_data):
        """Calculate response time percentiles and bar widths for the new design."""
        response_times = []
        
        for hour_data in hourly_data:
            response_time = hour_data.get('avg_response_time', None)
            replied_count = hour_data.get('emails_replied', 0) or 0
            
            if response_time is not None and replied_count > 0:
                for _ in range(int(replied_count)):
                    response_times.append(response_time)
        
        if not response_times:
            return {
                'percentiles': [
                    {'label': 'P25', 'value': 0, 'percentage': 25, 'color': 'muted', 'bar_width': 0},
                    {'label': 'P50', 'value': 0, 'percentage': 50, 'color': 'muted', 'bar_width': 0},
                    {'label': 'P75', 'value': 0, 'percentage': 75, 'color': 'muted', 'bar_width': 0},
                    {'label': 'P90', 'value': 0, 'percentage': 90, 'color': 'muted', 'bar_width': 0},
                    {'label': 'P95', 'value': 0, 'percentage': 95, 'color': 'muted', 'bar_width': 0}
                ],
                'quartiles': {'q1_count': 0, 'q2_count': 0, 'q3_count': 0, 'q4_count': 0},
                'has_data': False,
                'sla_target': self.sla_config['kpi_targets']['response_time_target_minutes'] if self.sla_config else 60
            }
        
        response_times.sort()
        total_count = len(response_times)

        # Helper to compute percentiles accurately
        def get_percentile(arr, p):
            # P50 should match true median for even/odd counts
            if p == 50:
                return statistics.median(arr)
            # Use inclusive method to match common dashboard expectations
            try:
                qs = statistics.quantiles(arr, n=100, method='inclusive')
                return qs[p - 1]
            except Exception:
                # Fallback: nearest-rank style using bounds
                idx = int(round((p / 100) * (len(arr) - 1)))
                idx = max(0, min(idx, len(arr) - 1))
                return arr[idx]

        percentiles = []
        for p_value, p_label in [(25, 'P25'), (50, 'P50'), (75, 'P75'), (90, 'P90'), (95, 'P95')]:
            value = get_percentile(response_times, p_value)

            if value <= 60:
                color = 'success'
            elif value <= 120:
                color = 'warning'
            else:
                color = 'danger'

            percentiles.append({
                'label': p_label,
                'value': round(value, 1),
                'percentage': p_value,
                'color': color
            })
            
        # Calculate bar widths based on the max percentile value (P95)
        max_p_value = percentiles[-1]['value'] if percentiles else 0
        for p in percentiles:
            if max_p_value > 0:
                p['bar_width'] = round((p['value'] / max_p_value) * 100)
            else:
                p['bar_width'] = 0

        # Calculate quartile counts
        p25_val = percentiles[0]['value']
        p50_val = percentiles[1]['value']
        p75_val = percentiles[2]['value']
        
        quartiles = {
            'q1_count': sum(1 for rt in response_times if rt <= p25_val),
            'q2_count': sum(1 for rt in response_times if p25_val < rt <= p50_val),
            'q3_count': sum(1 for rt in response_times if p50_val < rt <= p75_val),
            'q4_count': sum(1 for rt in response_times if rt > p75_val)
        }
        
        return {
            'percentiles': percentiles,
            'quartiles': quartiles,
            'has_data': True,
            'sla_target': self.sla_config['kpi_targets']['response_time_target_minutes'] if self.sla_config else 60
        }
    
    def aggregate_two_hour_intervals(self, hourly_data):
        """Aggregate hourly metrics into 2-hour blocks across configured business hours.
        Computes totals/averages per block:
        - emails: sum of emails_received
        - avg_unread: mean of unread_count (ignoring None)
        - sla_met: True only if all measured hours in the block met SLA; None if no data
        - avg_response_time: weighted average by emails_replied
        - median_response_time: weighted median using per-hour avg_response_time expanded by emails_replied
        - avg_mean_time: same as avg_response_time (business minutes)
        """
        intervals = []
        start_hour, end_hour = self.get_business_hour_bounds()
        for start in range(start_hour, end_hour, 2):
            end = min(start + 2, end_hour)
            hours = [h for h in hourly_data if h.get('hour') in (start, start + 1)]

            emails_sum = sum((h.get('emails_received') or 0) for h in hours)

            unread_vals = [h.get('unread_count') for h in hours if h.get('unread_count') is not None]
            avg_unread = round(sum(unread_vals) / len(unread_vals), 1) if unread_vals else None

            sla_vals = [h.get('sla_met') for h in hours if h.get('sla_met') is not None]
            if not sla_vals:
                sla_met = None
            else:
                sla_met = all(sla_vals)

            weighted_sum = 0
            total_weight = 0
            for h in hours:
                rt = h.get('avg_response_time')
                w = h.get('emails_replied') or 0
                if rt is not None and w > 0:
                    weighted_sum += rt * w
                    total_weight += w
            avg_rt = round(weighted_sum / total_weight, 1) if total_weight > 0 else None

            # Weighted median approximation by expanding per-hour averages by emails_replied
            rt_samples = []
            for h in hours:
                rt = h.get('avg_response_time')
                w = h.get('emails_replied') or 0
                if rt is not None and w > 0:
                    rt_samples.extend([rt] * int(w))
            median_rt = round(statistics.median(rt_samples), 1) if rt_samples else None

            intervals.append({
                'label': f"{self.format_hour_label(start)} – {self.format_hour_label(end)}",
                'start_hour': start,
                'end_hour': end,
                'emails': int(emails_sum),
                'avg_unread': avg_unread,
                'sla_met': sla_met,
                'avg_response_time': avg_rt,
                'avg_mean_time': avg_rt,
                'median_response_time': median_rt
            })

        return intervals
    
    def calculate_svg_coordinates(self, data_points, max_value, is_emails=True):
        """Calculate SVG coordinates for line chart data"""
        coordinates = []
        
        # Calculate X positions (evenly spaced across plot width)
        hours_count = len(data_points)
        x_step = self.plot_width / (hours_count - 1) if hours_count > 1 else 0
        start_hour, _ = self.get_business_hour_bounds()
        
        for i, value in enumerate(data_points):
            # X coordinate
            x = self.chart_left_margin + (i * x_step)
            
            # Y coordinate (inverted because SVG y=0 is at top)
            if max_value > 0:
                y_ratio = value / max_value
                y = self.chart_top_margin + (self.plot_height * (1 - y_ratio))
            else:
                y = self.chart_top_margin + self.plot_height
            
            coordinates.append({
                'x': round(x),
                'y': round(y),
                'value': value,
                'hour': start_hour + i  # Starting from configured business-hour start
            })
        
        return coordinates
    
    def create_svg_path(self, coordinates):
        """Create SVG path string from coordinates"""
        if not coordinates:
            return ""
        
        path_parts = [f"M {coordinates[0]['x']},{coordinates[0]['y']}"]
        for coord in coordinates[1:]:
            path_parts.append(f"L {coord['x']},{coord['y']}")
        
        return " ".join(path_parts)
    
    def create_smooth_svg_path(self, coordinates, tension: float = 1.0):
        """Create a smoothed SVG path using Catmull–Rom to cubic Bezier conversion.
        If fewer than 2 points, returns a move command only.
        Handles missing data by skipping points marked as missing_data.
        """
        if not coordinates:
            return ""
        
        # Filter out missing data points
        valid_coords = [c for c in coordinates if not c.get('is_missing_data', False)]
        
        if not valid_coords:
            return ""
        if len(valid_coords) == 1:
            return f"M {valid_coords[0]['x']},{valid_coords[0]['y']}"

        # Extract points from valid coordinates only
        pts = [(c['x'], c['y']) for c in valid_coords]
        path = [f"M {pts[0][0]},{pts[0][1]}"]

        for i in range(len(pts) - 1):
            p0 = pts[i - 1] if i - 1 >= 0 else pts[i]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]

            c1x = p1[0] + (p2[0] - p0[0]) / 6.0 * tension
            c1y = p1[1] + (p2[1] - p0[1]) / 6.0 * tension
            c2x = p2[0] - (p3[0] - p1[0]) / 6.0 * tension
            c2y = p2[1] - (p3[1] - p1[1]) / 6.0 * tension

            path.append(
                f"C {round(c1x, 2)},{round(c1y, 2)} {round(c2x, 2)},{round(c2y, 2)} {p2[0]},{p2[1]}"
            )

        return " ".join(path)

    def create_area_path(self, coordinates, baseline_y: float, use_smooth: bool = True, tension: float = 1.0):
        """Create a closed area path under the line down to the given baseline (x-axis)."""
        if not coordinates:
            return ""
        
        # Filter out missing data for area path too
        valid_coords = [c for c in coordinates if not c.get('is_missing_data', False)]
        
        if not valid_coords:
            return ""
            
        line_path = (
            self.create_smooth_svg_path(coordinates, tension) if use_smooth else self.create_svg_path(coordinates)
        )
        first_x = valid_coords[0]['x']
        last_x = valid_coords[-1]['x']
        # Close down to baseline and back to start
        area_path = f"{line_path} L {last_x},{baseline_y} L {first_x},{baseline_y} Z"
        return area_path
    
    def format_hour_label(self, hour):
        """Format hour as 12-hour time"""
        if hour == 0:
            return "12 AM"
        elif hour < 12:
            return f"{hour} AM"
        elif hour == 12:
            return "12 PM"
        else:
            return f"{hour - 12} PM"
    
    def generate_dashboard(self, target_date=None):
        """Generate the complete dashboard"""
        # Load data
        data = self.load_data()
        
        # Get target day data
        if target_date:
            if target_date not in data['days']:
                raise ValueError(f"Date {target_date} not found in database")
            date_str = target_date
            day_data = data['days'][target_date]
        else:
            date_str, day_data = self.get_latest_complete_day(data)
        
        # Extract business hours data
        business_data = self.extract_business_hours_data(day_data['hourly_data'])
        
        # Extract data series
        email_values = [item['emails'] for item in business_data]
        # For unread values, handle missing data properly
        unread_raw_values = [item['unread'] for item in business_data]
        
        # Targets and thresholds needed for scaling and template
        unread_threshold = (self.sla_config or {}).get('sla_thresholds', {}).get('unread_email_threshold', 30)

        # Calculate max values for scaling (ensure SLA threshold is visible on chart)
        # Only use non-null unread values for max calculation
        valid_unread_values = [v for v in unread_raw_values if v is not None]
        max_emails = max(email_values) if email_values else 1
        max_unread = max(valid_unread_values) if valid_unread_values else 1
        overall_max = max(max_emails, max_unread, unread_threshold)
        
        # Calculate coordinates - use 0 for display but track original values
        unread_display_values = [v if v is not None else 0 for v in unread_raw_values]
        email_coords = self.calculate_svg_coordinates(email_values, overall_max, True)
        unread_coords = self.calculate_svg_coordinates(unread_display_values, overall_max, False)
        
        # Mark coordinates that represent missing data
        for i, coord in enumerate(unread_coords):
            coord['is_missing_data'] = unread_raw_values[i] is None
            
        # Filter out missing data coordinates for template rendering (data points)
        unread_coords_filtered = [coord for coord in unread_coords if not coord.get('is_missing_data', False)]
        
        # SLA threshold Y position (horizontal line)
        if overall_max > 0:
            sla_ratio = unread_threshold / overall_max
        else:
            sla_ratio = 0
        sla_line_y = round(self.chart_top_margin + (self.plot_height * (1 - sla_ratio)))

        # Create smoothed SVG paths and area fills
        email_path = self.create_smooth_svg_path(email_coords)
        unread_path = self.create_smooth_svg_path(unread_coords)
        baseline_y = self.chart_height - self.chart_bottom_margin
        email_area_path = self.create_area_path(email_coords, baseline_y, use_smooth=True)
        unread_area_path = self.create_area_path(unread_coords, baseline_y, use_smooth=True)
        
        # Generate Y-axis labels
        y_labels = []
        for i in range(6):  # 5 grid lines + 1
            value = int((overall_max / 5) * i)
            y_pos = self.chart_top_margin + (self.plot_height * (1 - i/5))
            y_labels.append({'value': value, 'y': round(y_pos)})
        
        # Generate X-axis labels
        x_labels = []
        start_hour, _ = self.get_business_hour_bounds()
        for i, coord in enumerate(email_coords):
            hour = start_hour + i
            x_labels.append({
                'hour': hour,
                'label': self.format_hour_label(hour),
                'x': coord['x']
            })
        
        # Calculate response time components
        response_time_by_hour = self.calculate_response_time_by_hour(day_data['hourly_data'])
        response_time_distribution = self.calculate_response_time_distribution(day_data['hourly_data'])
        # Use business hours for percentiles to match KPI avg scope
        response_time_percentiles_data = self.calculate_response_time_percentiles(business_data)
        two_hour_metrics = self.aggregate_two_hour_intervals(day_data['hourly_data'])
        # For scaling microbars in the two-hour table
        if two_hour_metrics:
            two_hour_max_emails = max(item['emails'] for item in two_hour_metrics)
        else:
            two_hour_max_emails = 1
        
        # Extract percentiles list and quartile counts from the response
        response_time_percentiles = response_time_percentiles_data.get('percentiles', [])
        quartiles_raw = response_time_percentiles_data.get('quartiles', {})
        
        # Convert quartiles to expected format
        total_emails = sum([quartiles_raw.get('q1_count', 0), quartiles_raw.get('q2_count', 0), 
                           quartiles_raw.get('q3_count', 0), quartiles_raw.get('q4_count', 0)])
        
        quartile_counts = []
        if total_emails > 0:
            quartile_counts = [
                {
                    'label': 'Q1 (0-25%)',
                    'count': quartiles_raw.get('q1_count', 0),
                    'percentage': round((quartiles_raw.get('q1_count', 0) / total_emails) * 100)
                },
                {
                    'label': 'Q2 (25-50%)',
                    'count': quartiles_raw.get('q2_count', 0),
                    'percentage': round((quartiles_raw.get('q2_count', 0) / total_emails) * 100)
                },
                {
                    'label': 'Q3 (50-75%)',
                    'count': quartiles_raw.get('q3_count', 0),
                    'percentage': round((quartiles_raw.get('q3_count', 0) / total_emails) * 100)
                },
                {
                    'label': 'Q4 (75-100%)',
                    'count': quartiles_raw.get('q4_count', 0),
                    'percentage': round((quartiles_raw.get('q4_count', 0) / total_emails) * 100)
                }
            ]
        
        # Prepare template context
        formatted_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')
        daily_data = day_data['daily_summary']
        sla_compliance = round(daily_data['sla_compliance_rate'], 1)
        hourly_data = day_data['hourly_data']

        # Friendly timestamp for header (e.g., "2:40 PM")
        generated_at = datetime.now().strftime("%I:%M %p").lstrip("0")

        # Robust total emails fallback
        total_emails_val = daily_data.get('total_emails')
        if not total_emails_val:
            total_emails_val = sum(email_values)

        # Targets and thresholds for template convenience
        response_time_target = (self.sla_config or {}).get('kpi_targets', {}).get('response_time_target_minutes', 60)
        sla_compliance_target = (self.sla_config or {}).get('kpi_targets', {}).get('sla_compliance_target_percent', 85)

        # Compute business-hours weighted avg response time; fallback to daily summary minutes if present
        weighted_sum = 0
        total_weight = 0
        for h in business_data:
            rt = h.get('avg_response_time')
            w = h.get('emails_replied') or 0
            if rt is not None and w > 0:
                weighted_sum += rt * w
                total_weight += w
        computed_avg_rt = round(weighted_sum / total_weight, 1) if total_weight > 0 else None
        # Prefer business-hours computed average to keep scope consistent with percentiles/median
        if computed_avg_rt is not None:
            avg_response_time_val = computed_avg_rt
        else:
            avg_response_time_val = daily_data.get('avg_response_time_minutes') or 0

        # Median (P50) for quick reference in KPI card
        median_response_time = next((p['value'] for p in response_time_percentiles if p['label'] == 'P50'), 0)

        # Business hour labels for template (dynamic from SLA config)
        bh_start, bh_end = self.get_business_hour_bounds()
        bh_start_label = self.format_hour_label(bh_start)
        bh_end_label = self.format_hour_label(bh_end)
        bh_range_label = f"{bh_start_label} – {bh_end_label}"

        context = {
            'formatted_date': formatted_date,
            'date_str': date_str,
            'generated_at': generated_at,
            'daily_data': daily_data,
            'total_emails': total_emails_val,
            'avg_unread_count': daily_data.get('avg_unread_count', 0),
            'avg_response_time': avg_response_time_val,
            'median_response_time': median_response_time,
            'sla_compliance': sla_compliance,
            'hourly_data': hourly_data,
            'sla_config': self.sla_config,
            'unread_threshold': unread_threshold,
            'response_time_target': response_time_target,
            'sla_compliance_target': sla_compliance_target,
            'response_time_by_hour': response_time_by_hour,
            'response_time_distribution': response_time_distribution,
            'response_time_percentiles': response_time_percentiles,
            'quartile_counts': quartile_counts,
            'two_hour_metrics': two_hour_metrics,
            'two_hour_max_emails': two_hour_max_emails,
            'email_path': email_path,
            'unread_path': unread_path,
            'email_area_path': email_area_path,
            'unread_area_path': unread_area_path,
            'email_coords': email_coords,
            'unread_coords': unread_coords_filtered,
            'sla_line_y': sla_line_y,
            'y_labels': y_labels,
            'x_labels': x_labels,
            'business_data': business_data,
            'chart_height': self.chart_height,
            'chart_width': self.chart_width,
            'chart_left_margin': self.chart_left_margin,
            'chart_right_margin': self.chart_right_margin,
            'chart_top_margin': self.chart_top_margin,
            'chart_bottom_margin': self.chart_bottom_margin,
            'plot_width': self.plot_width,
            'plot_height': self.plot_height,
            # Dynamic business-hour metadata for template usage
            'business_start_hour': bh_start,
            'business_end_hour': bh_end,
            'business_start_label': bh_start_label,
            'business_end_label': bh_end_label,
            'business_hours_label': bh_range_label
        }
        
        return context
    
    def render_template(self, context):
        """Render the dashboard template with context data"""
        # Load template
        with open(self.template_path, 'r') as f:
            template_content = f.read()
        
        # Convert hardcoded template to Jinja2 template (if needed)
        template_content = self.convert_to_jinja_template(template_content)
        
        template = Template(template_content)
        return template.render(context)
    
    def convert_to_jinja_template(self, html_content):
        """Convert the hardcoded HTML template to use Jinja2 variables"""
        # This function is optional - if the template already uses Jinja2 syntax,
        # it will just return the content as-is
        return html_content
    
    def save_dashboard(self, rendered_html, date_str, write_latest: bool = True):
        """Save the rendered dashboard to output file.
        Optionally also write a convenient 'latest.html' alias in the same directory.
        """
        output_filename = f"email_dashboard_{date_str}.html"
        output_path = os.path.join(self.output_path, output_filename)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(rendered_html)
        
        # Also write a 'latest.html' alias to quickly open the most recently generated dashboard
        if write_latest:
            latest_path = os.path.join(self.output_path, "latest.html")
            try:
                with open(latest_path, 'w') as f:
                    f.write(rendered_html)
                print(f"Dashboard saved to: {output_path} (alias: {latest_path})")
            except Exception as e:
                # Still consider main save successful
                print(f"Dashboard saved to: {output_path}")
                print(f"Warning: Could not write latest alias: {e}")
        else:
            print(f"Dashboard saved to: {output_path}")
        return output_path

def main():
    """Main function to generate dashboard"""
    parser = argparse.ArgumentParser(description="Generate email dashboard HTML from unified JSON data.")
    parser.add_argument("--date", dest="date", help="Target date in YYYY-MM-DD. If omitted, uses latest complete day.")
    parser.add_argument("--validate-only", dest="validate_only", action="store_true",
                        help="Validate KPIs for the selected date; print summary and exit non-zero if required fields are missing.")
    parser.add_argument("--list-dates", dest="list_dates", action="store_true",
                        help="List available dates from email_database.json and whether each is complete.")
    args = parser.parse_args()

    # Get script directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Define paths
    json_path = project_root / "database" / "email_database.json"
    template_path = project_root / "daily" / "dashboard" / "templates" / "kpi_cards.html"
    sla_config_path = project_root / "config" / "sla_config.json"
    output_dir = project_root / "daily" / "dashboard" / "output"
    
    # Create generator
    generator = DashboardGenerator(
        json_path=str(json_path),
        template_path=str(template_path),
        output_path=str(output_dir),
        sla_config_path=str(sla_config_path)
    )
    
    # Handle "list dates" mode
    if args.list_dates:
        try:
            data = generator.load_data()
            days = data.get('days', {})
            for date_key in sorted(days.keys()):
                day = days[date_key]
                complete = day.get('has_email_data', False) and day.get('has_sla_data', False)
                total = (day.get('daily_summary') or {}).get('total_emails', 0)
                status = "complete" if complete else "incomplete"
                print(f"{date_key}  {status}  total_emails={total}")
            print(f"Found {len(days)} dates.")
            sys.exit(0)
        except Exception as e:
            print(f"Error listing dates: {e}", file=sys.stderr)
            sys.exit(2)
    
    # Handle validation mode
    if args.validate_only:
        try:
            context = generator.generate_dashboard(target_date=args.date)
        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            sys.exit(2)
        dd = context.get('daily_data') or {}
        hourly = context.get('hourly_data')
        missing = []
        if 'avg_unread_count' not in dd or dd.get('avg_unread_count') is None:
            missing.append('daily_data.avg_unread_count')
        if 'sla_compliance_rate' not in dd or dd.get('sla_compliance_rate') is None:
            missing.append('daily_data.sla_compliance_rate')
        if not hourly:
            missing.append('hourly_data')
        
        print("Validation KPIs")
        print(f"  Date: {context.get('date_str')}")
        print(f"  Total Emails: {context.get('total_emails')}")
        print(f"  Avg Unread Count: {context.get('avg_unread_count')}")
        print(f"  SLA Compliance: {context.get('sla_compliance')}%")
        print(f"  Avg Response Time: {context.get('avg_response_time')} min")
        
        if missing:
            print("Missing fields: " + ", ".join(missing), file=sys.stderr)
            sys.exit(1)
        else:
            print("\u2713 Validation passed")
            sys.exit(0)
    
    # Generate dashboard context
    context = generator.generate_dashboard(target_date=args.date)
    
    # Render template
    rendered_html = generator.render_template(context)
    
    # Save dashboard
    date_str = context.get('date_str') or datetime.now().strftime("%Y-%m-%d")
    output_path = generator.save_dashboard(rendered_html, date_str)
    
    print(f"\u2713 Dashboard generation complete!")
    print(f"  Output: {output_path}")

if __name__ == "__main__":
    main()
