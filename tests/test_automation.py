"""
Test suite for email automation
"""
import unittest
import pandas as pd
import os
from datetime import datetime
from src.email_automation import EmailAutomation
from src.utils.validators import EmailValidator
from src.utils.company_matcher import CompanyMatcher

class TestEmailAutomation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Create test data
        cls.create_test_excel()
        
        # Initialize automation
        cls.automation = EmailAutomation(
            excel_path="tests/test_data/test_contacts.xlsx",
            sender_email="test@example.com",
            sender_password="test_password"
        )
    
    @classmethod
    def create_test_excel(cls):
        """Create test Excel file"""
        test_data = {
            'Name': [
                'John Doe', 'Jane Smith', 'Bob Wilson',
                'Alice Brown', 'Charlie Davis', 'Eve White',
                'Invalid Name'
            ],
            'Email': [
                'john.doe@amazon.com',
                'jane.smith@meta.com',
                'bob.wilson@google.com',
                'alice@apple.com',
                'charlie@unknown.com',
                'linkedin.com/in/eve',
                ''
            ]
        }
        
        df = pd.DataFrame(test_data)
        os.makedirs('tests/test_data', exist_ok=True)
        df.to_excel("tests/test_data/test_contacts.xlsx", index=False)
    
    def test_excel_processing(self):
        """Test Excel file processing"""
        company_contacts = self.automation.process_excel_file()
        
        # Check company identification
        self.assertIn('amazon', company_contacts)
        self.assertIn('meta', company_contacts)
        self.assertIn('google', company_contacts)
        self.assertIn('apple', company_contacts)
        
        # Check invalid emails are filtered
        total_contacts = sum(len(contacts) for contacts in company_contacts.values())
        self.assertEqual(total_contacts, 4)  # Only valid company emails
    
    def test_batch_creation(self):
        """Test batch creation logic"""
        company_contacts = self.automation.process_excel_file()
        batches = self.automation.create_batches(company_contacts)
        
        # Check batch properties
        for batch in batches:
            total_contacts = sum(len(contacts) for contacts in batch.values())
            self.assertLessEqual(total_contacts, self.automation.batch_size)
    
    def test_email_scheduling(self):
        """Test email scheduling logic"""
        try:
            self.automation.schedule_emails()
            self.assertTrue(True)  # If no exception is raised
        except Exception as e:
            self.fail(f"Email scheduling failed with error: {e}")

class TestEmailValidation(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.validator = EmailValidator()
    
    def test_valid_emails(self):
        """Test valid email validation"""
        valid_emails = [
            'test@amazon.com',
            'john.doe@meta.com',
            'test.email+123@google.com'
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(self.validator.is_valid_email(email))
    
    def test_invalid_emails(self):
        """Test invalid email validation"""
        invalid_emails = [
            '',
            None,
            'invalid.email',
            'linkedin.com/profile',
            '@nodomain.com'
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(self.validator.is_valid_email(email))

if __name__ == '__main__':
    unittest.main()