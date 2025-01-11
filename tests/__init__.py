"""
Test suite for email automation system.
Contains unit tests and integration tests for all components.
"""

import os

# Create test data directory if it doesn't exist
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
os.makedirs(TEST_DATA_DIR, exist_ok=True)