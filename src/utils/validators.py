import re
import logging
from typing import Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailValidator:
    """Utility class for email validation and preprocessing"""
    
    # Regular expression for basic email validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Known social media domains to filter out
    SOCIAL_DOMAINS = {'linkedin.com', 'facebook.com', 'twitter.com'}
    
    @classmethod
    def is_valid_email(cls, email: Optional[str]) -> bool:
        """
        Validate email address format and domain
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
            
        # Convert to lowercase for consistent checking
        email = email.lower().strip()
        
        # Check for social media URLs
        if any(domain in email for domain in cls.SOCIAL_DOMAINS):
            logger.debug(f"Rejected social media URL: {email}")
            return False
            
        # Validate email format
        if not cls.EMAIL_PATTERN.match(email):
            logger.debug(f"Invalid email format: {email}")
            return False
            
        return True
        
    @staticmethod
    def normalize_name(name: Optional[str]) -> str:
        """
        Clean and normalize contact names
        
        Args:
            name: Name to normalize
            
        Returns:
            str: Normalized name
        """
        if not name or not isinstance(name, str):
            return ""
            
        # Remove extra whitespace and normalize case
        name = " ".join(name.split()).strip()
        
        # Capitalize first letter of each word
        return name.title()
        
class DataValidator:
    """Utility class for validating input data"""
    
    @staticmethod
    def validate_excel_structure(df) -> bool:
        """
        Validate Excel file structure
        
        Args:
            df: Pandas DataFrame to validate
            
        Returns:
            bool: True if structure is valid
        """
        required_columns = {'Role','Name', 'Email'}
        
        # Check for required columns
        if not all(col in df.columns for col in required_columns):
            logger.error("Missing required columns in Excel file")
            return False
            
        # Check for empty DataFrame
        if df.empty:
            logger.error("Excel file is empty")
            return False
            
        return True
        
    @staticmethod
    def validate_batch_size(size: Union[int, str]) -> int:
        """
        Validate and convert batch size
        
        Args:
            size: Batch size to validate
            
        Returns:
            int: Validated batch size
        """
        try:
            size = int(size)
            if size <= 0:
                raise ValueError("Batch size must be positive")
            return size
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid batch size: {e}")
            raise ValueError(f"Invalid batch size: {size}")