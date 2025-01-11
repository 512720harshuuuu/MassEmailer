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

from .utils.validators import EmailValidator, DataValidator
from .utils.company_matcher import CompanyMatcher
from .templates import EmailTemplateManager
from config.settings import EMAIL_SETTINGS, EMAIL_PROVIDERS, RETRY_SETTINGS

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
                    self._send_email(
                        recipient_email=email,
                        recipient_name=name,
                        company=company,
                        is_reminder=is_reminder,
                        batch_num=batch_num
                    )
                    time.sleep(EMAIL_SETTINGS['cooling_period'] * 3600)  # Convert hours to seconds
                    
                except Exception as e:
                    logger.error(f"Failed to send email to {email}: {e}")
                    self.failed_emails[email].append({
                        'time': datetime.now(),
                        'error': str(e),
                        'batch': batch_num
                    })
                    
    def _send_email(self, recipient_email: str, recipient_name: str, 
                    company: str, is_reminder: bool, batch_num: int):
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
            
            # In real implementation, connect to SMTP server and send
            # This is a simulation for testing
            logger.info(f"[Batch {batch_num}] Would send {template_type} email to: {recipient_name} ({recipient_email})")
            
            self.sent_emails.add(recipient_email)
            self.daily_count += 1
            self.last_send_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {e}")
            raise