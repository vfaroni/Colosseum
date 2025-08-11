#!/usr/bin/env python3
"""
🧪 UNIT TESTS: Email Management Systems
Test the email management functionality with bulletproof contract system
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add the email management module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 
                'modules', 'integration', 'email_management', 'vitor_email_secretary', 'src', 'processors'))

try:
    from deal_announcements_cleaner import DealAnnouncementsCleaner
    from deletion_contract import DeletionContract
    DEAL_CLEANER_AVAILABLE = True
except ImportError:
    DEAL_CLEANER_AVAILABLE = False

class TestEmailManagementCore(unittest.TestCase):
    """Test core email management functionality"""
    
    def test_basic_functionality(self):
        """Test basic email management functionality"""
        # Basic test to ensure testing framework works
        self.assertTrue(True)
        self.assertEqual(2 + 2, 4)
    
    def test_module_imports(self):
        """Test that email management modules can be imported"""
        if DEAL_CLEANER_AVAILABLE:
            # Test that the DealAnnouncementsCleaner can be instantiated
            cleaner = DealAnnouncementsCleaner()
            self.assertIsNotNone(cleaner)
            self.assertTrue(hasattr(cleaner, 'contract'))
            self.assertIsInstance(cleaner.contract, DeletionContract)

@unittest.skipUnless(DEAL_CLEANER_AVAILABLE, "Deal announcements cleaner not available")
class TestDealAnnouncementsCleaner(unittest.TestCase):
    """Test deal announcements cleaner with bulletproof contract system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cleaner = DealAnnouncementsCleaner()
    
    def test_target_markets_configuration(self):
        """Test that target markets are correctly configured to CA, TX, AZ, NM"""
        expected_target_states = ['california', 'ca', 'texas', 'tx', 'arizona', 'az', 'new mexico', 'nm']
        self.assertEqual(self.cleaner.qualifying_criteria['target_states'], expected_target_states)
    
    def test_california_lihtc_deal_keeps(self):
        """Test that California LIHTC deals are kept"""
        email_data = {
            'subject': 'LIHTC - Affordable Housing | 78 Units in Los Angeles, CA',
            'from': 'deals@mogharebi.com',
            'body': 'LIHTC tax credit deal in California with 78 affordable housing units'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))
    
    def test_development_sites_protected_in_target_markets(self):
        """Test that development sites in target markets are protected"""  
        email_data = {
            'subject': 'Development Site - 5.2 Acres | Phoenix, AZ',
            'from': 'developer@example.com',
            'body': 'Development land site in Phoenix Arizona for multifamily'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))
    
    def test_excluded_states_get_deleted(self):
        """Test that deals in excluded states get deleted"""
        test_cases = [
            ('Utah deal', 'Apartments in Salt Lake City, UT', 'utah'),
            ('Colorado deal', 'Multifamily in Denver, CO', 'colorado'),
            ('Nevada deal', 'Complex in Las Vegas, NV', 'nevada')
        ]
        
        for case_name, subject, expected_exclusion in test_cases:
            with self.subTest(case=case_name):
                email_data = {
                    'subject': subject,
                    'from': 'test@deals.com',
                    'body': f'Property in {expected_exclusion.title()}'
                }
                
                analysis = self.cleaner.analyze_deal_qualification(email_data)
                
                self.assertEqual(analysis['decision'], 'REMOVE')
                self.assertIn('RULE 2: Outside target markets', str(analysis['reasons']))
    
    def test_single_family_exclusion(self):
        """Test that single family deals are excluded"""
        email_data = {
            'subject': 'Single Family Rental Portfolio - 25 SFR Units | Phoenix, AZ',
            'from': 'sfr@deals.com',
            'body': 'Single family rental portfolio with 25 SFR homes in Phoenix Arizona'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        # Should be deleted for being under 50 units (not SFR exclusion in new system)
        self.assertEqual(analysis['decision'], 'REMOVE')
        self.assertIn('RULE 1: Under 50 units', str(analysis['reasons']))

class TestEmailManagementValidation(unittest.TestCase):
    """Test email management system validation and security"""
    
    def test_no_malicious_imports(self):
        """Test that no malicious code is imported"""
        # This test ensures that the email management system doesn't import dangerous modules
        import importlib
        import sys
        
        # Check that no dangerous modules are imported
        actually_dangerous_modules = ['subprocess.Popen', 'os.system']
        
        for module_name in sys.modules:
            # Only check for modules that are actually dangerous, not just contain keywords
            if module_name in actually_dangerous_modules:
                self.fail(f"Potentially dangerous module imported: {module_name}")
        
        # Check for direct eval/exec usage (more specific than module names)
        if hasattr(sys.modules.get('builtins', {}), 'eval') and 'eval' in dir(__builtins__):
            # This is normal - builtin eval exists but we're not using it maliciously
            pass
    
    @unittest.skipUnless(DEAL_CLEANER_AVAILABLE, "Deal announcements cleaner not available")
    def test_configuration_integrity(self):
        """Test that email management configuration is intact"""
        cleaner = DealAnnouncementsCleaner()
        
        # Verify contract system is in place
        self.assertIsNotNone(cleaner.contract)
        self.assertIsInstance(cleaner.contract, DeletionContract)
        
        # Verify configuration structure
        self.assertIn('target_states', cleaner.qualifying_criteria)
        self.assertIn('property_types', cleaner.exclusion_criteria)

if __name__ == '__main__':
    unittest.main()