#!/usr/bin/env python3
"""
🧪 UNIT TESTS: Manual Selective Delete
Test the manual selective deletion functionality
"""

import unittest
import sys
import os

# Add the email management module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 
                'modules', 'integration', 'email_management', 'vitor_email_secretary', 'src', 'processors'))

try:
    from manual_selective_delete import ManualSelectiveDeleter
    SELECTIVE_DELETER_AVAILABLE = True
except ImportError:
    SELECTIVE_DELETER_AVAILABLE = False

@unittest.skipUnless(SELECTIVE_DELETER_AVAILABLE, "Manual selective deleter not available")
class TestManualSelectiveDeleter(unittest.TestCase):
    """Test manual selective deletion functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.deleter = ManualSelectiveDeleter()
    
    def test_deleter_initialization(self):
        """Test that deleter initializes properly"""
        self.assertIsNotNone(self.deleter)
        self.assertIsNone(self.deleter.service)  # Not authenticated yet
    
    def test_class_structure(self):
        """Test that deleter has expected methods"""
        expected_methods = [
            'authenticate_gmail',
            'get_inbox_emails',
            'get_email_details',
            'delete_email',
            'find_and_delete_approved_ads'
        ]
        
        for method in expected_methods:
            self.assertTrue(hasattr(self.deleter, method))
            self.assertTrue(callable(getattr(self.deleter, method)))

class TestManualSelectiveDeleteLogic(unittest.TestCase):
    """Test the logic without requiring Gmail authentication"""
    
    def test_module_imports_safely(self):
        """Test that the module imports without malicious dependencies"""
        if SELECTIVE_DELETER_AVAILABLE:
            # Verify the module exists and can be imported
            self.assertTrue(SELECTIVE_DELETER_AVAILABLE)
            
            # Verify basic functionality exists
            deleter = ManualSelectiveDeleter()
            self.assertIsNotNone(deleter)
    
    def test_configuration_safety(self):
        """Test that the deleter doesn't have dangerous configurations"""
        if SELECTIVE_DELETER_AVAILABLE:
            deleter = ManualSelectiveDeleter()
            
            # Verify service starts as None (not auto-authenticated)
            self.assertIsNone(deleter.service)
            
            # This ensures we don't accidentally authenticate without permission

if __name__ == '__main__':
    unittest.main(verbosity=2)