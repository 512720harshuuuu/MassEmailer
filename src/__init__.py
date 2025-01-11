"""
Email Automation System
A system for automating personalized email campaigns to data science managers.
"""

__version__ = '1.0.0'
__author__ = 'Sai Harsha Mummaneni'

from .email_automation import EmailAutomation
from .templates import EmailTemplateManager

__all__ = ['EmailAutomation', 'EmailTemplateManager']

