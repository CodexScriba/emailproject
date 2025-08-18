#!/usr/bin/env python3
"""
Email Classification and SLA Compliance Calculator

This script processes two data sources to create a unified JSON database:
1. Complete_List_Raw.csv: Email lifecycle events and response time analysis
2. UnreadCount.csv: SLA compliance data with hourly unread counts

Features:
- Email classification (Replied, Completed, Pending)
- Business hours response time calculations (configurable via config/sla_config.json; default 7 AM – 9 PM, Monday–Sunday)
- Daily SLA compliance rate calculations (≤30 emails = SLA MET)
- Multi-day unified JSON database with both email and SLA metrics
- Dashboard-ready data structure for KPI generation

Business Hours: Configurable via config/sla_config.json (default 7:00 AM – 9:00 PM, Monday–Sunday)
SLA Threshold: 30 unread emails
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import os
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailClassifier:
    """Main class for processing and classifying email data."""
    
    def __init__(self, csv_file_path='../../data/Complete_List_Raw.csv', sla_file_path='../../data/UnreadCount.csv', sla_config_path='../../config/sla_config.json'):
        """Initialize the classifier with data file paths."""
        self.csv_file_path = self._resolve_relative_to_script(csv_file_path)
        self.sla_file_path = self._resolve_relative_to_script(sla_file_path)
        self.sla_config_path = self._resolve_relative_to_script(sla_config_path)
        self.df = None
        self.sla_df = None
        self.sla_config = None
        self.loaded_event_files = []  # names of event CSVs successfully loaded
        
        # Load SLA configuration
        self.load_sla_config()
        
        # Business hours configuration (from SLA config)
        self.business_start_hour = self.sla_config['sla_thresholds']['business_hours']['start_hour']
        self.business_end_hour = self.sla_config['sla_thresholds']['business_hours']['end_hour']
        self.business_days = self.sla_config['sla_thresholds']['business_hours']['business_days']
        self.unread_threshold = self.sla_config['sla_thresholds']['unread_email_threshold']
        
    def _resolve_relative_to_script(self, path_value):
        """Return an absolute Path for path_value, interpreting relative paths from this script's directory."""
        p = Path(path_value)
        if p.is_absolute():
            return p
        script_dir = Path(__file__).resolve().parent
        return (script_dir / p).resolve()

    def load_sla_config(self):
        """Load SLA configuration from JSON file."""
        try:
            with open(self.sla_config_path, 'r') as f:
                self.sla_config = json.load(f)
            logger.info(f"Loaded SLA config: {self.sla_config['metadata']['version']}")
            logger.info(f"Unread threshold: {self.sla_config['sla_thresholds']['unread_email_threshold']} emails")
        except Exception as e:
            logger.error(f"Error loading SLA config from {self.sla_config_path}: {e}")
            # Fallback to hardcoded values
            self.sla_config = {
                'sla_thresholds': {
                    'unread_email_threshold': 30,
                    'business_hours': {
                        'start_hour': 7,
                        'end_hour': 21,
                        'business_days': [0, 1, 2, 3, 4, 5, 6]
                    }
                }
            }
            logger.warning("Using fallback SLA configuration")
        
    def load_data(self):
        """Load and preprocess email event CSV data. Supports multiple daily files (MM-DD-YY.csv)."""
        logger.info(f"Loading data from {self.csv_file_path}")
        
        try:
            data_dir = Path(self.csv_file_path).resolve().parent
            files_to_load = []
            
            # Include the configured CSV if it exists
            if Path(self.csv_file_path).exists():
                files_to_load.append(Path(self.csv_file_path))
            
            # Discover daily CSVs in the same directory, e.g., 08-14-25.csv
            daily_pattern = re.compile(r"\d{2}-\d{2}-\d{2}\.csv$")
            for p in sorted(data_dir.iterdir()):
                if p.is_file() and daily_pattern.search(p.name):
                    files_to_load.append(p)
            
            if not files_to_load:
                raise FileNotFoundError(f"No input CSV files found in {data_dir}")
            
            frames = []
            self.loaded_event_files = []
            for fp in files_to_load:
                try:
                    df_part = pd.read_csv(fp)
                    frames.append(df_part)
                    logger.info(f"Loaded {len(df_part)} records from {fp.name}")
                    self.loaded_event_files.append(fp.name)
                except Exception as fe:
                    logger.warning(f"Skipping file {fp} due to read error: {fe}")
            
            if not frames:
                raise RuntimeError("No CSV files could be loaded successfully.")
            
            self.df = pd.concat(frames, ignore_index=True)
            logger.info(f"Total loaded records across files: {len(self.df)} (from {len(frames)} files)")

            # Deduplicate events to prevent double-counting across overlapping files
            if all(col in self.df.columns for col in ['Conversation-Id', 'TimeStamp', 'EventType', 'MessageId']):
                before = len(self.df)
                self.df = self.df.drop_duplicates(subset=['Conversation-Id', 'TimeStamp', 'EventType', 'MessageId'], keep='first')
                after = len(self.df)
                if after != before:
                    logger.info(f"Deduplicated events: removed {before - after} duplicate rows")
            
            # Convert timestamp to datetime
            self.df['TimeStamp'] = pd.to_datetime(self.df['TimeStamp'])
            
            # Sort by conversation ID and timestamp for easier processing
            self.df = self.df.sort_values(['Conversation-Id', 'TimeStamp'])
            
            logger.info("Data preprocessing completed")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def calculate_business_minutes(self, start_time, end_time):
        """
        Calculate business minutes between two timestamps.
        Only counts time within configured business hours (default 7 AM – 9 PM, Monday–Sunday).
        """
        if pd.isna(start_time) or pd.isna(end_time):
            return None
            
        if end_time <= start_time:
            return 0
            
        total_minutes = 0
        current_time = start_time
        
        while current_time < end_time:
            # Check if current day is a business day
            if current_time.weekday() in self.business_days:
                # Calculate business hours for this day
                day_start = current_time.replace(hour=self.business_start_hour, minute=0, second=0, microsecond=0)
                day_end = current_time.replace(hour=self.business_end_hour, minute=0, second=0, microsecond=0)
                
                # Adjust start time if before business hours
                period_start = max(current_time, day_start)
                # Adjust end time if after business hours or spans multiple days
                period_end = min(end_time, day_end)
                
                # Only add minutes if within business hours
                if period_start < period_end:
                    minutes_in_period = (period_end - period_start).total_seconds() / 60
                    total_minutes += minutes_in_period
            
            # Move to next day
            current_time = (current_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        return round(total_minutes, 2)
    
    def find_matching_event(self, inbox_row, conversation_events):
        """
        Find the next Replied or Completed event for an Inbox email.
        
        Priority:
        1. First Replied event after the Inbox timestamp
        2. If no Reply, first Completed event after the Inbox timestamp
        3. If neither, return None (Pending)
        """
        inbox_time = inbox_row['TimeStamp']
        
        # Filter events after the inbox timestamp
        later_events = conversation_events[conversation_events['TimeStamp'] > inbox_time]
        
        # Look for Replied events first
        replied_events = later_events[later_events['EventType'] == 'Replied']
        if not replied_events.empty:
            return replied_events.iloc[0], 'Replied'
        
        # If no replies, look for Completed events
        completed_events = later_events[later_events['EventType'] == 'Completed']
        if not completed_events.empty:
            return completed_events.iloc[0], 'Completed'
        
        # No matching event found
        return None, 'Pending'
    
    def process_conversations(self):
        """Process all conversations and classify emails."""
        logger.info("Processing conversations and matching events...")
        
        results = []
        
        # Group by conversation ID
        conversations = self.df.groupby('Conversation-Id')
        total_conversations = len(conversations)
        
        for conv_idx, (conv_id, conv_events) in enumerate(conversations):
            if conv_idx % 50 == 0:
                logger.info(f"Processing conversation {conv_idx + 1}/{total_conversations}")
            
            # Process each Inbox email in this conversation
            inbox_emails = conv_events[conv_events['EventType'] == 'Inbox']
            
            for _, inbox_email in inbox_emails.iterrows():
                # Find matching event
                match_event, status = self.find_matching_event(inbox_email, conv_events)
                
                # Calculate response time if match found
                response_time_minutes = None
                if match_event is not None:
                    response_time_minutes = self.calculate_business_minutes(
                        inbox_email['TimeStamp'], 
                        match_event['TimeStamp']
                    )
                
                # Create result record
                result = {
                    'Conversation-Id': conv_id,
                    'Inbox_Subject': inbox_email['Subject'],
                    'Inbox_Emails': inbox_email['Emails'],
                    'Inbox_TimeStamp': inbox_email['TimeStamp'],
                    'Inbox_MessageId': inbox_email['MessageId'],
                    'Status': status,
                    'Response_TimeStamp': match_event['TimeStamp'] if match_event is not None else None,
                    'Response_Subject': match_event['Subject'] if match_event is not None else None,
                    'Response_MessageId': match_event['MessageId'] if match_event is not None else None,
                    'Response_Time_Business_Minutes': response_time_minutes
                }
                
                results.append(result)
        
        logger.info(f"Processed {len(results)} inbox emails")
        return pd.DataFrame(results)
    
    def generate_summary_stats(self, results_df):
        """Generate summary statistics for the classification results."""
        logger.info("Generating summary statistics...")
        
        status_counts = results_df['Status'].value_counts()
        
        # Response time statistics (excluding pending)
        responded_emails = results_df[results_df['Status'] != 'Pending']
        response_times = responded_emails['Response_Time_Business_Minutes'].dropna()
        
        summary = {
            'Total_Inbox_Emails': len(results_df),
            'Replied_Count': status_counts.get('Replied', 0),
            'Completed_Count': status_counts.get('Completed', 0),
            'Pending_Count': status_counts.get('Pending', 0),
            'Reply_Rate_Percent': round((status_counts.get('Replied', 0) / len(results_df)) * 100, 2),
            'Completion_Rate_Percent': round((status_counts.get('Completed', 0) / len(results_df)) * 100, 2),
            'Pending_Rate_Percent': round((status_counts.get('Pending', 0) / len(results_df)) * 100, 2),
            'Avg_Response_Time_Minutes': round(response_times.mean(), 2) if not response_times.empty else None,
            'Median_Response_Time_Minutes': round(response_times.median(), 2) if not response_times.empty else None,
            'Min_Response_Time_Minutes': round(response_times.min(), 2) if not response_times.empty else None,
            'Max_Response_Time_Minutes': round(response_times.max(), 2) if not response_times.empty else None
        }
        
        return summary
    
    def analyze_hourly_distribution(self):
        """Analyze email distribution by hour of the day (0-23)."""
        logger.info("Analyzing hourly email distribution...")
        
        if self.df is None:
            logger.error("Data not loaded. Call load_data() first.")
            return None
            
        # Filter only Inbox emails
        inbox_emails = self.df[self.df['EventType'] == 'Inbox'].copy()
        
        # Extract hour from timestamp
        inbox_emails['Hour'] = inbox_emails['TimeStamp'].dt.hour
        
        # Count emails by hour
        hourly_counts = inbox_emails['Hour'].value_counts().sort_index()
        
        # Create complete 24-hour range (0-23)
        hourly_distribution = pd.DataFrame({
            'Hour': range(24),
            'Email_Count': [hourly_counts.get(hour, 0) for hour in range(24)]
        })
        
        # Add percentage of total
        total_emails = hourly_distribution['Email_Count'].sum()
        hourly_distribution['Percentage'] = round(
            (hourly_distribution['Email_Count'] / total_emails) * 100, 2
        ) if total_emails > 0 else 0
        
        # Add formatted hour labels
        hourly_distribution['Hour_Label'] = hourly_distribution['Hour'].apply(
            lambda x: f"{x:02d}:00"
        )
        
        logger.info(f"Peak email hour: {hourly_distribution.loc[hourly_distribution['Email_Count'].idxmax(), 'Hour_Label']} with {hourly_distribution['Email_Count'].max()} emails")
        logger.info(f"Total emails analyzed: {total_emails}")
        
        return hourly_distribution
    
    def analyze_response_time_by_hour(self, results_df):
        """Analyze average response times by hour of the day."""
        logger.info("Analyzing response times by hour of day...")
        
        if results_df is None or results_df.empty:
            logger.error("No results data provided for hourly response time analysis.")
            return None
            
        # Filter out pending emails (only emails with response times)
        responded_emails = results_df[
            (results_df['Status'] != 'Pending') & 
            (results_df['Response_Time_Business_Minutes'].notna())
        ].copy()
        
        if responded_emails.empty:
            logger.warning("No emails with response times found for hourly analysis.")
            return None
            
        # Extract hour from inbox timestamp
        responded_emails['Inbox_Hour'] = pd.to_datetime(responded_emails['Inbox_TimeStamp']).dt.hour
        
        # Group by hour and calculate statistics
        hourly_response_stats = responded_emails.groupby('Inbox_Hour')['Response_Time_Business_Minutes'].agg([
            'count', 'mean', 'median', 'min', 'max', 'std'
        ]).round(2)
        
        # Reset index to make hour a column
        hourly_response_stats = hourly_response_stats.reset_index()
        
        # Rename columns for clarity
        hourly_response_stats.columns = [
            'Hour', 'Email_Count', 'Avg_Response_Time_Minutes', 'Median_Response_Time_Minutes',
            'Min_Response_Time_Minutes', 'Max_Response_Time_Minutes', 'Std_Response_Time_Minutes'
        ]
        
        # Add formatted hour labels
        hourly_response_stats['Hour_Label'] = hourly_response_stats['Hour'].apply(
            lambda x: f"{x:02d}:00"
        )
        
        # Fill NaN values in standard deviation with 0 (for hours with only 1 email)
        hourly_response_stats['Std_Response_Time_Minutes'] = hourly_response_stats['Std_Response_Time_Minutes'].fillna(0)
        
        # Log insights
        if not hourly_response_stats.empty:
            fastest_hour = hourly_response_stats.loc[hourly_response_stats['Avg_Response_Time_Minutes'].idxmin()]
            slowest_hour = hourly_response_stats.loc[hourly_response_stats['Avg_Response_Time_Minutes'].idxmax()]
    def load_sla_data(self):
        """Load and preprocess the SLA data from UnreadCount.csv."""
        logger.info(f"Loading SLA data from {self.sla_file_path}")
        
        try:
            self.sla_df = pd.read_csv(self.sla_file_path)
            logger.info(f"Loaded {len(self.sla_df)} SLA records")
            
            # Convert date to datetime
            self.sla_df['Date'] = pd.to_datetime(self.sla_df['Date'])
            
            # Convert Hour to integer
            self.sla_df['Hour of the Day'] = pd.to_numeric(self.sla_df['Hour of the Day'])
            
            # Convert TotalUnread to integer
            self.sla_df['TotalUnread'] = pd.to_numeric(self.sla_df['TotalUnread'])
            
            # Add SLA status as boolean (True = SLA MET, False = SLA NOT MET)
            self.sla_df['SLA_Met'] = self.sla_df['Title'] == 'SLA MET'
            
            # Sort by date and hour
            self.sla_df = self.sla_df.sort_values(['Date', 'Hour of the Day'])
            
            logger.info("SLA data preprocessing completed")
            
        except Exception as e:
            logger.error(f"Error loading SLA data: {e}")
            raise
    
    def process_sla_hourly_data(self, date_str):
        """Return a dict of hour -> {unread_count, sla_met} for a given date (YYYY-MM-DD)."""
        if self.sla_df is None or self.sla_df.empty:
            return None
        try:
            target = pd.to_datetime(date_str).date()
        except Exception:
            return None
        df_day = self.sla_df[pd.to_datetime(self.sla_df['Date']).dt.date == target]
        if df_day.empty:
            return {}
        hourly = {}
        for _, row in df_day.iterrows():
            try:
                h = int(row['Hour of the Day'])
            except Exception:
                continue
            unread = int(row['TotalUnread']) if 'TotalUnread' in df_day.columns and not pd.isna(row['TotalUnread']) else None
            sla_val = row['SLA_Met'] if 'SLA_Met' in df_day.columns else None
            sla_met = bool(sla_val) if (sla_val is not None and not pd.isna(sla_val)) else None
            hourly[h] = {
                'unread_count': unread,
                'sla_met': sla_met,
            }
        return hourly

    def calculate_daily_sla_rates(self):
        """Calculate per-day SLA compliance rate (%) and average unread count within business hours/days."""
        if self.sla_df is None or self.sla_df.empty:
            logger.warning("SLA dataframe is empty; cannot compute daily SLA rates")
            return None
        df = self.sla_df.copy()
        # Normalize types
        df['Date'] = pd.to_datetime(df['Date'])
        df['Hour of the Day'] = pd.to_numeric(df['Hour of the Day'], errors='coerce')
        df['TotalUnread'] = pd.to_numeric(df['TotalUnread'], errors='coerce')
        # Filter to configured business hours
        start_h, end_h = self.business_start_hour, self.business_end_hour
        df = df[(df['Hour of the Day'] >= start_h) & (df['Hour of the Day'] <= end_h)]
        # Filter to configured business days of week
        df['weekday'] = df['Date'].dt.weekday
        df = df[df['weekday'].isin(self.business_days)]
        if df.empty:
            logger.warning("No SLA rows remain after filtering by business hours/days")
            return None
        # Compute per-day metrics
        grp = df.groupby(df['Date'].dt.date)
        daily = grp.agg(
            SLA_Compliance_Rate=( 'SLA_Met', lambda s: round(float(s.mean()) * 100, 2) if len(s) else 0.0),
            Avg_Unread_Count=( 'TotalUnread', lambda s: round(float(s.mean()), 2) if len(s) else None),
        ).reset_index().rename(columns={'Date':'date'})
        # Ensure date is datetime for downstream formatting
        daily['date'] = pd.to_datetime(daily['date'])
        daily = daily.sort_values('date')
        logger.info(f"Computed daily SLA rates for {len(daily)} days")
        return daily

    def get_email_dates(self, results_df):
        """Extract unique dates (YYYY-MM-DD) from results_df['Inbox_TimeStamp']."""
        if results_df is None or results_df.empty:
            return []
        dates = pd.to_datetime(results_df['Inbox_TimeStamp']).dt.date.unique().tolist()
        dates = sorted(str(d) for d in dates)
        return dates

    def generate_summary_stats_for_date(self, results_df, date_str):
        """Generate summary stats for a single date using the same schema as generate_summary_stats()."""
        if results_df is None or results_df.empty:
            return None
        try:
            target = pd.to_datetime(date_str).date()
        except Exception:
            return None
        df_day = results_df[pd.to_datetime(results_df['Inbox_TimeStamp']).dt.date == target]
        if df_day.empty:
            return None
        status_counts = df_day['Status'].value_counts()
        total = len(df_day)
        responded = df_day[df_day['Status'] != 'Pending']
        rts = responded['Response_Time_Business_Minutes'].dropna()
        return {
            'Total_Inbox_Emails': total,
            'Replied_Count': int(status_counts.get('Replied', 0)),
            'Completed_Count': int(status_counts.get('Completed', 0)),
            'Pending_Count': int(status_counts.get('Pending', 0)),
            'Reply_Rate_Percent': round((status_counts.get('Replied', 0) / total) * 100, 2) if total > 0 else 0.0,
            'Completion_Rate_Percent': round((status_counts.get('Completed', 0) / total) * 100, 2) if total > 0 else 0.0,
            'Pending_Rate_Percent': round((status_counts.get('Pending', 0) / total) * 100, 2) if total > 0 else 0.0,
            'Avg_Response_Time_Minutes': round(rts.mean(), 2) if not rts.empty else None,
            'Median_Response_Time_Minutes': round(rts.median(), 2) if not rts.empty else None,
            'Min_Response_Time_Minutes': round(rts.min(), 2) if not rts.empty else None,
            'Max_Response_Time_Minutes': round(rts.max(), 2) if not rts.empty else None
        }

    def analyze_hourly_distribution_for_date(self, date_str):
        """Count inbox emails per hour for a specific date; returns DataFrame with Hour and Email_Count."""
        if self.df is None or self.df.empty:
            return None
        try:
            target = pd.to_datetime(date_str).date()
        except Exception:
            return None
        df_inbox = self.df[self.df['EventType'] == 'Inbox'].copy()
        df_inbox = df_inbox[pd.to_datetime(df_inbox['TimeStamp']).dt.date == target]
        if df_inbox.empty:
            # Still return a 24-hour frame with zeros for consistency
            return pd.DataFrame({'Hour': range(24), 'Email_Count': [0]*24})
        df_inbox['Hour'] = pd.to_datetime(df_inbox['TimeStamp']).dt.hour
        hourly_counts = df_inbox['Hour'].value_counts().sort_index()
        dist = pd.DataFrame({'Hour': range(24), 'Email_Count': [int(hourly_counts.get(h, 0)) for h in range(24)]})
        return dist

    def analyze_response_time_by_hour_for_date(self, results_df, date_str):
        """Compute per-hour replied counts and average response times for emails on a date."""
        if results_df is None or results_df.empty:
            return None
        try:
            target = pd.to_datetime(date_str).date()
        except Exception:
            return None
        df = results_df.copy()
        df = df[(df['Status'] != 'Pending') & (df['Response_Time_Business_Minutes'].notna())]
        df = df[pd.to_datetime(df['Inbox_TimeStamp']).dt.date == target]
        if df.empty:
            return pd.DataFrame({'Hour': range(24), 'Email_Count': [0]*24, 'Avg_Response_Time_Minutes': [None]*24})
        df['Inbox_Hour'] = pd.to_datetime(df['Inbox_TimeStamp']).dt.hour
        stats = df.groupby('Inbox_Hour')['Response_Time_Business_Minutes'].agg(['count', 'mean']).reset_index()
        stats = stats.rename(columns={'Inbox_Hour': 'Hour', 'count': 'Email_Count', 'mean': 'Avg_Response_Time_Minutes'})
        # Merge into 0-23 template to ensure all hours present
        template = pd.DataFrame({'Hour': range(24)})
        merged = template.merge(stats, on='Hour', how='left')
        merged['Email_Count'] = merged['Email_Count'].fillna(0).astype(int)
        # Keep Avg_Response_Time_Minutes as float with NaNs (will be interpreted as None in JSON mapping step)
        return merged

    def save_to_unified_json(self, results_df, summary_stats, hourly_distribution, hourly_response_times, 
                            daily_sla_rates, json_file='../../email_database.json'):
        """Save data to unified multi-day JSON database with both email and SLA data (idempotent merge)."""
        json_path = self._resolve_relative_to_script(json_file)
        logger.info(f"Saving to unified database: {json_path}")

        # Sources
        new_sources = []
        if self.sla_df is not None:
            new_sources.append("UnreadCount.csv")
        if getattr(self, 'loaded_event_files', None):
            new_sources.extend(self.loaded_event_files)

        # Load existing
        existing_db = {}
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    existing_db = json.load(f)
                logger.info("Loaded existing database for merge")
            except Exception as e:
                logger.warning(f"Failed reading existing DB, starting fresh: {e}")

        days = existing_db.get('days', {})
        metadata = existing_db.get('metadata', {})
        data_sources = set(metadata.get('data_sources', [])) | set(new_sources)

        # Ensure day helper
        def ensure_day(date_str):
            if date_str not in days:
                days[date_str] = {
                    "date": date_str,
                    "has_sla_data": False,
                    "has_email_data": False,
                    "daily_summary": {
                        "sla_compliance_rate": None,
                        "avg_unread_count": None,
                        "total_emails": None,
                        "reply_rate_percent": None,
                        "avg_response_time_minutes": None,
                        "median_response_time_minutes": None
                    },
                    "hourly_data": [
                        {
                            "hour": h,
                            "unread_count": None,
                            "sla_met": None,
                            "emails_received": 0,
                            "emails_replied": 0,
                            "avg_response_time": None
                        } for h in range(24)
                    ]
                }
            # normalize to 24 hours
            if len(days[date_str].get("hourly_data", [])) != 24:
                existing = {e.get("hour", i): e for i, e in enumerate(days[date_str].get("hourly_data", []))}
                days[date_str]["hourly_data"] = [existing.get(h, {
                    "hour": h,
                    "unread_count": None,
                    "sla_met": None,
                    "emails_received": 0,
                    "emails_replied": 0,
                    "avg_response_time": None
                }) for h in range(24)]
            return days[date_str]

        # Merge SLA days
        if daily_sla_rates is not None and not daily_sla_rates.empty:
            for _, drow in daily_sla_rates.iterrows():
                dstr = drow['date'].strftime('%Y-%m-%d')
                day = ensure_day(dstr)
                day["has_sla_data"] = True
                day["daily_summary"]["sla_compliance_rate"] = drow['SLA_Compliance_Rate']
                day["daily_summary"]["avg_unread_count"] = drow['Avg_Unread_Count']
                hourly_sla = self.process_sla_hourly_data(dstr) or {}
                for h in range(24):
                    s = hourly_sla.get(h, {})
                    day["hourly_data"][h]["unread_count"] = s.get('unread_count')
                    day["hourly_data"][h]["sla_met"] = s.get('sla_met')

        # Merge Email days
        if results_df is not None and not results_df.empty:
            for dstr in self.get_email_dates(results_df):
                day = ensure_day(dstr)
                day["has_email_data"] = True
                # summaries
                dsum = self.generate_summary_stats_for_date(results_df, dstr)
                if dsum:
                    day["daily_summary"].update({
                        "total_emails": dsum['Total_Inbox_Emails'],
                        "reply_rate_percent": dsum['Reply_Rate_Percent'],
                        "avg_response_time_minutes": dsum['Avg_Response_Time_Minutes'],
                        "median_response_time_minutes": dsum['Median_Response_Time_Minutes']
                    })
                # hourly
                dist = self.analyze_hourly_distribution_for_date(dstr)
                resp = self.analyze_response_time_by_hour_for_date(results_df, dstr)
                dist_map = {int(r['Hour']): int(r.get('Email_Count', 0)) for r in (dist.to_dict('records') if dist is not None else [])}
                resp_map = {int(r['Hour']): {'count': int(r.get('Email_Count', 0)), 'avg': r.get('Avg_Response_Time_Minutes')} for r in (resp.to_dict('records') if resp is not None else [])}
                for h in range(24):
                    day["hourly_data"][h]["emails_received"] = dist_map.get(h, 0)
                    rinfo = resp_map.get(h)
                    day["hourly_data"][h]["emails_replied"] = rinfo['count'] if rinfo else 0
                    avg_val = rinfo.get('avg') if rinfo else None
                    # Normalize NaN to None for JSON safety
                    if avg_val is not None and not pd.isna(avg_val):
                        avg_rt = float(avg_val)
                    else:
                        avg_rt = None
                    day["hourly_data"][h]["avg_response_time"] = avg_rt

        # Metadata
        all_dates = sorted(days.keys())
        earliest_date = all_dates[0] if all_dates else None
        latest_date = all_dates[-1] if all_dates else None

        database = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_days_processed": len(days),
                "data_sources": sorted(list(data_sources)),
                "earliest_date": earliest_date,
                "latest_date": latest_date
            },
            "days": days
        }

        with open(json_path, 'w') as f:
            json.dump(database, f, indent=2, default=str)

        logger.info(f"Unified database saved to {json_file}")
        logger.info(f"Database contains {len(days)} days from {earliest_date} to {latest_date}")

        if summary_stats:
            logger.info("=== EMAIL CLASSIFICATION SUMMARY (overall) ===")
            for k, v in summary_stats.items():
                logger.info(f"{k}: {v}")
        if daily_sla_rates is not None:
            logger.info("=== SLA SUMMARY ===")
            try:
                avg_sla_rate = daily_sla_rates['SLA_Compliance_Rate'].mean()
                logger.info(f"Average SLA Compliance Rate: {avg_sla_rate:.2f}%")
            except Exception:
                pass
            logger.info(f"SLA data days: {len(daily_sla_rates) if daily_sla_rates is not None else 0}")
    
    def run(self):
        """Execute the complete email classification process."""
        logger.info("Starting email classification process...")
        
        # Load and preprocess data
        self.load_data()
        
        # Process conversations and classify emails
        results_df = self.process_conversations()
        
        # Generate summary statistics
        summary_stats = self.generate_summary_stats(results_df)
        
        # Analyze hourly distribution
        hourly_distribution = self.analyze_hourly_distribution()
        
        # Analyze response times by hour
        hourly_response_times = self.analyze_response_time_by_hour(results_df)
        
        # Load and process SLA data
        self.load_sla_data()
        daily_sla_rates = self.calculate_daily_sla_rates()
        
        # Save all data to unified multi-day JSON database
        self.save_to_unified_json(results_df, summary_stats, hourly_distribution, hourly_response_times, daily_sla_rates)
        
        logger.info("Email classification process completed successfully!")
        
        return results_df, summary_stats, hourly_distribution, hourly_response_times


def main():
    """Main function to run the email classifier."""
    classifier = EmailClassifier()
    results, summary, hourly_dist, hourly_response = classifier.run()
    return results, summary, hourly_dist, hourly_response


if __name__ == "__main__":
    main()