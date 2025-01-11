# Configuration settings for email automation
import logging
import os
from datetime import timedelta

# Email batch settings
EMAIL_SETTINGS = {
    'batch_size': 40,        # Total emails per batch
    'company_quota': 10,     # Emails per company in each batch
    'reminder_delay': 2,     # Days before sending reminder
    'cooling_period': 1      # Hours between email sends
}

# Email provider configurations
EMAIL_PROVIDERS = {
    'gmail': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'daily_limit': 500,  # Gmail's daily sending limit
        'batch_limit': 100   # Emails per batch to avoid rate limiting
    },
    'outlook': {
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'daily_limit': 300,
        'batch_limit': 75
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join('logs', 'email_automation.log'),
            'level': 'DEBUG',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'email_automation': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# Retry settings for failed emails
RETRY_SETTINGS = {
    'max_attempts': 3,
    'delay_between_attempts': timedelta(minutes=30),
    'exponential_backoff': True
}

# Path settings
PATH_SETTINGS = {
    'data_dir': 'data',
    'logs_dir': 'logs',
    'templates_dir': os.path.join('src', 'templates')
}