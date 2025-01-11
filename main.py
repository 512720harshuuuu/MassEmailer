"""
Entry point for email automation system
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from src.email_automation import EmailAutomation
from config.settings import LOGGING, PATH_SETTINGS

def setup_logging():
    """Configure logging"""
    # Create logs directory if it doesn't exist
    os.makedirs(PATH_SETTINGS['logs_dir'], exist_ok=True)
    
    # Configure logging
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger('email_automation')
    logger.info(f"Starting email automation at {datetime.now()}")
    return logger

def main():
    """Main execution function"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logging()
    
    try:
        # Initialize automation
        automation = EmailAutomation(
            excel_path=os.path.join(PATH_SETTINGS['data_dir'], 'contacts.xlsx'),
            sender_email=os.getenv('SENDER_EMAIL'),
            sender_password=os.getenv('SENDER_PASSWORD')
        )
        
        # Run automation
        automation.schedule_emails()
        logger.info("Email automation completed successfully")
        
    except Exception as e:
        logger.error(f"Error in email automation: {e}")
        raise

if __name__ == "__main__":
    main()