"""
Small scale test for email scheduling
"""
import os
from dotenv import load_dotenv
from src.email_automation import EmailAutomation
import logging
from datetime import datetime, timedelta
import time

def setup_test():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)

def run_small_test():
    """Run a small scale test with just 2-3 emails"""
    setup_test()
    
    try:
        automation = EmailAutomation(
            excel_path='data/contacts.xlsx',
            sender_email=os.getenv('SENDER_EMAIL'),
            sender_password=os.getenv('SENDER_PASSWORD')
        )
        
        # Test SMTP connection
        if not automation.test_smtp_connection():
            logging.error("SMTP connection failed")
            return
            
        # Process contacts but limit to 2-3 emails for testing
        company_contacts = automation.process_excel_file()
        test_contacts = {}
        
        # Take only 1 contact from each company for testing
        for company, contacts in company_contacts.items():
            test_contacts[company] = contacts[:1]  # Take first contact from each company
            
        # Schedule these emails for the next few minutes
        current_time = datetime.now()
        
        # Schedule first email in 2 minutes
        automation._schedule_batch(
            batch=test_contacts,
            days_delay=0,  # Today
            is_reminder=False,
            batch_num=1
        )
        
        print("\nScheduled emails:")
        automation.verify_schedule()
        
        print("\nWaiting to send scheduled emails...")
        print("Press Ctrl+C to stop the program")
        
        # Run the scheduling loop
        while True:
            current_time = datetime.now()
            for email in automation.scheduled_emails[:]:
                if current_time >= email['send_time']:
                    try:
                        automation._send_email(
                            recipient_email=email['recipient_email'],
                            recipient_name=email['recipient_name'],
                            company=email['company'],
                            is_reminder=email['is_reminder'],
                            batch_num=email['batch_num']
                        )
                        automation.scheduled_emails.remove(email)
                        print(f"Sent email to {email['recipient_email']}")
                    except Exception as e:
                        logging.error(f"Failed to send scheduled email: {e}")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\nStopping the scheduler...")
    except Exception as e:
        logging.error(f"Test run failed: {e}")
        raise

if __name__ == "__main__":
    run_small_test()