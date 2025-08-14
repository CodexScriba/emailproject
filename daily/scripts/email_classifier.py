#!/usr/bin/env python3
"""
Email Classification and Response Time Calculator

This script processes the Complete_List_Raw.csv file to:
1. Match Inbox emails with their corresponding Replied or Completed events
2. Calculate response times in business minutes
3. Classify emails as Replied, Completed, or Pending
4. Generate a comprehensive output file with all classifications

Business Hours: Monday-Friday, 7:00 AM - 6:00 PM
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
    
    def __init__(self, csv_file_path='../../data/Complete_List_Raw.csv'):
        """Initialize the classifier with data file path."""
        self.csv_file_path = csv_file_path
        self.df = None
        
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
    
    def save_to_unified_json(self, results_df, summary_stats, hourly_distribution, hourly_response_times, 
                            json_file='../../email_database.json'):
        """Save data to unified multi-day JSON database."""
        logger.info(f"Saving to unified database: {json_file}")
        
        # Extract the date from the data (assuming single day for now)
        date_str = "2025-08-13"  # From Complete_List_Raw.csv
        
        # Merge hourly distribution with response times
        hourly_data = []
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
        
        # Create unified hourly data (0-23 hours)
        for hour in range(24):
            dist_data = hourly_dist_dict.get(hour, {})
            response_data = hourly_response_dict.get(hour, {})
            
            # Count replied emails for this hour
            emails_replied = 0
            if hour in hourly_response_dict:
                emails_replied = response_data.get('Email_Count', 0)
            
            hourly_entry = {
                "hour": hour,
                "unread_count": None,  # Will be populated when SLA data is added
                "sla_met": None,      # Will be populated when SLA data is added
                "emails_received": dist_data.get('Email_Count', 0),
                "emails_replied": emails_replied,
                "avg_response_time": response_data.get('Avg_Response_Time_Minutes') if response_data.get('Avg_Response_Time_Minutes', 0) > 0 else None
            }
            hourly_data.append(hourly_entry)
        
        # Create unified database structure
        database = {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_days_processed": 1,
                "data_sources": ["Complete_List_Raw.csv"],
                "earliest_date": date_str,
                "latest_date": date_str
            },
            "days": {
                date_str: {
                    "date": date_str,
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
            }
        }
        
        # Save to JSON
        with open(json_file, 'w') as f:
            json.dump(database, f, indent=2, default=str)
        
        logger.info(f"Unified database saved to {json_file}")
        
        # Log summary to console
        logger.info("=== CLASSIFICATION SUMMARY ===")
        for key, value in summary_stats.items():
            logger.info(f"{key}: {value}")
    
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
        
        # Save all data to unified multi-day JSON database
        self.save_to_unified_json(results_df, summary_stats, hourly_distribution, hourly_response_times)
        
        logger.info("Email classification process completed successfully!")
        
        return results_df, summary_stats, hourly_distribution, hourly_response_times


def main():
    """Main function to run the email classifier."""
    classifier = EmailClassifier()
    results, summary, hourly_dist, hourly_response = classifier.run()
    return results, summary, hourly_dist, hourly_response


if __name__ == "__main__":
    main()