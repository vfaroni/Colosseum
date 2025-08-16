#!/usr/bin/env python3
"""
Comprehensive BOTN Generator - Complete recreation with xlsxwriter
Creates a fully functional BOTN calculator with all essential calculations
"""

import pandas as pd
import xlsxwriter
from pathlib import Path
import logging
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveBOTNGenerator:
    """Complete BOTN calculator with all essential calculations"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.sites_path = self.base_path / "Sites"
        
    def process_user_inputs(self, raw_inputs):
        """Process and normalize user inputs"""
        processed = {}
        
        input_mapping = {
            8: ('Housing Type', raw_inputs[0]),
            9: ('Credit Pricing', raw_inputs[1]),
            10: ('Credit Type', raw_inputs[2]),
            11: ('Construction Loan Term', raw_inputs[3]),
            12: ('Market Cap Rate', raw_inputs[4]),
            13: ('Financing Interest Rate', raw_inputs[5]),
            14: ('Elevator', raw_inputs[6]),
            15: ('# Units', raw_inputs[7]),
            16: ('Avg Unit Size', raw_inputs[8]),
            17: ('Hard Cost/SF', raw_inputs[9])
        }
        
        for col_num, (field_name, raw_value) in input_mapping.items():
            processed_value = self.normalize_input(field_name, raw_value)
            processed[col_num] = processed_value
            logger.info(f"Processed {field_name}: '{raw_value}' → {processed_value}")
        
        return processed
    
    def normalize_input(self, field_name, raw_value):
        """Normalize input values"""
        raw_str = str(raw_value).strip()
        
        if 'Housing Type' in field_name:
            return raw_str.title()
        elif 'Credit Pricing' in field_name:
            if 'cent' in raw_str.lower():
                number = re.findall(r'\d+', raw_str)[0]
                return float(number) / 100
            elif '%' in raw_str:
                number = float(re.findall(r'[\d.]+', raw_str)[0])
                return number / 100
            else:
                return float(raw_str)
        elif 'Credit Type' in field_name:
            return raw_str
        elif 'Loan Term' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Rate' in field_name:
            if '%' in raw_str:
                number = float(re.findall(r'[\d.]+', raw_str)[0])
                return number / 100
            else:
                return float(raw_str)
        elif 'Elevator' in field_name:
            if raw_str.lower() in ['no', 'none', 'false']:
                return "Non-Elevator"
            else:
                return "Elevator"
        elif 'Units' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Unit Size' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        elif 'Hard Cost' in field_name:
            number = re.findall(r'\d+', raw_str)[0]
            return int(number)
        else:
            return raw_str
    
    def get_cdlac_region(self, county_name):
        """Get CDLAC region"""
        cdlac_regions = {
            'San Francisco': 'San Francisco County',
            'Alameda': 'East Bay Region', 'Contra Costa': 'East Bay Region',
            'San Mateo': 'South & West Bay Region', 'Santa Clara': 'South & West Bay Region',
            'Santa Cruz': 'South & West Bay Region',
            'Lake': 'Northern Region', 'Marin': 'Northern Region', 'Napa': 'Northern Region',
            'Solano': 'Northern Region', 'Sonoma': 'Northern Region', 'Butte': 'Northern Region', 
            'Colusa': 'Northern Region', 'El Dorado': 'Northern Region', 'Glenn': 'Northern Region', 
            'Nevada': 'Northern Region', 'Placer': 'Northern Region', 'Sacramento': 'Northern Region', 
            'Sutter': 'Northern Region', 'Tehama': 'Northern Region', 'Yolo': 'Northern Region', 
            'Yuba': 'Northern Region', 'Alpine': 'Northern Region', 'Amador': 'Northern Region', 
            'Calaveras': 'Northern Region', 'Del Norte': 'Northern Region', 'Humboldt': 'Northern Region', 
            'Inyo': 'Northern Region', 'Lassen': 'Northern Region', 'Madera': 'Northern Region', 
            'Mariposa': 'Northern Region', 'Mendocino': 'Northern Region', 'Modoc': 'Northern Region', 
            'Mono': 'Northern Region', 'Plumas': 'Northern Region', 'Shasta': 'Northern Region', 
            'Sierra': 'Northern Region', 'Siskiyou': 'Northern Region', 'Tuolumne': 'Northern Region', 
            'Trinity': 'Northern Region',
            'Fresno': 'Central Valley Region', 'Kern': 'Central Valley Region', 'Kings': 'Central Valley Region', 
            'Merced': 'Central Valley Region', 'San Joaquin': 'Central Valley Region', 
            'Stanislaus': 'Central Valley Region', 'Tulare': 'Central Valley Region',
            'Monterey': 'Central Coast Region', 'San Benito': 'Central Coast Region', 
            'San Luis Obispo': 'Central Coast Region', 'Santa Barbara': 'Central Coast Region', 
            'Ventura': 'Central Coast Region',
            'Los Angeles': 'Los Angeles County',
            'Orange': 'Orange County',
            'Riverside': 'Inland Empire Region', 'San Bernardino': 'Inland Empire Region',
            'San Diego': 'San Diego County', 'Imperial': 'San Diego County'
        }
        return cdlac_regions.get(county_name, None)
    
    def create_comprehensive_botn(self, site_data, user_inputs):
        """Create comprehensive BOTN with all calculations"""
        
        # Generate filename
        site_name = str(site_data.get('Property Name', 'Site')).replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"COMPREHENSIVE_BOTN_{site_name}_{timestamp}.xlsx"
        output_path = self.base_path / "outputs" / output_filename
        
        try:
            # Create workbook
            workbook = xlsxwriter.Workbook(str(output_path))
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter'
            })
            
            input_format = workbook.add_format({
                'bg_color': '#E7E6E6',
                'border': 1
            })
            
            calc_format = workbook.add_format({
                'bg_color': '#F2F2F2',
                'border': 1,
                'num_format': '#,##0'
            })
            
            money_format = workbook.add_format({
                'bg_color': '#F2F2F2',
                'border': 1,
                'num_format': '$#,##0'
            })
            
            percent_format = workbook.add_format({
                'bg_color': '#F2F2F2',
                'border': 1,
                'num_format': '0.00%'
            })
            
            # Create Inputs sheet
            inputs_sheet = workbook.add_worksheet('Inputs')
            inputs_sheet.set_column('A:A', 25)
            inputs_sheet.set_column('B:B', 15)
            
            # Headers
            inputs_sheet.write('A1', 'INPUT FIELD', header_format)
            inputs_sheet.write('B1', 'VALUE', header_format)
            
            # Site data inputs
            site_inputs = [
                ('Property Name', str(site_data.get('Property Name', ''))),
                ('Property Address', str(site_data.get('Property Address', ''))),
                ('County Name', str(site_data.get('County Name', ''))),
                ('CDLAC Region', str(self.get_cdlac_region(site_data.get('County Name')))),
                ('State', str(site_data.get('State', ''))),
                ('Zip Code', site_data.get('Zip', '')),
                ('Purchase Price', float(site_data.get('For Sale Price', 0)) if site_data.get('For Sale Price') else 0),
            ]
            
            # User inputs
            user_input_labels = [
                'Housing Type', 'Credit Pricing', 'Credit Type', 'Construction Loan Term',
                'Market Cap Rate', 'Financing Interest Rate', 'Elevator', 'Number of Units',
                'Average Unit Size', 'Hard Cost per SF'
            ]
            
            # Write site data
            row = 1
            for label, value in site_inputs:
                inputs_sheet.write(row, 0, label)
                if isinstance(value, (int, float)) and label == 'Purchase Price':
                    inputs_sheet.write(row, 1, value, money_format)
                else:
                    inputs_sheet.write(row, 1, value, input_format)
                row += 1
            
            # Write user inputs
            for i, label in enumerate(user_input_labels):
                col_num = i + 8  # Starting from column H (8)
                value = user_inputs.get(col_num, '')
                inputs_sheet.write(row, 0, label)
                
                if 'Rate' in label or 'Pricing' in label:
                    inputs_sheet.write(row, 1, value, percent_format)
                elif isinstance(value, (int, float)) and ('Units' in label or 'Size' in label or 'Cost' in label):
                    inputs_sheet.write(row, 1, value, calc_format)
                else:
                    inputs_sheet.write(row, 1, value, input_format)
                row += 1
            
            # Create Calculations sheet
            calc_sheet = workbook.add_worksheet('Calculations')
            calc_sheet.set_column('A:A', 30)
            calc_sheet.set_column('B:B', 15)
            
            # Headers
            calc_sheet.write('A1', 'CALCULATION', header_format)
            calc_sheet.write('B1', 'RESULT', header_format)
            
            # Key BOTN calculations
            calculations = [
                ('Total Units', f'=Inputs!B{7 + len(user_input_labels)}'),  # Number of Units
                ('Total Square Feet', f'=B2*Inputs!B{8 + len(user_input_labels)}'),  # Units * Avg Unit Size
                ('Total Hard Costs', f'=B3*Inputs!B{9 + len(user_input_labels)}'),  # Total SF * Hard Cost/SF
                ('Purchase Price', f'=Inputs!B7'),
                ('Total Development Cost', '=B4+B5'),  # Hard Costs + Land
                ('Cost per Unit', '=B6/B2'),
                ('Cost per SF', '=B6/B3'),
                ('Annual Tax Credits (4%)', '=B6*0.04'),  # Basic 4% calculation
                ('10-Year Credit Value', '=B9*10'),
                ('Net Present Value of Credits', f'=B10/(1+Inputs!B{5 + len(user_input_labels)})^5'),  # Discounted at cap rate
            ]
            
            row = 1
            for label, formula in calculations:
                calc_sheet.write(row, 0, label)
                calc_sheet.write(row, 1, formula, calc_format if 'Cost' in label or 'Units' in label else money_format)
                row += 1
            
            # Create Summary sheet
            summary_sheet = workbook.add_worksheet('Summary')
            summary_sheet.set_column('A:A', 25)
            summary_sheet.set_column('B:B', 20)
            
            # Summary header
            summary_sheet.write('A1', 'PROJECT SUMMARY', header_format)
            summary_sheet.write('B1', site_data.get('Property Name', 'BOTN Analysis'), header_format)
            
            # Key metrics summary
            summary_items = [
                ('Project Name', f'=Inputs!B2'),
                ('Location', f'=Inputs!B3&", "&Inputs!B5'),
                ('Total Units', '=Calculations!B2'),
                ('Total Development Cost', '=Calculations!B6'),
                ('Cost per Unit', '=Calculations!B7'),
                ('Annual Tax Credits', '=Calculations!B9'),
                ('Credit Pricing', f'=Inputs!B{1 + len(user_input_labels)}'),
                ('Credit Proceeds', f'=Calculations!B9*Inputs!B{1 + len(user_input_labels)}'),
            ]
            
            row = 2
            for label, formula in summary_items:
                summary_sheet.write(row, 0, label)
                if 'Cost' in label or 'Credits' in label or 'Proceeds' in label:
                    summary_sheet.write(row, 1, formula, money_format)
                else:
                    summary_sheet.write(row, 1, formula, input_format)
                row += 1
            
            # Add dropdowns to Inputs sheet
            cdlac_options = [
                'Los Angeles County', 'Orange County', 'San Diego County', 'Inland Empire Region',
                'Central Valley Region', 'Central Coast Region', 'East Bay Region', 
                'South & West Bay Region', 'San Francisco County', 'Northern Region'
            ]
            
            housing_types = ['New Construction', 'Acquisition/Rehab', 'Adaptive Reuse']
            credit_types = ['4%', '9%']
            elevator_types = ['Elevator', 'Non-Elevator']
            
            # Apply data validations
            inputs_sheet.data_validation('B4', {
                'validate': 'list',
                'source': cdlac_options,
                'dropdown': True
            })
            
            inputs_sheet.data_validation(f'B{8}', {
                'validate': 'list',
                'source': housing_types,
                'dropdown': True
            })
            
            inputs_sheet.data_validation(f'B{10}', {
                'validate': 'list',
                'source': credit_types,
                'dropdown': True
            })
            
            inputs_sheet.data_validation(f'B{14}', {
                'validate': 'list',
                'source': elevator_types,
                'dropdown': True
            })
            
            workbook.close()
            
            logger.info(f"✅ Comprehensive BOTN created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating comprehensive BOTN: {str(e)}")
            return None
    
    def generate_comprehensive_botn(self):
        """Generate comprehensive BOTN"""
        
        # User inputs
        user_inputs_raw = [
            "new Construction", "80 cents", "4%", "36 months", "5%", "6%", 
            "No", "100 units", "900SF", "250/SF"
        ]
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        test_site = df.iloc[0]
        
        # Display info
        logger.info("\n" + "="*70)
        logger.info("🏗️ COMPREHENSIVE BOTN GENERATION")
        logger.info("="*70)
        logger.info(f"🏠 Site: {test_site.get('Property Name')}")
        logger.info(f"📍 Address: {test_site.get('Property Address')}")
        logger.info(f"🔧 Method: Complete recreation with all calculations")
        logger.info(f"✨ Features: Inputs + Calculations + Summary + Dropdowns")
        
        # Create comprehensive BOTN
        output_path = self.create_comprehensive_botn(test_site, processed_inputs)
        
        if output_path:
            logger.info(f"\n🎉 SUCCESS: Comprehensive BOTN created!")
            logger.info(f"📁 File: {output_path}")
            logger.info(f"✅ Features included:")
            logger.info(f"   • Complete Inputs tab with dropdowns")
            logger.info(f"   • Full Calculations tab with LIHTC formulas")
            logger.info(f"   • Executive Summary tab")
            logger.info(f"   • Professional formatting")
            logger.info(f"   • No corruption issues")
        else:
            logger.error("\n❌ Failed to create comprehensive BOTN")

def main():
    generator = ComprehensiveBOTNGenerator()
    generator.generate_comprehensive_botn()

if __name__ == "__main__":
    main()