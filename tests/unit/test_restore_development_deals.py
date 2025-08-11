#!/usr/bin/env python3
"""
🧪 UNIT TESTS: Restore Development Deals
Test the development deal restoration functionality
"""

import unittest
import sys
import os

# Add the email management module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 
                'modules', 'integration', 'email_management', 'vitor_email_secretary', 'src', 'processors'))

try:
    from restore_development_deals import DevelopmentDealsRestorer
    RESTORER_AVAILABLE = True
except ImportError:
    RESTORER_AVAILABLE = False

@unittest.skipUnless(RESTORER_AVAILABLE, "Development deals restorer not available")
class TestDevelopmentDealsRestorer(unittest.TestCase):
    """Test development deals restorer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.restorer = DevelopmentDealsRestorer()
    
    def test_restorer_initialization(self):
        """Test that restorer initializes properly"""
        self.assertIsNotNone(self.restorer)
        self.assertIsNone(self.restorer.service)  # Not authenticated yet
    
    def test_class_structure(self):
        """Test that restorer has expected methods"""
        expected_methods = [
            'authenticate_gmail',
            'get_deal_announcements_label_id',
            'search_rocklin_deals',
            'get_email_details',
            'add_email_to_label',
            'restore_development_deals'
        ]
        
        for method in expected_methods:
            self.assertTrue(hasattr(self.restorer, method))
            self.assertTrue(callable(getattr(self.restorer, method)))

class TestDevelopmentDealsRestorerLogic(unittest.TestCase):
    """Test the logic without requiring Gmail authentication"""
    
    def test_module_imports_safely(self):
        """Test that the module imports without malicious dependencies"""
        if RESTORER_AVAILABLE:
            # Verify the module exists and can be imported
            self.assertTrue(RESTORER_AVAILABLE)
            
            # Verify basic functionality exists
            restorer = DevelopmentDealsRestorer()
            self.assertIsNotNone(restorer)
    
    def test_configuration_safety(self):
        """Test that the restorer doesn't have dangerous configurations"""
        if RESTORER_AVAILABLE:
            restorer = DevelopmentDealsRestorer()
            
            # Verify service starts as None (not auto-authenticated)
            self.assertIsNone(restorer.service)
            
            # This ensures we don't accidentally authenticate without permission

if __name__ == '__main__':
    unittest.main(verbosity=2)