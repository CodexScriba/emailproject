#!/usr/bin/env python3
"""
Intelligent Email Data Ingestion and Update System

This script processes Complete_List_Raw.csv and UnreadCount.csv files from the ingest folder,
intelligently updates the email_database.json with complete conversation tracking,
and automatically creates timestamped backups.

Key Features:
- Processes entire files to capture cross-day conversations
- Merges new data with existing database intelligently
- Handles conversation updates across multiple days
- Creates automatic backups with timestamps
- Preserves historical data while updating with new information
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import shutil
from pathlib import Path
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntelligentIngester:
    """Handles intelligent ingestion and merging of email data."""
    
    def __init__(self):
        """Initialize the ingester with paths."""
        # Set up paths relative to script location
        self.script_dir = Path(__file__).resolve().parent
        self.project_root = self.script_dir.parent.parent
        
        # Data paths
        self.ingest_dir = self.project_root / 'data' / 'ingest'
        self.backup_dir = self.project_root / 'data' / 'backup'
        self.database_path = self.project_root / 'database' / 'email_database.json'
        self.config_path = self.project_root / 'config' / 'sla_config.json'
        
        # Input files
        self.complete_list_path = self.ingest_dir / 'Complete_List_Raw.csv'
        self.unread_count_path = self.ingest_dir / 'UnreadCount.csv'
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Track processed conversations for deduplication
        self.processed_conversations = {}
        
    def load_config(self):
        """Load SLA configuration."""
        try:
            with open(self.config_path, 'r') as f:
                self.sla_config = json.load(f)
            self.business_start_hour = self.sla_config['sla_thresholds']['business_hours']['start_hour']
            self.business_end_hour = self.sla_config['sla_thresholds']['business_hours']['end_hour']
            self.business_days = self.sla_config['sla_thresholds']['business_hours']['business_days']
            self.unread_threshold = self.sla_config['sla_thresholds']['unread_email_threshold']
            logger.info(f"Loaded SLA config: Business hours {self.business_start_hour}:00-{self.business_end_hour}:00")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            # Use defaults
            self.business_start_hour = 7
            self.business_end_hour = 21
            self.business_days = [0, 1, 2, 3, 4, 5, 6]
            self.unread_threshold = 30
            
    def create_backup(self, file_path, backup_name_prefix):
        """Create a timestamped backup of a file."""
        if not Path(file_path).exists():
            return None
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{backup_name_prefix}_{timestamp}{Path(file_path).suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
            
    def load_existing_database(self):
        """Load existing database or create new structure."""
        if self.database_path.exists():
            try:
                with open(self.database_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading existing database: {e}")
                # Create backup of corrupted file
                self.create_backup(self.database_path, 'email_database_corrupted')
                
        # Return new database structure
        return {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_days_processed": 0,
                "data_sources": [],
                "earliest_date": None,
                "latest_date": None
            },
            "days": {}
        }
        
    def calculate_business_minutes(self, start_time, end_time):
        """Calculate business minutes between two timestamps."""
        if pd.isna(start_time) or pd.isna(end_time):
            return None
            
        if end_time <= start_time:
            return 0
            
        total_minutes = 0
        current_time = start_time
        
        while current_time < end_time:
            if current_time.weekday() in self.business_days:
                day_start = current_time.replace(hour=self.business_start_hour, minute=0, second=0, microsecond=0)
                day_end = current_time.replace(hour=self.business_end_hour, minute=0, second=0, microsecond=0)
                
                period_start = max(current_time, day_start)
                period_end = min(end_time, day_end)
                
                if period_start < period_end:
                    minutes_in_period = (period_end - period_start).total_seconds() / 60
                    total_minutes += minutes_in_period
            
            current_time = (current_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        return round(total_minutes, 2)
        
    def process_email_events(self):
        """Process Complete_List_Raw.csv with full conversation tracking."""
        if not self.complete_list_path.exists():
            logger.warning(f"Complete_List_Raw.csv not found at {self.complete_list_path}")
            return None
            
        logger.info("Processing email events from Complete_List_Raw.csv")
        
        # Load the CSV
        df = pd.read_csv(self.complete_list_path)
        df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
        
        # Sort by conversation and timestamp
        df = df.sort_values(['Conversation-Id', 'TimeStamp'])
        
        # Track all conversations and their events
        conversations = {}
        
        for _, row in df.iterrows():
            conv_id = row['Conversation-Id']
            if conv_id not in conversations:
                conversations[conv_id] = {
                    'inbox_events': [],
                    'reply_events': [],
                    'completed_events': []
                }
            
            event_type = row['EventType']
            event_data = {
                'timestamp': row['TimeStamp'],
                'subject': row['Subject'],
                'emails': row['Emails'],
                'message_id': row['MessageId']
            }
            
            if event_type == 'Inbox':
                conversations[conv_id]['inbox_events'].append(event_data)
            elif event_type == 'Replied':
                conversations[conv_id]['reply_events'].append(event_data)
            elif event_type == 'Completed':
                conversations[conv_id]['completed_events'].append(event_data)
                
        # Process conversations to create email records
        email_records = []
        
        for conv_id, events in conversations.items():
            for inbox_event in events['inbox_events']:
                # Find the matching reply or completed event
                status = 'Pending'
                response_event = None
                response_time = None
                
                # Check for replies first
                for reply in events['reply_events']:
                    if reply['timestamp'] > inbox_event['timestamp']:
                        status = 'Replied'
                        response_event = reply
                        break
                
                # If no reply, check for completed
                if status == 'Pending':
                    for completed in events['completed_events']:
                        if completed['timestamp'] > inbox_event['timestamp']:
                            status = 'Completed'
                            response_event = completed
                            break
                
                # Calculate response time if we have a response
                if response_event:
                    response_time = self.calculate_business_minutes(
                        inbox_event['timestamp'],
                        response_event['timestamp']
                    )
                
                email_records.append({
                    'conversation_id': conv_id,
                    'inbox_timestamp': inbox_event['timestamp'],
                    'inbox_subject': inbox_event['subject'],
                    'inbox_emails': inbox_event['emails'],
                    'inbox_message_id': inbox_event['message_id'],
                    'status': status,
                    'response_timestamp': response_event['timestamp'] if response_event else None,
                    'response_time_minutes': response_time
                })
        
        logger.info(f"Processed {len(email_records)} email records from {len(conversations)} conversations")
        return pd.DataFrame(email_records)
        
    def process_sla_data(self):
        """Process UnreadCount.csv for SLA compliance data."""
        if not self.unread_count_path.exists():
            logger.warning(f"UnreadCount.csv not found at {self.unread_count_path}")
            return None
            
        logger.info("Processing SLA data from UnreadCount.csv")
        
        # Load the CSV
        df = pd.read_csv(self.unread_count_path)
        
        # Handle different possible column names
        if 'Unread Count' in df.columns:
            df['TotalUnread'] = df['Unread Count']
        
        # Handle different hour column names
        if 'Hour of the Day' in df.columns:
            df['Hour'] = df['Hour of the Day']
        elif 'Hour' not in df.columns:
            logger.error("No hour column found in UnreadCount.csv")
            return None
        
        # Convert date/time columns
        df['Date'] = pd.to_datetime(df['Date'])
        df['Hour'] = pd.to_numeric(df['Hour'])
        
        # Calculate SLA compliance
        df['SLA_Met'] = df['TotalUnread'] <= self.unread_threshold
        
        logger.info(f"Processed {len(df)} SLA records")
        return df
        
    def merge_with_existing(self, existing_db, email_df, sla_df):
        """Intelligently merge new data with existing database."""
        logger.info("Merging new data with existing database")
        
        # Update metadata
        existing_db['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Process email data by date
        if email_df is not None and not email_df.empty:
            for date in email_df['inbox_timestamp'].dt.date.unique():
                date_str = str(date)
                
                # Get emails for this date
                day_emails = email_df[email_df['inbox_timestamp'].dt.date == date]
                
                # Initialize or update day entry
                if date_str not in existing_db['days']:
                    existing_db['days'][date_str] = {
                        'date': date_str,
                        'has_email_data': True,
                        'has_sla_data': False,
                        'daily_summary': {},
                        'hourly_data': [{'hour': h} for h in range(24)]
                    }
                else:
                    existing_db['days'][date_str]['has_email_data'] = True
                
                # Calculate daily summary
                total_emails = len(day_emails)
                replied = len(day_emails[day_emails['status'] == 'Replied'])
                completed = len(day_emails[day_emails['status'] == 'Completed'])
                
                response_times = day_emails[day_emails['response_time_minutes'].notna()]['response_time_minutes']
                
                existing_db['days'][date_str]['daily_summary'].update({
                    'total_emails': total_emails,
                    'replied_count': replied,
                    'completed_count': completed,
                    'pending_count': total_emails - replied - completed,
                    'reply_rate_percent': round((replied / total_emails * 100) if total_emails > 0 else 0, 1),
                    'avg_response_time_minutes': round(response_times.mean(), 1) if not response_times.empty else None,
                    'median_response_time_minutes': round(response_times.median(), 1) if not response_times.empty else None
                })
                
                # Calculate hourly data
                for hour in range(24):
                    hour_emails = day_emails[day_emails['inbox_timestamp'].dt.hour == hour]
                    hour_replied = hour_emails[hour_emails['status'] == 'Replied']
                    
                    hour_response_times = hour_emails[hour_emails['response_time_minutes'].notna()]['response_time_minutes']
                    
                    # Find or create hour entry
                    hour_entry = next((h for h in existing_db['days'][date_str]['hourly_data'] if h.get('hour') == hour), None)
                    if not hour_entry:
                        hour_entry = {'hour': hour}
                        existing_db['days'][date_str]['hourly_data'].append(hour_entry)
                    
                    hour_entry.update({
                        'emails_received': len(hour_emails),
                        'emails_replied': len(hour_replied),
                        'avg_response_time': round(hour_response_times.mean(), 1) if not hour_response_times.empty else None
                    })
        
        # Process SLA data
        if sla_df is not None and not sla_df.empty:
            for date in sla_df['Date'].dt.date.unique():
                date_str = str(date)
                
                # Get SLA data for this date
                day_sla = sla_df[sla_df['Date'].dt.date == date]
                
                # Initialize day entry if needed
                if date_str not in existing_db['days']:
                    existing_db['days'][date_str] = {
                        'date': date_str,
                        'has_email_data': False,
                        'has_sla_data': True,
                        'daily_summary': {},
                        'hourly_data': [{'hour': h} for h in range(24)]
                    }
                else:
                    existing_db['days'][date_str]['has_sla_data'] = True
                
                # Calculate daily SLA summary
                business_hours_sla = day_sla[
                    (day_sla['Hour'] >= self.business_start_hour) & 
                    (day_sla['Hour'] < self.business_end_hour)
                ]
                
                if not business_hours_sla.empty:
                    sla_compliance = (business_hours_sla['SLA_Met'].sum() / len(business_hours_sla)) * 100
                    avg_unread = business_hours_sla['TotalUnread'].mean()
                    
                    existing_db['days'][date_str]['daily_summary'].update({
                        'sla_compliance_rate': round(sla_compliance, 1),
                        'avg_unread_count': round(avg_unread, 1)
                    })
                
                # Update hourly SLA data
                for _, row in day_sla.iterrows():
                    hour = int(row['Hour'])
                    
                    # Find or create hour entry
                    hour_entry = next((h for h in existing_db['days'][date_str]['hourly_data'] if h.get('hour') == hour), None)
                    if not hour_entry:
                        hour_entry = {'hour': hour}
                        existing_db['days'][date_str]['hourly_data'].append(hour_entry)
                    
                    hour_entry.update({
                        'unread_count': int(row['TotalUnread']),
                        'sla_met': bool(row['SLA_Met'])
                    })
        
        # Sort hourly data
        for date_str in existing_db['days']:
            existing_db['days'][date_str]['hourly_data'] = sorted(
                existing_db['days'][date_str]['hourly_data'],
                key=lambda x: x.get('hour', 0)
            )
        
        # Update metadata
        all_dates = list(existing_db['days'].keys())
        if all_dates:
            existing_db['metadata']['earliest_date'] = min(all_dates)
            existing_db['metadata']['latest_date'] = max(all_dates)
            existing_db['metadata']['total_days_processed'] = len(all_dates)
        
        # Update data sources
        existing_db['metadata']['data_sources'] = ['Complete_List_Raw.csv', 'UnreadCount.csv']
        
        logger.info(f"Database now contains {len(all_dates)} days of data")
        return existing_db
        
    def save_database(self, database):
        """Save the updated database to JSON."""
        try:
            with open(self.database_path, 'w') as f:
                json.dump(database, f, indent=2, default=str)
            logger.info(f"Successfully saved database to {self.database_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save database: {e}")
            return False
            
    def run(self):
        """Main execution method."""
        logger.info("=" * 60)
        logger.info("Starting Intelligent Email Data Ingestion")
        logger.info("=" * 60)
        
        # Check if input files exist
        if not self.complete_list_path.exists() and not self.unread_count_path.exists():
            logger.error("No input files found in ingest folder!")
            logger.info(f"Please place Complete_List_Raw.csv and/or UnreadCount.csv in {self.ingest_dir}")
            return False
        
        # Create backups of existing files
        if self.database_path.exists():
            self.create_backup(self.database_path, 'email_database')
        
        if self.complete_list_path.exists():
            self.create_backup(self.complete_list_path, 'Complete_List_Raw')
        
        if self.unread_count_path.exists():
            self.create_backup(self.unread_count_path, 'UnreadCount')
        
        # Load existing database
        database = self.load_existing_database()
        
        # Process new data
        email_df = self.process_email_events()
        sla_df = self.process_sla_data()
        
        # Merge with existing data
        updated_db = self.merge_with_existing(database, email_df, sla_df)
        
        # Save updated database
        if self.save_database(updated_db):
            logger.info("=" * 60)
            logger.info("Ingestion completed successfully!")
            logger.info(f"Database contains {updated_db['metadata']['total_days_processed']} days")
            logger.info(f"Date range: {updated_db['metadata']['earliest_date']} to {updated_db['metadata']['latest_date']}")
            logger.info("=" * 60)
            
            # Optional: Move processed files to backup
            if self.complete_list_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                processed_path = self.backup_dir / f"Complete_List_Raw_processed_{timestamp}.csv"
                shutil.move(str(self.complete_list_path), str(processed_path))
                logger.info(f"Moved processed file to {processed_path}")
            
            if self.unread_count_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                processed_path = self.backup_dir / f"UnreadCount_processed_{timestamp}.csv"
                shutil.move(str(self.unread_count_path), str(processed_path))
                logger.info(f"Moved processed file to {processed_path}")
            
            return True
        
        return False


if __name__ == "__main__":
    ingester = IntelligentIngester()
    success = ingester.run()
    exit(0 if success else 1)
