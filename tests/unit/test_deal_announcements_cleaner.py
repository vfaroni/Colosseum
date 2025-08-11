#!/usr/bin/env python3
"""
🧪 UNIT TESTS: Deal Announcements Cleaner
Test the bulletproof contract system and deal deletion logic
"""

import unittest
import sys
import os

# Add the email management module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 
                'modules', 'integration', 'email_management', 'vitor_email_secretary', 'src', 'processors'))

from deal_announcements_cleaner import DealAnnouncementsCleaner
from deletion_contract import DeletionContract

class TestDealAnnouncementsCleaner(unittest.TestCase):
    """Test deal announcements cleaner with bulletproof contract system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cleaner = DealAnnouncementsCleaner()
        self.contract = DeletionContract()
    
    def test_contract_system_initialization(self):
        """Test that contract system is properly initialized"""
        self.assertIsNotNone(self.cleaner.contract)
        self.assertIsInstance(self.cleaner.contract, DeletionContract)
    
    def test_california_lihtc_deal_kept(self):
        """Test that California LIHTC deals are kept"""
        email_data = {
            'subject': 'LIHTC - Affordable Housing | 78 Units in Los Angeles, CA',
            'from': 'deals@mogharebi.com',
            'body': 'LIHTC tax credit deal in California with 78 affordable housing units'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))
    
    def test_texas_multifamily_deal_kept(self):
        """Test that Texas multifamily deals are kept"""
        email_data = {
            'subject': 'Greysteel Offering: Martha\'s Villa Apartments | 177 Units | Fort Worth, TX',
            'from': 'deals@greysteel.com',
            'body': 'Multifamily property in Fort Worth Texas with 177 units'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))
    
    def test_arizona_development_site_kept(self):
        """Test that Arizona development sites are kept"""
        email_data = {
            'subject': 'REMINDER - CALL FOR OFFERS: July 31, 2025 :: Residences at Tierra Montana | ±17.0 Acres | Zoned for Multifamily | Laveen Village, AZ',
            'from': 'cbre@rcm1.com',
            'body': 'Development site in Arizona zoned for multifamily housing development'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))
    
    def test_new_mexico_deal_kept(self):
        """Test that New Mexico deals are kept"""
        email_data = {
            'subject': 'Affordable Housing Opportunity | 120 Units in Albuquerque, NM',
            'from': 'newmexico@deals.com',
            'body': 'Affordable housing project in Albuquerque New Mexico with 120 units'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))

class TestDeletionRules(unittest.TestCase):
    """Test the three deletion rules specifically"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cleaner = DealAnnouncementsCleaner()
        self.contract = DeletionContract()
    
    def test_rule_1_under_50_units_deleted(self):
        """Test Rule 1: Under 50 units are deleted"""
        email_data = {
            'subject': 'Now Touring by Appt Only | 24 Units | Original Developer | San Leandro',
            'from': 'bayareamultifamily@colliers.com',
            'body': '24 unit property in San Leandro California'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'REMOVE')
        self.assertIn('RULE 1: Under 50 units (24)', str(analysis['reasons']))
    
    def test_rule_1_land_site_exception(self):
        """Test Rule 1: Land sites are exempt from unit count rule"""
        email_data = {
            'subject': 'Development Land Site | 5.2 Acres | Zoned for 40 Units | Phoenix, AZ',
            'from': 'land@deals.com',
            'body': 'Development land site in Phoenix Arizona, 5.2 acres zoned for multifamily'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))
    
    def test_rule_2_outside_target_markets_deleted(self):
        """Test Rule 2: Outside target markets are deleted"""
        email_data = {
            'subject': 'Bid Deadline (August 13th) | 123 Units | 100% HAP | Camden, NJ',
            'from': 'svnaffordablelistings@svn.com',
            'body': '123 unit property in Camden New Jersey'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'REMOVE')
        self.assertIn('RULE 2: Outside target markets', str(analysis['reasons']))
    
    def test_rule_2_former_target_states_now_excluded(self):
        """Test Rule 2: Former target states (UT, CO, NV) are now excluded"""
        test_cases = [
            {
                'subject': '192 Units in Orem, UT | Call for Details',
                'body': '192 unit apartment complex in Orem Utah',
                'state': 'Utah'
            },
            {
                'subject': 'Denver Multifamily Portfolio - 150 Units | Colorado',
                'body': 'Multifamily portfolio in Denver Colorado',
                'state': 'Colorado'
            },
            {
                'subject': 'Las Vegas Investment Opportunity | 88 Units | Nevada',
                'body': 'Investment opportunity in Las Vegas Nevada',
                'state': 'Nevada'
            }
        ]
        
        for case in test_cases:
            with self.subTest(state=case['state']):
                email_data = {
                    'subject': case['subject'],
                    'from': 'test@deals.com',
                    'body': case['body']
                }
                
                analysis = self.cleaner.analyze_deal_qualification(email_data)
                
                self.assertEqual(analysis['decision'], 'REMOVE')
                self.assertIn('RULE 2: Outside target markets', str(analysis['reasons']))
    
    def test_rule_3_successful_closings_deleted(self):
        """Test Rule 3: Successful closing announcements are deleted"""
        email_data = {
            'subject': 'Just Closed: 150 Unit Multifamily Deal in Austin, TX',
            'from': 'closed@deals.com',
            'body': 'We just closed this 150 unit multifamily property in Austin Texas'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'REMOVE')
        self.assertIn('RULE 3: Successful closing announcement', str(analysis['reasons']))
    
    def test_rule_3_active_deals_not_closings(self):
        """Test Rule 3: Active deals with call for offers are kept"""
        email_data = {
            'subject': 'Call for Offers: August 12th | Yardly Paradisi | 193-Home Build-to-Rent Community | Phoenix MSA',
            'from': 'northmarqlistings@rcm1.com',
            'body': 'Call for offers on 193 home build-to-rent community in Phoenix metropolitan area'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))

class TestContractValidation(unittest.TestCase):
    """Test the bulletproof contract validation system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.contract = DeletionContract()
    
    def test_unit_detection_validation(self):
        """Test unit detection validation method"""
        email_data = {
            'subject': 'For Sale: The Flats | 18 Luxury Apartments & Upscale Retail Steps from the Beach',
            'from': 'philip.buckley@cbre.com',
            'body': '18 luxury apartments near the beach'
        }
        
        should_delete, reason, unit_count = self.contract.validate_unit_detection(email_data)
        
        self.assertTrue(should_delete)
        self.assertEqual(unit_count, 18)
        self.assertIn('RULE 1: Under 50 units (18)', reason)
    
    def test_location_detection_validation(self):
        """Test location detection validation method"""
        email_data = {
            'subject': 'Exclusive Offering: Bozeman Montana MHC Portfolio | 2 Legacy Communities',
            'from': 'manufacturedhousing@berkadia.com',
            'body': 'Manufactured housing community portfolio in Bozeman Montana'
        }
        
        should_delete, reason, locations = self.contract.validate_location_detection(email_data)
        
        self.assertTrue(should_delete)
        self.assertIn('RULE 2: Outside target markets', reason)
        self.assertIn('bozeman montana', reason.lower())
    
    def test_closing_detection_validation(self):
        """Test closing detection validation method"""
        active_deal_data = {
            'subject': 'CALL FOR OFFERS: Auro Crossing // 100% LIHTC // 256 Units // Austin, TX // 8.14.2025',
            'from': 'AHAinfo@nmrk.com',
            'body': 'Call for offers on LIHTC property in Austin Texas'
        }
        
        should_delete, reason, phrase = self.contract.validate_closing_detection(active_deal_data)
        
        self.assertFalse(should_delete)
        self.assertIn('Active deal - not a closing', reason)
    
    def test_contract_enforcement_guarantee(self):
        """Test that contract enforcement provides guaranteed results"""
        # Test a deal that should be deleted (under 50 units)
        delete_email = {
            'subject': 'Steps from Sausalito Ferry | 28 Units | > 5% In-Place Cap Rate',
            'from': 'bayareamultifamily@colliers.com',
            'body': '28 unit property near Sausalito ferry'
        }
        
        result = self.contract.enforce_deletion_contract(delete_email)
        
        self.assertEqual(result['decision'], 'REMOVE')
        self.assertIn('contract_results', result)
        self.assertEqual(result['contract_results']['final_decision'], 'REMOVE')
        self.assertTrue(result['contract_results']['contract_enforced'])
        
        # Test a deal that should be kept (50+ units in target market)
        keep_email = {
            'subject': 'Silicon Valley Investment Opportunity | 134-Unit Value-Add Community in Fremont, California',
            'from': 'investmentproperty@rcm1.com',
            'body': '134 unit value-add community in Fremont California'
        }
        
        result = self.contract.enforce_deletion_contract(keep_email)
        
        self.assertEqual(result['decision'], 'KEEP')
        self.assertIn('contract_results', result)
        self.assertEqual(result['contract_results']['final_decision'], 'KEEP')
        self.assertTrue(result['contract_results']['contract_enforced'])

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cleaner = DealAnnouncementsCleaner()
    
    def test_exactly_50_units_kept(self):
        """Test that exactly 50 units are kept (boundary condition)"""
        email_data = {
            'subject': 'Value-Add Opportunity | Prime Cal State Fresno Location | 50 Units in Fresno, CA',
            'from': 'sales@mogharebi.com',
            'body': '50 unit property in Fresno California'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))
    
    def test_49_units_deleted(self):
        """Test that 49 units are deleted (boundary condition)"""
        email_data = {
            'subject': 'Small Multifamily Deal | 49 Units | Sacramento, CA',
            'from': 'small@deals.com',
            'body': '49 unit multifamily property in Sacramento California'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'REMOVE')
        self.assertIn('RULE 1: Under 50 units (49)', str(analysis['reasons']))
    
    def test_mixed_unit_types_maximum_detection(self):
        """Test that maximum unit count is used when multiple unit types detected"""
        email_data = {
            'subject': 'Mixed-Use Development | 25 Apartments + 75 Condos = 100 Total Units | Phoenix, AZ',
            'from': 'mixed@deals.com',
            'body': 'Mixed use development with 25 apartments and 75 condos for total of 100 units in Phoenix Arizona'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        # Should use maximum unit count (100) not minimum (25)
        self.assertIn('No deletion criteria met', str(analysis['reasons']))
    
    def test_no_units_detected_kept(self):
        """Test that emails with no unit detection are kept (conservative approach)"""
        email_data = {
            'subject': 'Investment Opportunity for 4825 - 4857 College Ave',
            'from': 'cbre@rcm1.com',
            'body': 'Investment opportunity on College Avenue in Oakland California'
        }
        
        analysis = self.cleaner.analyze_deal_qualification(email_data)
        
        self.assertEqual(analysis['decision'], 'KEEP')
        self.assertIn('No deletion criteria met', str(analysis['reasons']))

if __name__ == '__main__':
    unittest.main()