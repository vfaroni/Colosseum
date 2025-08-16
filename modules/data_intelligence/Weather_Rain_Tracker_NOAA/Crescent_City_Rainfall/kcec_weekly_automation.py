#!/usr/bin/env python3
"""
KCEC Weekly Weather Data Automation
Automatically downloads and organizes weather data every week
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time

# Import our scrapers
from kcec_weather_downloader import KCECWeatherDownloader
from kcec_realtime_scraper import KCECRealtimeScraper

class KCECWeeklyAutomation:
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
        self.data_dir = self.config.get("data_dir", "weather_data")
        self.archive_dir = os.path.join(self.data_dir, "archive")
        self.current_dir = os.path.join(self.data_dir, "current")
        
        # Create directories
        os.makedirs(self.archive_dir, exist_ok=True)
        os.makedirs(self.current_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            filename=os.path.join(self.data_dir, "automation.log"),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize scrapers
        self.noaa_downloader = KCECWeatherDownloader(self.current_dir)
        self.realtime_scraper = KCECRealtimeScraper(self.current_dir)
        
        # Set NOAA token if provided
        if "noaa_token" in self.config:
            self.noaa_downloader.set_noaa_token(self.config["noaa_token"])
            
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "data_dir": "weather_data",
                "noaa_token": "YOUR_NOAA_TOKEN_HERE",
                "email_notifications": False,
                "email_to": "your-email@example.com",
                "email_from": "weather-bot@example.com",
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": ""
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default config file: {config_file}")
            print("Please edit this file with your settings.")
            return default_config
            
    def collect_weekly_data(self):
        """Main function to collect all weather data"""
        logging.info("Starting weekly data collection")
        
        success = True
        report = []
        
        try:
            # 1. Download NOAA historical data for the past week
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            logging.info(f"Downloading NOAA data from {start_date.date()} to {end_date.date()}")
            historical_df = self.noaa_downloader.download_noaa_historical(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            if historical_df is not None:
                report.append(f"✓ Downloaded {len(historical_df)} days of NOAA historical data")
            else:
                report.append("✗ Failed to download NOAA historical data")
                success = False
                
        except Exception as e:
            logging.error(f"Error downloading NOAA data: {e}")
            report.append(f"✗ NOAA download error: {e}")
            success = False
            
        try:
            # 2. Scrape real-time data
            logging.info("Scraping real-time weather data")
            realtime_df = self.realtime_scraper.scrape_with_requests()
            
            if realtime_df is not None:
                report.append(f"✓ Scraped {len(realtime_df)} real-time observations")
            else:
                report.append("✗ Failed to scrape real-time data")
                success = False
                
        except Exception as e:
            logging.error(f"Error scraping real-time data: {e}")
            report.append(f"✗ Real-time scraping error: {e}")
            success = False
            
        # 3. Archive old files
        self.archive_old_files()
        
        # 4. Create summary report
        self.create_summary_report()
        
        # 5. Send notification if configured
        if self.config.get("email_notifications", False):
            self.send_email_notification(report, success)
            
        logging.info("Weekly data collection completed")
        return success
        
    def archive_old_files(self):
        """Move files older than 30 days to archive"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for filename in os.listdir(self.current_dir):
            filepath = os.path.join(self.current_dir, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_time < cutoff_date:
                    archive_path = os.path.join(self.archive_dir, filename)
                    os.rename(filepath, archive_path)
                    logging.info(f"Archived {filename}")
                    
    def create_summary_report(self):
        """Create a summary report of all collected data"""
        all_data = []
        
        # Read all CSV files in current directory
        for filename in os.listdir(self.current_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.current_dir, filename)
                try:
                    df = pd.read_csv(filepath)
                    all_data.append(df)
                except Exception as e:
                    logging.error(f"Error reading {filename}: {e}")
                    
        if all_data:
            # Combine all data
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Create summary
            summary_file = os.path.join(self.data_dir, f"summary_{datetime.now().strftime('%Y%m%d')}.txt")
            with open(summary_file, 'w') as f:
                f.write("KCEC Weather Data Summary\n")
                f.write(f"Generated: {datetime.now()}\n")
                f.write("-" * 50 + "\n")
                f.write(f"Total records: {len(combined_df)}\n")
                
                if 'precipitation_inches' in combined_df.columns:
                    f.write(f"Total precipitation: {combined_df['precipitation_inches'].sum():.2f} inches\n")
                    f.write(f"Days with precipitation: {(combined_df['precipitation_inches'] > 0).sum()}\n")
                    
    def send_email_notification(self, report, success):
        """Send email notification about data collection status"""
        if not all([self.config.get("smtp_server"), self.config.get("email_to")]):
            logging.warning("Email configuration incomplete, skipping notification")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email_from']
            msg['To'] = self.config['email_to']
            msg['Subject'] = f"KCEC Weather Data Collection - {'Success' if success else 'Failed'}"
            
            body = "Weekly KCEC Weather Data Collection Report\n\n"
            body += "\n".join(report)
            body += f"\n\nTimestamp: {datetime.now()}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            if self.config.get('smtp_username') and self.config.get('smtp_password'):
                server.login(self.config['smtp_username'], self.config['smtp_password'])
            server.send_message(msg)
            server.quit()
            
            logging.info("Email notification sent successfully")
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")
            
    def run_once(self):
        """Run data collection once"""
        return self.collect_weekly_data()
        
    def run_scheduled(self):
        """Run on a schedule (every Monday at 9 AM)"""
        schedule.every().monday.at("09:00").do(self.collect_weekly_data)
        
        logging.info("Weekly automation started. Will run every Monday at 9 AM")
        print("Weekly automation started. Press Ctrl+C to stop.")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def setup_cron():
    """Helper function to set up cron job"""
    print("\nTo set up automatic weekly collection using cron:")
    print("1. Open crontab: crontab -e")
    print("2. Add this line (runs every Monday at 9 AM):")
    print(f"0 9 * * 1 /usr/bin/python3 {os.path.abspath(__file__)} --run-once")
    print("\nOr for launchd on macOS, create a plist file in ~/Library/LaunchAgents/")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="KCEC Weekly Weather Data Automation")
    parser.add_argument("--run-once", action="store_true", help="Run data collection once and exit")
    parser.add_argument("--setup-cron", action="store_true", help="Show cron setup instructions")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron()
        return
        
    automation = KCECWeeklyAutomation(args.config)
    
    if args.run_once:
        success = automation.run_once()
        sys.exit(0 if success else 1)
    else:
        # Run scheduled
        automation.run_scheduled()

if __name__ == "__main__":
    main()