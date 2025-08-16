#!/usr/bin/env python3
"""
Automatic CTCAC Extractor Patcher
Safely patches your comprehensive extractor with the unit mix and basis/credits fixes
NO MANUAL EDITING REQUIRED!
"""

import re
from pathlib import Path
from datetime import datetime

def main():
    print("🔧 AUTOMATIC CTCAC EXTRACTOR PATCHER")
    print("=" * 60)
    print("This script will automatically fix your comprehensive extractor")
    print("by replacing the broken unit mix and basis/credits methods.")
    print("=" * 60)
    
    # Find your comprehensive extractor file
    current_dir = Path.cwd()
    
    # Look for your comprehensive extractor
    candidates = [
        'enhanced_ctcac_extractor_complete-2.py',
        'enhanced_ctcac_extractor_complete.py', 
        'enhanced_ctcac_extractor_fixed-2.py'
    ]
    
    target_file = None
    for candidate in candidates:
        file_path = current_dir / candidate
        if file_path.exists():
            target_file = file_path
            break
    
    if not target_file:
        print("❌ Could not find your comprehensive extractor file!")
        print("Looking for one of these files:")
        for candidate in candidates:
            print(f"   - {candidate}")
        print("\nPlease make sure the file is in the current directory.")
        return
    
    print(f"✅ Found target file: {target_file.name}")
    
    # Read the original file
    print(f"📖 Reading original file...")
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        print(f"✅ Successfully read {len(original_content)} characters")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = current_dir / f"{target_file.stem}_BACKUP_{timestamp}.py"
    
    print(f"💾 Creating backup: {backup_file.name}")
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ Backup created successfully")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return
    
    # Apply patches
    print(f"🔧 Applying patches...")
    patched_content = original_content
    patches_applied = 0
    
    # Patch 1: Fix unit mix extraction
    print("   🏠 Patching unit mix extraction method...")
    unit_mix_pattern = r'def extract_detailed_unit_mix\(self, sheet\).*?(?=\n    def |\n\nclass |\nclass |\Z)'
    unit_mix_replacement = '''def extract_detailed_unit_mix(self, sheet) -> Dict[str, Any]:
        """FIXED: Extract detailed unit mix information from Application sheet"""
        try:
            unit_mix = {
                'total_units': None,
                'affordable_units': None,
                'market_rate_units': None,
                'unit_types': {},
                'ami_levels': {},
                'rent_schedule': {},
                'unit_mix_table': []
            }
            
            self.logger.info("   🏠 FIXED unit mix extraction...")
            
            # FIXED: Search in the correct area where data actually exists
            search_ranges = [
                (710, 730),  # Primary search area for unit mix tables
                (690, 710),  # Secondary area for 9% applications  
                (730, 750)   # Extended area for variations
            ]
            
            for start_row, end_row in search_ranges:
                self.logger.info(f"     Searching rows {start_row}-{end_row}...")
                
                for row in range(start_row, end_row + 1):
                    # Check column B for unit types
                    unit_cell = self.get_cell_value(sheet, f'B{row}')
                    
                    if unit_cell and isinstance(unit_cell, str):
                        unit_lower = unit_cell.lower().strip()
                        
                        # FIXED: More precise unit type matching
                        if any(pattern in unit_lower for pattern in [
                            '1 bedroom', '2 bedroom', '3 bedroom', '4 bedroom', '5 bedroom',
                            'studio', 'efficiency'
                        ]):
                            unit_type = unit_cell.strip()
                            self.logger.info(f"       Found unit type at B{row}: '{unit_type}'")
                            
                            # FIXED: Extract from correct columns
                            unit_count = None
                            rent_amount = None
                            square_feet = None
                            utility_allowance = None
                            
                            # Column G has unit count
                            g_value = self.get_cell_value(sheet, f'G{row}')
                            if isinstance(g_value, (int, float)) and 1 <= g_value <= 500:
                                unit_count = int(g_value)
                            
                            # Column K has rent amount  
                            k_value = self.get_cell_value(sheet, f'K{row}')
                            if isinstance(k_value, (int, float)) and 200 <= k_value <= 5000:
                                rent_amount = float(k_value)
                            
                            # Column O has square footage
                            o_value = self.get_cell_value(sheet, f'O{row}')
                            if isinstance(o_value, (int, float)) and 300 <= o_value <= 3000:
                                square_feet = int(o_value)
                            
                            # Column T has utility allowance
                            t_value = self.get_cell_value(sheet, f'T{row}')
                            if isinstance(t_value, (int, float)) and 10 <= t_value <= 500:
                                utility_allowance = float(t_value)
                            
                            # Store data if found
                            if unit_count and unit_count > 0:
                                unit_mix['unit_types'][unit_type] = unit_count
                                self.logger.info(f"         ✅ {unit_type}: {unit_count} units")
                                
                                if rent_amount:
                                    unit_mix['rent_schedule'][unit_type] = {
                                        'base_rent': rent_amount,
                                        'utility_allowance': utility_allowance,
                                        'total_rent': rent_amount + (utility_allowance or 0),
                                        'square_feet': square_feet
                                    }
                                    self.logger.info(f"            Rent: ${rent_amount}, Utilities: ${utility_allowance}")
                
                # If we found data, don't search other ranges
                if unit_mix['unit_types']:
                    break
            
            # Calculate total units
            if unit_mix['unit_types']:
                unit_mix['total_units'] = sum(unit_mix['unit_types'].values())
                unit_mix['affordable_units'] = unit_mix['total_units']
                self.logger.info(f"     ✅ Total units: {unit_mix['total_units']}")
            
            return unit_mix
            
        except Exception as e:
            self.logger.error(f"Error extracting FIXED unit mix: {e}")
            return {}'''
    
    if re.search(unit_mix_pattern, patched_content, re.DOTALL):
        patched_content = re.sub(unit_mix_pattern, unit_mix_replacement, patched_content, flags=re.DOTALL)
        patches_applied += 1
        print("      ✅ Unit mix method patched successfully")
    else:
        print("      ❌ Could not find unit mix method to patch")
    
    # Patch 2: Fix basis/credits extraction  
    print("   🧮 Patching basis/credits extraction method...")
    basis_pattern = r'def extract_comprehensive_basis_credits\(self, workbook\).*?(?=\n    def |\n\nclass |\nclass |\Z)'
    basis_replacement = '''def extract_comprehensive_basis_credits(self, workbook) -> Dict[str, Any]:
        """FIXED: Extract comprehensive basis and credit calculations"""
        try:
            sheet_name = self.find_sheet_name(workbook, 'Basis & Credits')
            if not sheet_name:
                return {}
            
            sheet = workbook[sheet_name]
            
            basis_credits = {
                # Main calculations
                'eligible_basis': None,
                'qualified_basis': None,
                'federal_credits_annual': None,
                'state_credits_annual': None,
                'federal_credits_total': None,
                'state_credits_total': None,
                
                # Detailed breakdowns
                'basis_breakdown': {},
                'credit_calculations': {},
                'income_calculations': {},
                'operating_data': {},
                
                # Additional calculations
                'gross_rent_potential': None,
                'effective_gross_income': None,
                'operating_expenses': None,
                'net_operating_income': None
            }
            
            self.logger.info("   🧮 FIXED basis and credits extraction...")
            
            # FIXED: Enhanced search terms
            basis_terms = {
                'eligible_basis': [
                    'total eligible basis', 'eligible basis:', 'total requested unadjusted eligible basis',
                    'total adjusted eligible basis', 'aggregate eligible basis'
                ],
                'qualified_basis': [
                    'qualified basis:', 'total qualified basis', 'aggregate qualified basis'
                ],
                'federal_credits_annual': [
                    'subtotal annual federal credit', 'total combined annual federal credit',
                    'annual federal credit', 'federal credit amount'
                ],
                'federal_credits_total': [
                    'total federal credit', 'federal credit total', '10 year federal credit'
                ]
            }
            
            # FIXED: Search entire sheet with better logic
            for row in range(1, 200):
                for col in range(10):  # Columns A-J
                    col_letter = chr(65 + col)
                    cell_value = self.get_cell_value(sheet, f'{col_letter}{row}')
                    
                    if isinstance(cell_value, str):
                        cell_lower = cell_value.lower().strip()
                        
                        for key, terms in basis_terms.items():
                            if any(term in cell_lower for term in terms):
                                self.logger.info(f"       Found '{terms[0]}' at {col_letter}{row}")
                                
                                # FIXED: Search ENTIRE ROW for numeric values
                                found_value = None
                                found_cell = None
                                
                                # Check all columns in this row
                                for val_col in range(15):  # Columns A-O
                                    val_letter = chr(65 + val_col)
                                    val_cell_ref = f'{val_letter}{row}'
                                    val = self.get_cell_value(sheet, val_cell_ref)
                                    
                                    if isinstance(val, (int, float)) and val > 10000:
                                        found_value = float(val)
                                        found_cell = val_cell_ref
                                        break
                                
                                # Check nearby rows if no value found
                                if not found_value:
                                    for adj_row in [row + 1, row - 1, row + 2, row - 2]:
                                        if adj_row > 0:
                                            for val_col in range(10):
                                                val_letter = chr(65 + val_col)
                                                val_cell_ref = f'{val_letter}{adj_row}'
                                                val = self.get_cell_value(sheet, val_cell_ref)
                                                
                                                if isinstance(val, (int, float)) and val > 10000:
                                                    found_value = float(val)
                                                    found_cell = val_cell_ref
                                                    break
                                        if found_value:
                                            break
                                
                                if found_value:
                                    basis_credits[key] = found_value
                                    
                                    # Store detailed information
                                    basis_credits['credit_calculations'][f'{key}_details'] = {
                                        'source_cell': f'{col_letter}{row}',
                                        'value_cell': found_cell,
                                        'description': cell_value[:100],
                                        'amount': float(found_value)
                                    }
                                    
                                    self.logger.info(f"         ✅ Found {key}: ${found_value:,.0f} at {found_cell}")
                                    break
                        
                        if basis_credits.get(key):
                            break
            
            # FIXED: Fallback search for large amounts
            if not any(basis_credits[key] for key in ['eligible_basis', 'qualified_basis', 'federal_credits_annual']):
                self.logger.info("     Trying fallback search for large amounts...")
                
                large_amounts = []
                for row in range(1, 100):
                    for col in range(15):
                        col_letter = chr(65 + col)
                        value = self.get_cell_value(sheet, f'{col_letter}{row}')
                        
                        if isinstance(value, (int, float)) and value > 50000:
                            context_a = self.get_cell_value(sheet, f'A{row}') or ''
                            context_b = self.get_cell_value(sheet, f'B{row}') or ''
                            
                            large_amounts.append({
                                'value': value,
                                'cell': f'{col_letter}{row}',
                                'context': f"{context_a} {context_b}".lower()
                            })
                
                # Sort and auto-assign
                large_amounts.sort(key=lambda x: x['value'], reverse=True)
                
                for item in large_amounts:
                    value = item['value']
                    context = item['context']
                    
                    if not basis_credits['eligible_basis'] and value > 1000000:
                        if 'eligible' in context or value > 5000000:
                            basis_credits['eligible_basis'] = value
                            self.logger.info(f"     Auto-assigned eligible_basis: ${value:,.0f}")
                    
                    elif not basis_credits['qualified_basis'] and 500000 < value < 5000000:
                        if 'qualified' in context:
                            basis_credits['qualified_basis'] = value
                            self.logger.info(f"     Auto-assigned qualified_basis: ${value:,.0f}")
                    
                    elif not basis_credits['federal_credits_annual'] and 10000 < value < 500000:
                        if 'credit' in context or 'annual' in context:
                            basis_credits['federal_credits_annual'] = value
                            self.logger.info(f"     Auto-assigned federal_credits_annual: ${value:,.0f}")
            
            return basis_credits
            
        except Exception as e:
            self.logger.error(f"Error extracting FIXED basis and credits: {e}")
            return {}'''
    
    if re.search(basis_pattern, patched_content, re.DOTALL):
        patched_content = re.sub(basis_pattern, basis_replacement, patched_content, flags=re.DOTALL)
        patches_applied += 1
        print("      ✅ Basis/credits method patched successfully")
    else:
        print("      ❌ Could not find basis/credits method to patch")
    
    # Save patched file
    if patches_applied > 0:
        patched_file = current_dir / f"{target_file.stem}_PATCHED.py"
        print(f"💾 Saving patched file: {patched_file.name}")
        
        try:
            with open(patched_file, 'w', encoding='utf-8') as f:
                f.write(patched_content)
            print(f"✅ Patched file saved successfully")
        except Exception as e:
            print(f"❌ Error saving patched file: {e}")
            return
        
        # Summary
        print(f"\n" + "=" * 60)
        print("🎉 PATCHING COMPLETE!")
        print("=" * 60)
        print(f"✅ Applied {patches_applied}/2 patches successfully")
        print(f"📁 Original file: {target_file.name}")
        print(f"💾 Backup file: {backup_file.name}")
        print(f"🔧 Patched file: {patched_file.name}")
        
        print(f"\n🚀 TO RUN YOUR FIXED EXTRACTOR:")
        print(f"python {patched_file.name}")
        
        print(f"\n💡 WHAT WAS FIXED:")
        print("   🏠 Unit mix extraction now finds data in correct rows/columns")
        print("   🧮 Basis/credits extraction with comprehensive row scanning")
        print("   ✅ All your advanced features preserved (scoring, tie breakers, etc.)")
        
    else:
        print(f"\n❌ No patches could be applied!")
        print("The target methods were not found in the expected format.")

if __name__ == "__main__":
    main()
