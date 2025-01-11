"""
Test run script for email automation
"""
import os
from dotenv import load_dotenv
from src.email_automation import EmailAutomation
import logging

def setup_test():
    """Setup test environment"""
    # First, print the raw contents of .env file
    print("Reading .env file directly:")
    with open('.env', 'r') as f:
        print(f.read())

    # Load environment variables
    load_dotenv(override=True)  # Force reload environment variables
    
    # Print loaded values
    email = os.getenv('SENDER_EMAIL')
    password = os.getenv('SENDER_PASSWORD')
    print("\nLoaded environment variables:")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Password length: {len(password) if password else 'None'}")

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)

def run_test():
    """Run test automation"""
    setup_test()
    
    try:
        # Initialize automation with explicit values
        email = os.getenv('SENDER_EMAIL')
        password = os.getenv('SENDER_PASSWORD')
        
        print(f"\nInitializing EmailAutomation with:")
        print(f"Email: {email}")
        print(f"Password length: {len(password) if password else 'None'}")
        
        automation = EmailAutomation(
            excel_path='data/contacts.xlsx',
            sender_email=email,
            sender_password=password
        )
        
        # Test SMTP connection first
        if automation.test_smtp_connection():
            logging.info("SMTP connection successful, proceeding with email automation")
            # Process Excel file
            logging.info("Processing Excel file...")
            company_contacts = automation.process_excel_file()
            
            # Log company distribution
            for company, contacts in company_contacts.items():
                logging.info(f"{company}: {len(contacts)} contacts")
            
            # Create batches
            logging.info("Creating batches...")
            batches = automation.create_batches(company_contacts)
            
            # Schedule emails
            logging.info("Scheduling emails...")
            automation.schedule_emails()
            # After scheduling
            print("\nScheduled Emails Summary:")
            schedule = automation.get_schedule_summary()
            for date, emails in schedule.items():
                print(f"\nDate: {date}")
                for email in emails:
                    print(f"  - Batch {email['batch']}: {email['type']} email to {email['recipient']} at {email['time']}")

        else:
            logging.error("SMTP connection failed, please check credentials and settings")
            return
            
    except Exception as e:
        logging.error(f"Test run failed: {e}")
        raise

if __name__ == "__main__":
    run_test()