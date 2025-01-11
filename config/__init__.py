"""
Configuration management for email automation system.
"""

from .settings import (
    EMAIL_SETTINGS,
    EMAIL_PROVIDERS,
    LOGGING,
    PATH_SETTINGS
)

__all__ = [
    'EMAIL_SETTINGS',
    'EMAIL_PROVIDERS',
    'LOGGING',
    'PATH_SETTINGS'
]