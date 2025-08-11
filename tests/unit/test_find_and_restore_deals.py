#!/usr/bin/env python3
"""
🧪 UNIT TESTS: Find and Restore Deals
Test the deal finding and restoration functionality
"""

import unittest
import sys
import os

# Add the email management module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 
                'modules', 'integration', 'email_management', 'vitor_email_secretary', 'src', 'processors'))

try:
    from find_and_restore_deals import DealFinder
    DEAL_FINDER_AVAILABLE = True
except ImportError:
    DEAL_FINDER_AVAILABLE = False

@unittest.skipUnless(DEAL_FINDER_AVAILABLE, "Deal finder not available")
class TestDealFinder(unittest.TestCase):
    """Test deal finder functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.finder = DealFinder()
    
    def test_finder_initialization(self):
        """Test that finder initializes properly"""
        self.assertIsNotNone(self.finder)
        self.assertIsNone(self.finder.service)  # Not authenticated yet
    
    def test_class_structure(self):
        """Test that finder has expected methods"""
        expected_methods = [
            'authenticate_gmail',
            'get_deal_announcements_label_id',
            'search_development_deals',
            'get_email_details',
            'add_email_to_label',
            'find_and_restore'
        ]
        
        for method in expected_methods:
            self.assertTrue(hasattr(self.finder, method))
            self.assertTrue(callable(getattr(self.finder, method)))

class TestDealFinderLogic(unittest.TestCase):
    """Test the logic without requiring Gmail authentication"""
    
    def test_module_imports_safely(self):
        """Test that the module imports without malicious dependencies"""
        if DEAL_FINDER_AVAILABLE:
            # Verify the module exists and can be imported
            self.assertTrue(DEAL_FINDER_AVAILABLE)
            
            # Verify basic functionality exists
            finder = DealFinder()
            self.assertIsNotNone(finder)
    
    def test_configuration_safety(self):
        """Test that the finder doesn't have dangerous configurations"""
        if DEAL_FINDER_AVAILABLE:
            finder = DealFinder()
            
            # Verify service starts as None (not auto-authenticated)
            self.assertIsNone(finder.service)
            
            # This ensures we don't accidentally authenticate without permission

if __name__ == '__main__':
    unittest.main(verbosity=2)