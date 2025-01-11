import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class CompanyMatcher:
    """Utility class for identifying companies from email addresses"""
    
    # Company email patterns
    COMPANY_PATTERNS = {
        'amazon': [r'@amazon\.', r'@a2z\.'],
        'meta': [r'@meta\.', r'@fb\.', r'@facebook\.'],
        'google': [r'@google\.', r'@gmail\.'],
        'apple': [r'@apple\.', r'@icloud\.']
    }
    
    # Compiled regex patterns for performance
    _compiled_patterns: Dict[str, list] = {}
    
    def __init__(self):
        """Initialize regex patterns"""
        for company, patterns in self.COMPANY_PATTERNS.items():
            self._compiled_patterns[company] = [
                re.compile(pattern, re.IGNORECASE) 
                for pattern in patterns
            ]
    
    def identify_company(self, email: Optional[str]) -> str:
        """
        Identify company from email address
        
        Args:
            email: Email address to check
            
        Returns:
            str: Identified company name or 'unknown'
        """
        if not email or not isinstance(email, str):
            return 'unknown'
            
        email = email.lower().strip()
        
        # Check each company's patterns
        for company, patterns in self._compiled_patterns.items():
            if any(pattern.search(email) for pattern in patterns):
                logger.debug(f"Identified {company} from email: {email}")
                return company
                
        logger.debug(f"Unknown company for email: {email}")
        return 'unknown'
    
    def get_company_quota(self, company: str, default_quota: int = 10) -> int:
        """
        Get email quota for specific company
        
        Args:
            company: Company name
            default_quota: Default quota if not specified
            
        Returns:
            int: Company-specific quota
        """
        # Company-specific quotas (can be adjusted based on requirements)
        quotas = {
            'amazon': 10,
            'meta': 10,
            'google': 10,
            'apple': 10
        }
        return quotas.get(company, default_quota)
        
    def validate_company_distribution(self, companies: Dict[str, int]) -> bool:
        """
        Validate distribution of emails across companies
        
        Args:
            companies: Dictionary of company counts
            
        Returns:
            bool: True if distribution is valid
        """
        if not companies:
            return False
            
        # Check if we have contacts for each target company
        missing_companies = set(self.COMPANY_PATTERNS.keys()) - set(companies.keys())
        if missing_companies:
            logger.warning(f"Missing contacts for companies: {missing_companies}")
            return False
            
        return True