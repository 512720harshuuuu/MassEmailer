"""
Main email automation class handling the core functionality
"""
import pandas as pd
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from typing import Dict, List, Tuple
from collections import defaultdict
import pandas as pd
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication  # Added for PDF attachment
import time
from typing import Dict, List, Tuple
from collections import defaultdict
from .utils.validators import EmailValidator, DataValidator
from .utils.company_matcher import CompanyMatcher
from .templates import EmailTemplateManager
from config.settings import EMAIL_SETTINGS, EMAIL_PROVIDERS

logger = logging.getLogger(__name__)

class EmailAutomation:
    def __init__(self, excel_path: str, sender_email: str, sender_password: str):
        """
        Initialize email automation system
        
        Args:
            excel_path: Path to Excel file with contacts
            sender_email: Sender's email address
            sender_password: Sender's email password
        """
        self.excel_path = excel_path
        self.sender_email = sender_email
        self.sender_password = sender_password
        
        # Initialize components
        self.validator = EmailValidator()
        self.data_validator = DataValidator()
        self.company_matcher = CompanyMatcher()
        self.template_manager = EmailTemplateManager()
        
        # Track email sending
        self.sent_emails = set()
        self.failed_emails = defaultdict(list)
        self.daily_count = 0
        self.last_send_time = None
        self.scheduled_emails = []  # Add this line


    def process_excel_file(self) -> Dict[str, List[Tuple[str, str]]]:
        """Process Excel file and organize contacts by company"""
        logger.info(f"Processing Excel file: {self.excel_path}")
        
        try:
            df = pd.read_excel(self.excel_path)
            if not self.data_validator.validate_excel_structure(df):
                raise ValueError("Invalid Excel structure")
                
            company_contacts = defaultdict(list)
            for _, row in df.iterrows():
                email = str(row['Email'])
                name = str(row['Name'])
                role = str(row['Role'])
                
                if self.validator.is_valid_email(email):
                    company = self.company_matcher.identify_company(email)
                    if company != 'unknown':
                        name = self.validator.normalize_name(name)
                        company_contacts[company].append((name, email,role))
            
            logger.info(f"Processed {sum(len(contacts) for contacts in company_contacts.values())} valid contacts")
            return company_contacts
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise
            
    def create_batches(self, company_contacts: Dict[str, List[Tuple[str, str]]]) -> List[Dict[str, List[Tuple[str, str]]]]:
        """Create balanced batches of contacts"""
        batches = []
        company_indices = {company: 0 for company in company_contacts}
        batch_size = EMAIL_SETTINGS['batch_size']
        company_quota = EMAIL_SETTINGS['company_quota']
        
        while True:
            current_batch = defaultdict(list)
            batch_complete = True
            
            for company in company_contacts:
                contacts = company_contacts[company]
                start_idx = company_indices[company]
                end_idx = min(start_idx + company_quota, len(contacts))
                
                if start_idx < len(contacts):
                    current_batch[company] = contacts[start_idx:end_idx]
                    company_indices[company] = end_idx
                    batch_complete = batch_complete and (end_idx - start_idx) == company_quota
            
            if not any(current_batch.values()):
                break
                
            batches.append(dict(current_batch))
            if not batch_complete:
                break
                
        logger.info(f"Created {len(batches)} batches")
        return batches
        
    def schedule_emails(self):
        """Schedule emails in batches with reminders"""
        try:
            company_contacts = self.process_excel_file()
            batches = self.create_batches(company_contacts)
            
            for batch_idx, batch in enumerate(batches, 1):
                # Schedule initial emails
                self._schedule_batch(
                    batch=batch,
                    days_delay=batch_idx - 1,  # Start from day 0
                    is_reminder=False,
                    batch_num=batch_idx
                )
                
                # Schedule reminder emails
                if batch_idx <= len(batches) - 2:  # Don't send reminders for last 2 batches
                    self._schedule_batch(
                        batch=batch,
                        days_delay=batch_idx + 1,  # Reminder 2 days after initial
                        is_reminder=True,
                        batch_num=batch_idx
                    )
                    
        except Exception as e:
            logger.error(f"Error in email scheduling: {e}")
            raise
            
    def _schedule_batch(self, batch: Dict[str, List[Tuple[str, str, str]]], 
                    days_delay: int, is_reminder: bool, batch_num: int):
        """Schedule a batch of emails"""
        send_time = datetime.now() + timedelta(days=days_delay)
        action = "Reminder" if is_reminder else "Initial"
        
        logger.info(f"Scheduling {action} Emails for Batch {batch_num}")
        logger.info(f"Scheduled for: {send_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        for company, contacts in batch.items():
            for name, email, role in contacts:
                try:
                    # Instead of sending immediately, store the scheduled email
                    scheduled_email = {
                        'recipient_email': email,
                        'recipient_name': name,
                        'company': company,
                        'is_reminder': is_reminder,
                        'batch_num': batch_num,
                        'send_time': send_time
                    }
                    
                    # Store this in a schedule queue
                    logger.info(f"Scheduled email to {email} for {send_time}")
                    self.scheduled_emails.append(scheduled_email)
                    
                except Exception as e:
                    logger.error(f"Failed to schedule email to {email}: {e}")
                    self.failed_emails[email].append({
                        'time': datetime.now(),
                        'error': str(e),
                        'batch': batch_num
                    })      
    def get_schedule_summary(self):
        """Get summary of scheduled emails"""
        schedule_summary = defaultdict(list)
        for email in self.scheduled_emails:
            date = email['send_time'].strftime('%Y-%m-%d')
            schedule_summary[date].append({
                'recipient': email['recipient_email'],
                'type': 'reminder' if email['is_reminder'] else 'initial',
                'batch': email['batch_num'],
                'time': email['send_time'].strftime('%H:%M:%S')
            })
        return schedule_summary    
    def _send_email(self, recipient_email: str, recipient_name: str, company: str, is_reminder: bool, batch_num: int):
        """Send individual email"""
        if recipient_email in self.sent_emails:
            logger.warning(f"Email already sent to {recipient_email}")
            return
            
        if self.daily_count >= EMAIL_PROVIDERS['gmail']['daily_limit']:
            logger.warning("Daily email limit reached")
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            template_type = 'reminder' if is_reminder else 'initial'
            template = self.template_manager.get_template(company, template_type)
            
            msg['Subject'] = f"{'Following up: ' if is_reminder else ''}Data Science Opportunities at {company.title()}"
            
            body = self.template_manager.format_template(
                template,
                name=recipient_name
            )
            msg.attach(MIMEText(body, 'plain'))

            # Attach resume
            resume_path = 'data/resume.pdf'  # Make sure your resume is in this location
            with open(resume_path, 'rb') as f:
                resume = MIMEApplication(f.read(), _subtype='pdf')
                resume.add_header('Content-Disposition', 'attachment', 
                                filename='Sai_Harsha_Mummaneni_Resume.pdf')
                msg.attach(resume)
            
            # Send email
            with smtplib.SMTP(EMAIL_PROVIDERS['gmail']['smtp_server'], 
                            EMAIL_PROVIDERS['gmail']['smtp_port']) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            logger.info(f"[Batch {batch_num}] Successfully sent {template_type} email to: {recipient_name} ({recipient_email})")
            
            self.sent_emails.add(recipient_email)
            self.daily_count += 1
            self.last_send_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {e}")
            raise          
    def test_smtp_connection(self):
        """Test SMTP connection before running automation"""
        try:
            logger.info("Testing SMTP connection...")
            logger.info(f"Connecting to {EMAIL_PROVIDERS['gmail']['smtp_server']}:{EMAIL_PROVIDERS['gmail']['smtp_port']}")
            time.sleep(1)  # Add small delay

            server = smtplib.SMTP(EMAIL_PROVIDERS['gmail']['smtp_server'], 
                                EMAIL_PROVIDERS['gmail']['smtp_port'])
            logger.info("Initial connection successful")
            
            logger.info("Starting TLS...")
            server.ehlo()
            server.starttls()
            server.ehlo()
            logger.info("TLS started successfully")
            
            logger.info("Attempting login...")
            server.login(self.sender_email, self.sender_password)
            logger.info("Login successful")
            
            server.quit()
            logger.info("SMTP connection test successful")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Authentication failed: {str(e)}")
            logger.error("Please check your email and app password")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            logger.error("This might be due to connection issues or server configuration")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during SMTP test: {str(e)}")
            logger.error(f"Using email: {self.sender_email}")
            return False
    def verify_schedule(self):
        """Verify and display all scheduled emails"""
        if not hasattr(self, 'scheduled_emails') or not self.scheduled_emails:
            print("\nNo emails currently scheduled")
            return
            
        print("\n=== SCHEDULED EMAILS ===")
        
        # Group by date
        from collections import defaultdict
        schedule_by_date = defaultdict(list)
        for email in self.scheduled_emails:
            date = email['send_time'].strftime('%Y-%m-%d')
            schedule_by_date[date].append(email)
        
        # Print schedule
        for date, emails in sorted(schedule_by_date.items()):
            print(f"\nDate: {date}")
            for email in sorted(emails, key=lambda x: x['send_time']):
                print(f"""
        Batch {email['batch_num']}:
        - Recipient: {email['recipient_name']} ({email['recipient_email']})
        - Type: {'Reminder' if email['is_reminder'] else 'Initial'} email
        - Company: {email['company'].title()}
        - Scheduled Time: {email['send_time'].strftime('%H:%M:%S')}
        """)
        
        print(f"\nTotal scheduled emails: {len(self.scheduled_emails)}")