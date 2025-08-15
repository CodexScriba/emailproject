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

class DashboardGenerator:
    def __init__(self, json_path, template_path, output_path):
        self.json_path = json_path
        self.template_path = template_path
        self.output_path = output_path
        
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
        """Extract data for business hours (7 AM to 6 PM)"""
        business_hours = []
        for hour_data in hourly_data:
            hour = hour_data['hour']
            if 7 <= hour <= 18:  # 7 AM to 6 PM
                business_hours.append({
                    'hour': hour,
                    'emails': hour_data.get('emails_received', 0) or 0,
                    'unread': hour_data.get('unread_count', 0) or 0,
                    'sla_met': hour_data.get('sla_met', False)
                })
        return business_hours
    
    def calculate_svg_coordinates(self, data_points, max_value, is_emails=True):
        """Calculate SVG coordinates for line chart data"""
        coordinates = []
        
        # Calculate X positions (evenly spaced across plot width)
        hours_count = len(data_points)
        x_step = self.plot_width / (hours_count - 1) if hours_count > 1 else 0
        
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
                'hour': 7 + i  # Starting from 7 AM
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
        unread_values = [item['unread'] for item in business_data]
        
        # Calculate max values for scaling
        max_emails = max(email_values) if email_values else 1
        max_unread = max(unread_values) if unread_values else 1
        overall_max = max(max_emails, max_unread)
        
        # Calculate coordinates
        email_coords = self.calculate_svg_coordinates(email_values, overall_max, True)
        unread_coords = self.calculate_svg_coordinates(unread_values, overall_max, False)
        
        # Create SVG paths
        email_path = self.create_svg_path(email_coords)
        unread_path = self.create_svg_path(unread_coords)
        
        # Generate Y-axis labels
        y_labels = []
        for i in range(6):  # 5 grid lines + 1
            value = int((overall_max / 5) * i)
            y_pos = self.chart_top_margin + (self.plot_height * (1 - i/5))
            y_labels.append({'value': value, 'y': round(y_pos)})
        
        # Generate X-axis labels
        x_labels = []
        for i, coord in enumerate(email_coords):
            hour = 7 + i
            x_labels.append({
                'hour': hour,
                'label': self.format_hour_label(hour),
                'x': coord['x']
            })
        
        # Prepare template context
        context = {
            'date': date_str,
            'formatted_date': datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y'),
            'daily_summary': day_data['daily_summary'],
            'email_path': email_path,
            'unread_path': unread_path,
            'email_coords': email_coords,
            'unread_coords': unread_coords,
            'y_labels': y_labels,
            'x_labels': x_labels,
            'business_data': business_data,
            'chart_width': self.chart_width,
            'chart_height': self.chart_height,
            'max_value': overall_max
        }
        
        return context
    
    def render_template(self, context):
        """Render the dashboard template with context data"""
        # Load template (convert to Jinja2 template)
        with open(self.template_path, 'r') as f:
            template_content = f.read()
        
        # Convert hardcoded template to Jinja2 template
        template_content = self.convert_to_jinja_template(template_content)
        
        template = Template(template_content)
        return template.render(context)
    
    def convert_to_jinja_template(self, html_content):
        """Convert the hardcoded HTML template to use Jinja2 variables"""
        # Replace title
        html_content = html_content.replace(
            'Email Dashboard - KPI Overview',
            'Email Dashboard - {{ formatted_date }}'
        )
        
        # Replace hardcoded KPI values
        html_content = html_content.replace(
            '<div class="kpi-value">262</div>',
            '<div class="kpi-value">{{ daily_summary.total_emails or 0 }}</div>'
        )
        html_content = html_content.replace(
            '<div class="kpi-value">65.2 min</div>',
            '<div class="kpi-value">{{ "%.1f"|format(daily_summary.avg_response_time_minutes or 0) }} min</div>'
        )
        html_content = html_content.replace(
            '<div class="kpi-value">66.67%</div>',
            '<div class="kpi-value">{{ "%.1f"|format(daily_summary.sla_compliance_rate or 0) }}%</div>'
        )
        html_content = html_content.replace(
            '<div class="kpi-value">29.5</div>',
            '<div class="kpi-value">{{ daily_summary.avg_unread_count or 0 }}</div>'
        )
        
        # Replace SVG paths
        html_content = html_content.replace(
            'path id="emails-line" class="line-emails" d="M 135,356 L 190,350 L 245,266 L 300,326 L 355,260 L 410,150 L 465,278 L 520,224 L 575,194 L 630,224 L 685,230 L 740,350 L 795,278 L 845,356 L 900,374"',
            'path id="emails-line" class="line-emails" d="{{ email_path }}"'
        )
        html_content = html_content.replace(
            'path id="unread-line" class="line-unread" d="M 135,268 L 190,292 L 245,322 L 300,284 L 355,324 L 410,268 L 465,256 L 520,194 L 575,194 L 630,112 L 685,74 L 740,268 L 795,272 L 845,272 L 900,324"',
            'path id="unread-line" class="line-unread" d="{{ unread_path }}"'
        )
        
        # Replace data points and labels (this is more complex, we'll replace the entire sections)
        # Find and replace email points section
        import re
        
        # Replace email data points
        email_points_pattern = r'<g id="email-points">.*?</g>'
        email_points_replacement = '''<g id="email-points">
                {% for coord in email_coords %}
                <circle cx="{{ coord.x }}" cy="{{ coord.y }}" r="4" class="data-point point-emails"/>
                <text x="{{ coord.x }}" y="{{ coord.y - 10 }}" class="data-label label-emails">{{ coord.value }}</text>
                {% endfor %}
            </g>'''
        html_content = re.sub(email_points_pattern, email_points_replacement, html_content, flags=re.DOTALL)
        
        # Replace unread data points
        unread_points_pattern = r'<g id="unread-points">.*?</g>'
        unread_points_replacement = '''<g id="unread-points">
                {% for coord in unread_coords %}
                <circle cx="{{ coord.x }}" cy="{{ coord.y }}" r="4" class="data-point point-unread"/>
                <text x="{{ coord.x }}" y="{{ coord.y - 10 }}" class="data-label label-unread">{{ coord.value }}</text>
                {% endfor %}
            </g>'''
        html_content = re.sub(unread_points_pattern, unread_points_replacement, html_content, flags=re.DOTALL)
        
        # Replace X-axis labels
        x_axis_pattern = r'<!-- X-axis Labels -->.*?(?=<!-- SLA Indicators -->|</svg>)'
        x_axis_replacement = '''<!-- X-axis Labels -->
            {% for label in x_labels %}
            <text x="{{ label.x }}" y="{{ chart_height - 20 }}" class="axis-label" text-anchor="middle">{{ label.label }}</text>
            {% endfor %}
            
            '''
        html_content = re.sub(x_axis_pattern, x_axis_replacement, html_content, flags=re.DOTALL)
        
        # Replace Y-axis labels
        y_axis_pattern = r'<!-- Y-axis Labels -->.*?(?=<!-- X-axis Labels -->)'
        y_axis_replacement = '''<!-- Y-axis Labels -->
            {% for label in y_labels %}
            <text x="70" y="{{ label.y + 4 }}" class="y-axis-label" text-anchor="end">{{ label.value }}</text>
            {% endfor %}
            
            '''
        html_content = re.sub(y_axis_pattern, y_axis_replacement, html_content, flags=re.DOTALL)
        
        # Replace SLA indicators
        sla_pattern = r'<!-- SLA Indicators -->.*?(?=</svg>)'
        sla_replacement = '''<!-- SLA Indicators -->
            {% for item in business_data %}
            {% set coord = unread_coords[loop.index0] %}
            <text x="{{ coord.x }}" y="{{ coord.y + 25 }}" class="sla-indicator {{ 'sla-met' if item.sla_met else 'sla-failed' }}" text-anchor="middle">
                {{ '✓' if item.sla_met else '✗' }}
            </text>
            {% endfor %}
            '''
        html_content = re.sub(sla_pattern, sla_replacement, html_content, flags=re.DOTALL)
        
        return html_content
    
    def save_dashboard(self, rendered_html):
        """Save the rendered dashboard to output file"""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w') as f:
            f.write(rendered_html)

def main():
    """Main function to generate dashboard"""
    # Get script directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Define paths
    json_path = project_root / "email_database.json"
    template_path = project_root / "dashboard" / "templates" / "kpi_cards.html"
    
    # Generate output filename with current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_path = project_root / "dashboard" / "output" / f"email_dashboard_{current_date}.html"
    
    # Check if files exist
    if not json_path.exists():
        print(f"Error: JSON database not found at {json_path}")
        sys.exit(1)
    
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        sys.exit(1)
    
    try:
        # Initialize generator
        generator = DashboardGenerator(str(json_path), str(template_path), str(output_path))
        
        # Generate dashboard context
        print("Generating dashboard...")
        context = generator.generate_dashboard()
        
        print(f"Using data from: {context['formatted_date']}")
        print(f"Total emails: {context['daily_summary']['total_emails']}")
        print(f"SLA compliance: {context['daily_summary']['sla_compliance_rate']:.1f}%")
        
        # Render template
        print("Rendering template...")
        rendered_html = generator.render_template(context)
        
        # Save dashboard
        generator.save_dashboard(rendered_html)
        
        print(f"Dashboard generated successfully!")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"Error generating dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()