#!/usr/bin/env python3
"""
Deep Search Extractor - More thorough extraction for remaining fields
"""

import pandas as pd
import json
import re
from pathlib import Path

class DeepSearchExtractor:
    def __init__(self):
        self.debug_mode = True
        
    def log_debug(self, message):
        if self.debug_mode:
            print(f"DEBUG: {message}")
    
    def get_cell_value_safe(self, df, row, col):
        """Safely get cell value"""
        try:
            if 0 <= row < len(df) and 0 <= col < len(df.columns):
                value = df.iloc[row, col]
                if pd.notna(value) and str(value).strip():
                    return str(value).strip()
        except:
            pass
        return None
    
    def search_all_numeric_values(self, df, min_val, max_val, context_terms=None):
        """Find all numeric values within a range, optionally near context terms"""
        matches = []
        
        for row in range(len(df)):
            for col in range(len(df.columns)):
                cell_value = self.get_cell_value_safe(df, row, col)
                if cell_value:
                    # Try to extract number
                    try:
                        # Remove common formatting
                        clean_val = cell_value.replace(',', '').replace('$', '').replace('%', '')
                        num = float(clean_val)
                        
                        if min_val <= num <= max_val:
                            context = self.get_nearby_context(df, row, col)
                            
                            # If context terms specified, check if any are nearby
                            if context_terms:
                                context_lower = context.lower()
                                if any(term.lower() in context_lower for term in context_terms):
                                    matches.append({
                                        'value': num,
                                        'location': f"Row {row+1}, Col {chr(65+col)}",
                                        'context': context[:100],  # First 100 chars
                                        'original_text': cell_value
                                    })
                            else:
                                matches.append({
                                    'value': num,
                                    'location': f"Row {row+1}, Col {chr(65+col)}",
                                    'context': context[:100],
                                    'original_text': cell_value
                                })
                    except:
                        pass
        
        return matches
    
    def get_nearby_context(self, df, center_row, center_col, radius=3):
        """Get text context around a cell"""
        context_parts = []
        
        for row in range(max(0, center_row - radius), min(len(df), center_row + radius + 1)):
            for col in range(max(0, center_col - radius), min(len(df.columns), center_col + radius + 1)):
                value = self.get_cell_value_safe(df, row, col)
                if value:
                    context_parts.append(value)
        
        return " ".join(context_parts)
    
    def find_square_footage_deep(self, file_path):
        """Deep search for square footage values"""
        try:
            df = pd.read_excel(file_path, sheet_name="Application", header=None)
            
            # Search for numbers in square footage range with context
            sqft_context_terms = [
                'square', 'sq', 'footage', 'ft', 'area', 'residential', 
                'low income', 'affordable', 'dwelling', 'unit', 'floor'
            ]
            
            # Look for values between 10,000 and 1,000,000 sq ft
            matches = self.search_all_numeric_values(df, 10000, 1000000, sqft_context_terms)
            
            self.log_debug(f"Found {len(matches)} potential square footage values:")
            for i, match in enumerate(matches[:10]):  # Show first 10
                self.log_debug(f"  {i+1}. {match['value']:,.0f} at {match['location']} - Context: {match['context']}")
            
            # Score matches based on context relevance
            scored_matches = []
            for match in matches:
                score = 0
                context_lower = match['context'].lower()
                
                # Higher scores for better context
                if 'low income' in context_lower:
                    score += 10
                if 'residential' in context_lower:
                    score += 8
                if 'square' in context_lower or 'sq' in context_lower:
                    score += 15
                if 'footage' in context_lower or 'ft' in context_lower:
                    score += 12
                if 'total' in context_lower:
                    score += 5
                if 'unit' in context_lower:
                    score += 3
                
                # Penalty for irrelevant context
                if any(bad_term in context_lower for bad_term in ['cost', 'dollar', '$', 'fee', 'price']):
                    score -= 5
                
                match['score'] = score
                if score > 5:  # Only keep reasonably relevant matches
                    scored_matches.append(match)
            
            # Sort by score and return best match
            scored_matches.sort(key=lambda x: x['score'], reverse=True)
            
            if scored_matches:
                best = scored_matches[0]
                self.log_debug(f"Best square footage match: {best['value']:,.0f} (score: {best['score']}) - {best['context']}")
                return int(best['value'])
            
            return 0
            
        except Exception as e:
            self.log_debug(f"Error in square footage search: {e}")
            return 0
    
    def find_construction_costs_deep(self, file_path):
        """Deep search for construction costs"""
        try:
            df = pd.read_excel(file_path, sheet_name="Sources and Uses Budget", header=None)
            
            # Search for large dollar amounts (construction costs are usually millions)
            construction_context_terms = [
                'construction', 'hard cost', 'building', 'development', 
                'improvement', 'new', 'total', 'direct'
            ]
            
            # Look for values between $1M and $100M
            matches = self.search_all_numeric_values(df, 1000000, 100000000, construction_context_terms)
            
            self.log_debug(f"Found {len(matches)} potential construction cost values:")
            for i, match in enumerate(matches[:10]):
                self.log_debug(f"  {i+1}. ${match['value']:,.0f} at {match['location']} - Context: {match['context']}")
            
            # Score construction cost matches
            scored_matches = []
            for match in matches:
                score = 0
                context_lower = match['context'].lower()
                
                if 'construction' in context_lower:
                    score += 20
                if 'hard cost' in context_lower:
                    score += 15
                if 'building' in context_lower:
                    score += 10
                if 'total' in context_lower and 'construction' in context_lower:
                    score += 25
                if 'new construction' in context_lower:
                    score += 30
                
                # Penalty for other cost types
                if any(bad_term in context_lower for bad_term in ['land', 'soft', 'fee', 'architectural', 'engineering']):
                    score -= 10
                
                match['score'] = score
                if score > 10:
                    scored_matches.append(match)
            
            scored_matches.sort(key=lambda x: x['score'], reverse=True)
            
            if scored_matches:
                best = scored_matches[0]
                self.log_debug(f"Best construction cost match: ${best['value']:,.0f} (score: {best['score']}) - {best['context']}")
                return best['value']
            
            return 0
            
        except Exception as e:
            self.log_debug(f"Error in construction cost search: {e}")
            return 0
    
    def analyze_all_costs(self, file_path):
        """Analyze all cost-related values in Sources and Uses Budget"""
        try:
            df = pd.read_excel(file_path, sheet_name="Sources and Uses Budget", header=None)
            
            # Find all potential dollar amounts
            cost_matches = self.search_all_numeric_values(df, 1000, 100000000)  # $1K to $100M
            
            print(f"\n=== ALL POTENTIAL COSTS IN SOURCES & USES BUDGET ===")
            print(f"Found {len(cost_matches)} potential cost values:")
            
            # Group by value ranges
            ranges = {
                'Small costs ($1K-$100K)': [],
                'Medium costs ($100K-$1M)': [],
                'Large costs ($1M-$10M)': [],
                'Very large costs ($10M+)': []
            }
            
            for match in cost_matches:
                val = match['value']
                if val < 100000:
                    ranges['Small costs ($1K-$100K)'].append(match)
                elif val < 1000000:
                    ranges['Medium costs ($100K-$1M)'].append(match)
                elif val < 10000000:
                    ranges['Large costs ($1M-$10M)'].append(match)
                else:
                    ranges['Very large costs ($10M+)'].append(match)
            
            for range_name, matches in ranges.items():
                if matches:
                    print(f"\n{range_name}: {len(matches)} values")
                    for match in matches[:5]:  # Show first 5 in each range
                        print(f"  ${match['value']:,.0f} at {match['location']} - {match['context'][:80]}...")
            
        except Exception as e:
            self.log_debug(f"Error analyzing costs: {e}")

def test_deep_search():
    """Test deep search extraction"""
    source_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-Personal/Structured Consultants/AI Projects/CTCAC_RAG/raw_data"
    test_file = Path(source_dir) / "2024_4pct_R1_24-409.xlsx"
    
    if test_file.exists():
        extractor = DeepSearchExtractor()
        
        print("="*70)
        print("DEEP SEARCH ANALYSIS - MARINA TOWERS")
        print("="*70)
        
        # Find square footage
        print("\n--- SEARCHING FOR SQUARE FOOTAGE ---")
        sqft = extractor.find_square_footage_deep(test_file)
        print(f"Final square footage result: {sqft:,} sq ft")
        
        # Find construction costs
        print("\n--- SEARCHING FOR CONSTRUCTION COSTS ---")
        construction_cost = extractor.find_construction_costs_deep(test_file)
        print(f"Final construction cost result: ${construction_cost:,.0f}")
        
        # Analyze all costs
        extractor.analyze_all_costs(test_file)
        
        # Summary
        print(f"\n" + "="*70)
        print("DEEP SEARCH SUMMARY")
        print("="*70)
        print(f"Square Footage: {sqft:,} sq ft")
        print(f"Construction Cost: ${construction_cost:,.0f}")
        
    else:
        print(f"File not found: {test_file}")

if __name__ == "__main__":
    test_deep_search()