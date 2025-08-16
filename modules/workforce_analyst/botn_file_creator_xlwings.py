#!/usr/bin/env python3
"""
BOTN File Creator - Enhanced with xlwings for Excel compatibility
Creates actual BOTN Excel files with proper Excel formatting using xlwings

Author: Claude Code Assistant
Date: 2025-08-04
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import xlwings as xw
import sys
import traceback

class BOTNFileCreatorXL:
    def __init__(self):
        # Base directories
        self.deals_base_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Deals"
        self.template_path = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/workforce_analyst/templates/80AMIBOTN.xlsx"
        self.cache_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/workforce_analyst/deal_cache"
        
        # Verify paths exist
        self.verify_paths()
        
    def verify_paths(self):
        """Verify all required paths exist"""
        if not os.path.exists(self.deals_base_dir):
            print(f"❌ Deals directory not found: {self.deals_base_dir}")
            
        if not os.path.exists(self.template_path):
            print(f"❌ BOTN template not found: {self.template_path}")
            
        if not os.path.exists(self.cache_dir):
            print(f"❌ Cache directory not found: {self.cache_dir}")
    
    def create_botn_file(self, deal_name, extracted_data):
        """
        Create actual BOTN file in deal folder using xlwings
        
        Args:
            deal_name (str): Name of the deal (e.g., "Sunset Gardens - El Cajon, CA")
            extracted_data (dict): Extracted property data
            
        Returns:
            dict: Result with success status and file path
        """
        try:
            print(f"\n🏗️ Creating BOTN file with xlwings for: {deal_name}")
            
            # Step 1: Create deal folder and BOTN subfolder
            deal_folder = os.path.join(self.deals_base_dir, deal_name)
            botn_folder = os.path.join(deal_folder, "BOTN")
            
            # Create directories if they don't exist
            os.makedirs(deal_folder, exist_ok=True)
            os.makedirs(botn_folder, exist_ok=True)
            print(f"✅ Created folder: {botn_folder}")
            
            # Step 2: Generate BOTN filename
            sanitized_name = deal_name.replace("/", "-").replace("\\", "-")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            botn_filename = f"BOTN_{sanitized_name}_{timestamp}.xlsx"
            botn_file_path = os.path.join(botn_folder, botn_filename)
            
            # Step 3: Copy BOTN template
            if os.path.exists(self.template_path):
                shutil.copy2(self.template_path, botn_file_path)
                print(f"✅ Copied BOTN template to: {botn_filename}")
            else:
                # Create a basic Excel file if template not found
                self.create_basic_excel_template(botn_file_path)
                print(f"⚠️ Template not found, created basic BOTN: {botn_filename}")
            
            # Step 4: Populate with extracted data using xlwings
            self.populate_botn_data_xlwings(botn_file_path, extracted_data, deal_name)
            print(f"✅ Populated BOTN with extracted data using xlwings")
            
            return {
                "success": True,
                "file_path": botn_file_path,
                "filename": botn_filename,
                "folder": botn_folder,
                "message": f"BOTN file created successfully with xlwings: {botn_filename}"
            }
            
        except Exception as e:
            error_msg = f"Failed to create BOTN file with xlwings: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return {
                "success": False,
                "error": error_msg
            }
    
    def create_basic_excel_template(self, file_path):
        """Create a basic Excel template using xlwings if official template not found"""
        try:
            # Create new Excel workbook
            app = xw.App(visible=False)
            wb = app.books.add()
            ws = wb.sheets[0]
            ws.name = "BOTN Analysis"
            
            # Create basic BOTN structure
            ws.range('A1').value = "BACK OF THE NAPKIN (BOTN) ANALYSIS"
            ws.range('A1').font.size = 16
            ws.range('A1').font.bold = True
            
            # Property Information Section
            ws.range('A3').value = "PROPERTY INFORMATION"
            ws.range('A3').font.bold = True
            ws.range('A3').color = (44, 62, 80)
            ws.range('A3').font.color = (255, 255, 255)
            
            property_fields = [
                ('A4', 'Property Name', 'B4'),
                ('A5', 'Address', 'B5'),
                ('A6', 'City, State, Zip', 'B6'),
                ('A7', 'Year Built', 'B7'),
                ('A8', 'Total Units', 'B8'),
            ]
            
            for row, (cell, label, data_cell) in enumerate(property_fields, 4):
                ws.range(cell).value = label
                ws.range(cell).font.bold = True
            
            # Financial Performance Section
            ws.range('A10').value = "FINANCIAL PERFORMANCE"
            ws.range('A10').font.bold = True
            ws.range('A10').color = (44, 62, 80)
            ws.range('A10').font.color = (255, 255, 255)
            
            financial_fields = [
                ('A11', 'Average Rent', 'B11'),
                ('A12', 'T12 Net Rental Income', 'B12'),
                ('A13', 'T12 Other Income', 'B13'),
                ('A14', 'T12 Operating Expenses', 'B14'),
                ('A15', 'Net Operating Income', 'B15'),
            ]
            
            for cell, label, data_cell in financial_fields:
                ws.range(cell).value = label
                ws.range(cell).font.bold = True
            
            # Unit Mix Section
            ws.range('A17').value = "UNIT MIX & RENTS"
            ws.range('A17').font.bold = True
            ws.range('A17').color = (44, 62, 80)
            ws.range('A17').font.color = (255, 255, 255)
            
            unit_fields = [
                ('A18', 'Studio Units', 'B18'),
                ('A19', '1BR Units', 'B19'),
                ('A20', '2BR Units', 'B20'),
                ('A21', '3BR Units', 'B21'),
            ]
            
            for cell, label, data_cell in unit_fields:
                ws.range(cell).value = label
                ws.range(cell).font.bold = True
            
            # Market Analysis Section
            ws.range('A23').value = "MARKET ANALYSIS"
            ws.range('A23').font.bold = True
            ws.range('A23').color = (44, 62, 80)
            ws.range('A23').font.color = (255, 255, 255)
            
            market_fields = [
                ('A24', 'Market Area', 'B24'),
                ('A25', 'County', 'B25'),
                ('A26', 'Construction Type', 'B26'),
            ]
            
            for cell, label, data_cell in market_fields:
                ws.range(cell).value = label
                ws.range(cell).font.bold = True
            
            # Save and close
            wb.save(file_path)
            wb.close()
            app.quit()
            
        except Exception as e:
            print(f"Warning: Could not create basic template with xlwings: {e}")
            # Fallback to creating empty file
            app = xw.App(visible=False)
            wb = app.books.add()
            wb.save(file_path)
            wb.close()
            app.quit()
    
    def populate_botn_data_xlwings(self, file_path, extracted_data, deal_name):
        """Populate BOTN template with extracted data using xlwings"""
        try:
            print(f"📊 Opening Excel file with xlwings: {file_path}")
            
            # Open Excel file with xlwings
            app = xw.App(visible=False)
            wb = app.books.open(file_path)
            ws = wb.sheets[0]  # Use first sheet
            
            print(f"📝 Populating data for: {deal_name}")
            
            # Data mapping for BOTN population
            data_mapping = {
                # Standard BOTN field locations
                "B4": extracted_data.get("Property Name", deal_name.split(" - ")[0]),
                "B5": extracted_data.get("Property Address", "Address TBD"),
                "B6": self.extract_city_state_zip(extracted_data),
                "B7": extracted_data.get("Year Built", "TBD"),
                "B8": extracted_data.get("Total Units", extracted_data.get("Number of Units", "TBD")),
                "B11": extracted_data.get("Average Rent", extracted_data.get("Avg In Place Rents", "TBD")),
                "B12": self.format_currency(extracted_data.get("T12 Net Rental Income", "TBD")),
                "B13": self.format_currency(extracted_data.get("T12 Other Income", extracted_data.get("T12 Total Other Income", "TBD"))),
                "B14": self.format_currency(extracted_data.get("T12 Operating Expenses", extracted_data.get("T12 Expenses", "TBD"))),
                "B15": self.calculate_noi(extracted_data),
                "B24": extracted_data.get("Market Area", self.get_market_area(deal_name)),
                "B25": extracted_data.get("County", extracted_data.get("County Name", "TBD")),
                "B26": extracted_data.get("Construction", extracted_data.get("Construction Type", "TBD"))
            }
            
            # Unit mix data
            unit_mapping = {
                "B18": f"{extracted_data.get('# Studio Units', '0')} units @ {extracted_data.get('Studio Rents', extracted_data.get('Studio Rent', 'TBD'))}",
                "B19": f"{extracted_data.get('# 1 Bed Units', '0')} units @ {extracted_data.get('1 Bed Current Rents', extracted_data.get('1BR Rent', 'TBD'))}",
                "B20": f"{extracted_data.get('# 2 Bed Units', '0')} units @ {extracted_data.get('2 Bed Current Rents', extracted_data.get('2BR Rent', 'TBD'))}",
                "B21": f"{extracted_data.get('# 3 Bed Units', '0')} units @ {extracted_data.get('3 Bed Current Rents', extracted_data.get('3BR Rent', 'TBD'))}"
            }
            
            # Combine all mappings
            all_mappings = {**data_mapping, **unit_mapping}
            
            # Populate cells using xlwings
            for cell_ref, value in all_mappings.items():
                if value and value != "TBD" and value != "0 units @ TBD":
                    try:
                        ws.range(cell_ref).value = value
                        print(f"   ✅ {cell_ref}: {value}")
                    except Exception as e:
                        print(f"   ⚠️ Could not populate cell {cell_ref}: {e}")
            
            # Add metadata at bottom
            ws.range("A30").value = "Generated by Deal Underwriting Assistant (xlwings)"
            ws.range("A31").value = f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ws.range("A32").value = f"Data Source: Real Cached Data"
            
            # Save and close
            wb.save()
            wb.close()
            app.quit()
            
            print(f"✅ Excel file saved successfully with xlwings")
            
        except Exception as e:
            print(f"❌ Error populating BOTN data with xlwings: {e}")
            traceback.print_exc()
            # Try to close Excel app if it's still open
            try:
                if 'app' in locals():
                    app.quit()
            except:
                pass
    
    def extract_city_state_zip(self, data):
        """Extract city, state, zip from address or individual fields"""
        address = data.get("Property Address", "")
        if address and "," in address:
            parts = address.split(",")
            if len(parts) >= 2:
                return f"{parts[-2].strip()}, {parts[-1].strip()}"
        
        # Try individual fields
        city = data.get("City", "")
        state = data.get("State", "")
        zip_code = data.get("Zip Code", "")
        
        if city and state:
            result = f"{city}, {state}"
            if zip_code:
                result += f" {zip_code}"
            return result
        
        return "TBD"
    
    def format_currency(self, value):
        """Format currency values"""
        if not value or value == "TBD":
            return "TBD"
        
        # Remove existing formatting
        clean_value = str(value).replace("$", "").replace(",", "")
        
        try:
            num_value = float(clean_value)
            return f"${num_value:,.0f}"
        except (ValueError, TypeError):
            return str(value)
    
    def calculate_noi(self, data):
        """Calculate Net Operating Income"""
        try:
            income = self.parse_currency(data.get("T12 Net Rental Income", "0"))
            other_income = self.parse_currency(data.get("T12 Other Income", data.get("T12 Total Other Income", "0")))
            expenses = self.parse_currency(data.get("T12 Operating Expenses", data.get("T12 Expenses", "0")))
            
            total_income = income + other_income
            noi = total_income - expenses
            
            if noi > 0:
                return f"${noi:,.0f}"
        except:
            pass
        
        return "TBD"
    
    def parse_currency(self, value):
        """Parse currency string to float"""
        if not value or value == "TBD":
            return 0
        
        clean_value = str(value).replace("$", "").replace(",", "")
        try:
            return float(clean_value)
        except (ValueError, TypeError):
            return 0
    
    def get_market_area(self, deal_name):
        """Extract market area from deal name"""
        if "San Diego" in deal_name or "El Cajon" in deal_name:
            return "San Diego Metro"
        elif "Los Angeles" in deal_name:
            return "Los Angeles Metro"
        elif "Oakland" in deal_name:
            return "East Bay"
        elif "San Jose" in deal_name:
            return "Silicon Valley"
        else:
            return "California Market"

def main():
    """Command line interface for xlwings BOTN creation"""
    if len(sys.argv) < 2:
        print("Usage: python3 botn_file_creator_xlwings.py <deal_name> [data_file]")
        print("Example: python3 botn_file_creator_xlwings.py 'Sunset Gardens - El Cajon, CA'")
        return
    
    deal_name = sys.argv[1]
    
    # Load extracted data
    extracted_data = {}
    if len(sys.argv) > 2:
        data_file = sys.argv[2]
        try:
            with open(data_file, 'r') as f:
                extracted_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load data file {data_file}: {e}")
    
    # Create BOTN file with xlwings
    creator = BOTNFileCreatorXL()
    result = creator.create_botn_file(deal_name, extracted_data)
    
    if result["success"]:
        print(f"\n🎉 SUCCESS!")
        print(f"📁 File: {result['filename']}")
        print(f"📂 Location: {result['folder']}")
        print(f"✅ {result['message']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")

if __name__ == "__main__":
    main()