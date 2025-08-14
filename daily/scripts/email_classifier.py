#!/usr/bin/env python3
"""
Email Classification and SLA Compliance Calculator

This script processes two data sources to create a unified JSON database:
1. Complete_List_Raw.csv: Email lifecycle events and response time analysis
2. UnreadCount.csv: SLA compliance data with hourly unread counts

Features:
- Email classification (Replied, Completed, Pending)
- Business hours response time calculations (7 AM - 6 PM, Monday-Friday)
- Daily SLA compliance rate calculations (≤30 emails = SLA MET)
- Multi-day unified JSON database with both email and SLA metrics
- Dashboard-ready data structure for KPI generation

Business Hours: Monday-Friday, 7:00 AM - 6:00 PM
SLA Threshold: 30 unread emails
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailClassifier:
    """Main class for processing and classifying email data."""
    
    def __init__(self, csv_file_path='../../data/Complete_List_Raw.csv', sla_file_path='../../data/UnreadCount.csv'):
        """Initialize the classifier with data file paths."""
        self.csv_file_path = csv_file_path
        self.sla_file_path = sla_file_path
        self.df = None
        self.sla_df = None
        
        # Business hours configuration
        self.business_start_hour = 7  # 7 AM
        self.business_end_hour = 18   # 6 PM
        self.business_days = [0, 1, 2, 3, 4]  # Monday=0 to Friday=4
        
    def load_data(self):
        """Load and preprocess the CSV data."""
        logger.info(f"Loading data from {self.csv_file_path}")
        
        try:
            self.df = pd.read_csv(self.csv_file_path)
            logger.info(f"Loaded {len(self.df)} records")
            
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
        Only counts time during business hours (7 AM - 6 PM, Monday-Friday).
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
            
            logger.info(f"Fastest response hour: {fastest_hour['Hour_Label']} with {fastest_hour['Avg_Response_Time_Minutes']:.1f} min average")
            logger.info(f"Slowest response hour: {slowest_hour['Hour_Label']} with {slowest_hour['Avg_Response_Time_Minutes']:.1f} min average")
            logger.info(f"Total emails with response times: {responded_emails.shape[0]}")
        
        return hourly_response_stats
    
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
    
    def calculate_daily_sla_rates(self):
        """Calculate daily SLA compliance rates from hourly data."""
        if self.sla_df is None:
            logger.error("SLA data not loaded. Call load_sla_data() first.")
            return None
            
        logger.info("Calculating daily SLA compliance rates...")
        
        # Group by date and calculate SLA compliance rate
        daily_sla = self.sla_df.groupby(self.sla_df['Date'].dt.date).agg({
            'SLA_Met': 'mean',  # Percentage of hours that met SLA
            'TotalUnread': 'mean',  # Average unread count for the day
            'Hour of the Day': 'count'  # Number of measurements per day
        }).reset_index()
        
        # Convert to percentage and round
        daily_sla['SLA_Compliance_Rate'] = round(daily_sla['SLA_Met'] * 100, 2)
        daily_sla['Avg_Unread_Count'] = round(daily_sla['TotalUnread'], 1)
        
        # Rename columns for clarity
        daily_sla = daily_sla.rename(columns={
            'Date': 'date',
            'Hour of the Day': 'hourly_measurements'
        })
        
        logger.info(f"Calculated SLA rates for {len(daily_sla)} days")
        return daily_sla
    
    def process_sla_hourly_data(self, target_date):
        """Process hourly SLA data for a specific date."""
        if self.sla_df is None:
            return None
            
        # Filter data for the target date
        target_date_obj = pd.to_datetime(target_date).date()
        day_sla_data = self.sla_df[self.sla_df['Date'].dt.date == target_date_obj]
        
        if day_sla_data.empty:
            return None
            
        # Create hourly data structure
        hourly_sla_data = {}
        for _, row in day_sla_data.iterrows():
            hour = int(row['Hour of the Day'])
            hourly_sla_data[hour] = {
                'unread_count': int(row['TotalUnread']),
                'sla_met': bool(row['SLA_Met'])
            }
            
        return hourly_sla_data
    
    def save_to_unified_json(self, results_df, summary_stats, hourly_distribution, hourly_response_times, 
                            daily_sla_rates, json_file='../../email_database.json'):
        """Save data to unified multi-day JSON database with both email and SLA data."""
        logger.info(f"Saving to unified database: {json_file}")
        
        # Collect all data sources
        data_sources = []
        if self.sla_df is not None:
            data_sources.append("UnreadCount.csv")
        if results_df is not None:
            data_sources.append("Complete_List_Raw.csv")
        
        # Initialize days dictionary
        days = {}
        earliest_date = None
        latest_date = None
        
        # Process SLA data days
        if daily_sla_rates is not None:
            for _, day_row in daily_sla_rates.iterrows():
                date_str = day_row['date'].strftime('%Y-%m-%d')
                
                # Update date range
                if earliest_date is None or date_str < earliest_date:
                    earliest_date = date_str
                if latest_date is None or date_str > latest_date:
                    latest_date = date_str
                
                # Get hourly SLA data for this day
                hourly_sla_data = self.process_sla_hourly_data(date_str)
                
                # Create hourly data array (0-23 hours)
                hourly_data = []
                for hour in range(24):
                    sla_data = hourly_sla_data.get(hour, {}) if hourly_sla_data else {}
                    
                    hourly_entry = {
                        "hour": hour,
                        "unread_count": sla_data.get('unread_count'),
                        "sla_met": sla_data.get('sla_met'),
                        "emails_received": None,
                        "emails_replied": None,
                        "avg_response_time": None
                    }
                    hourly_data.append(hourly_entry)
                
                # Create day entry
                days[date_str] = {
                    "date": date_str,
                    "has_sla_data": True,
                    "has_email_data": False,
                    "daily_summary": {
                        "sla_compliance_rate": day_row['SLA_Compliance_Rate'],
                        "avg_unread_count": day_row['Avg_Unread_Count'],
                        "total_emails": None,
                        "reply_rate_percent": None,
                        "avg_response_time_minutes": None,
                        "median_response_time_minutes": None
                    },
                    "hourly_data": hourly_data
                }
        
        # Process email data (single day: 2025-08-13)
        if results_df is not None:
            email_date_str = "2025-08-13"
            
            # Update date range
            if earliest_date is None or email_date_str < earliest_date:
                earliest_date = email_date_str
            if latest_date is None or email_date_str > latest_date:
                latest_date = email_date_str
            
            # Prepare email hourly data
            hourly_dist_dict = {}
            hourly_response_dict = {}
            
            # Convert hourly distribution to dict by hour
            if hourly_distribution is not None:
                for row in hourly_distribution.to_dict('records'):
                    hourly_dist_dict[row['Hour']] = row
            
            # Convert hourly response times to dict by hour
            if hourly_response_times is not None:
                for row in hourly_response_times.to_dict('records'):
                    hourly_response_dict[row['Hour']] = row
            
            # Check if this day already exists (has SLA data)
            if email_date_str in days:
                # Merge with existing SLA data
                existing_day = days[email_date_str]
                existing_day["has_email_data"] = True
                
                # Update daily summary with email data
                existing_day["daily_summary"].update({
                    "total_emails": summary_stats['Total_Inbox_Emails'],
                    "reply_rate_percent": summary_stats['Reply_Rate_Percent'],
                    "avg_response_time_minutes": summary_stats['Avg_Response_Time_Minutes'],
                    "median_response_time_minutes": summary_stats['Median_Response_Time_Minutes']
                })
                
                # Update hourly data with email metrics
                for hour_entry in existing_day["hourly_data"]:
                    hour = hour_entry["hour"]
                    dist_data = hourly_dist_dict.get(hour, {})
                    response_data = hourly_response_dict.get(hour, {})
                    
                    hour_entry["emails_received"] = dist_data.get('Email_Count', 0)
                    hour_entry["emails_replied"] = response_data.get('Email_Count', 0) if hour in hourly_response_dict else 0
                    hour_entry["avg_response_time"] = response_data.get('Avg_Response_Time_Minutes') if response_data.get('Avg_Response_Time_Minutes', 0) > 0 else None
            
            else:
                # Create new day entry with email data only
                hourly_data = []
                for hour in range(24):
                    dist_data = hourly_dist_dict.get(hour, {})
                    response_data = hourly_response_dict.get(hour, {})
                    
                    hourly_entry = {
                        "hour": hour,
                        "unread_count": None,
                        "sla_met": None,
                        "emails_received": dist_data.get('Email_Count', 0),
                        "emails_replied": response_data.get('Email_Count', 0) if hour in hourly_response_dict else 0,
                        "avg_response_time": response_data.get('Avg_Response_Time_Minutes') if response_data.get('Avg_Response_Time_Minutes', 0) > 0 else None
                    }
                    hourly_data.append(hourly_entry)
                
                days[email_date_str] = {
                    "date": email_date_str,
                    "has_sla_data": False,
                    "has_email_data": True,
                    "daily_summary": {
                        "sla_compliance_rate": None,
                        "avg_unread_count": None,
                        "total_emails": summary_stats['Total_Inbox_Emails'],
                        "reply_rate_percent": summary_stats['Reply_Rate_Percent'],
                        "avg_response_time_minutes": summary_stats['Avg_Response_Time_Minutes'],
                        "median_response_time_minutes": summary_stats['Median_Response_Time_Minutes']
                    },
                    "hourly_data": hourly_data
                }
        
        # Create unified database structure
        database = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_days_processed": len(days),
                "data_sources": data_sources,
                "earliest_date": earliest_date,
                "latest_date": latest_date
            },
            "days": days
        }
        
        # Save to JSON
        with open(json_file, 'w') as f:
            json.dump(database, f, indent=2, default=str)
        
        logger.info(f"Unified database saved to {json_file}")
        logger.info(f"Database contains {len(days)} days from {earliest_date} to {latest_date}")
        
        # Log summary to console
        if summary_stats:
            logger.info("=== EMAIL CLASSIFICATION SUMMARY ===")
            for key, value in summary_stats.items():
                logger.info(f"{key}: {value}")
        
        if daily_sla_rates is not None:
            logger.info("=== SLA SUMMARY ===")
            avg_sla_rate = daily_sla_rates['SLA_Compliance_Rate'].mean()
            logger.info(f"Average SLA Compliance Rate: {avg_sla_rate:.2f}%")
            logger.info(f"SLA data days: {len(daily_sla_rates)}")
    
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