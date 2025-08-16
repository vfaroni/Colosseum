#!/usr/bin/env python3
"""
CTCAC 2025 9% Application Checklist Extractor
Extracts the detailed checklist from the "Checklist Items" tab
"""

import pandas as pd
import openpyxl
from pathlib import Path
import json
import re

class CTCACChecklistExtractor:
    """Extract CTCAC application checklist with proper handling of merged cells"""
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.workbook = openpyxl.load_workbook(excel_path, data_only=True)
        self.checklist_items = []
        
    def extract_checklist(self):
        """Extract checklist from Checklist Items tab"""
        try:
            sheet = self.workbook["Checklist Items"]
        except KeyError:
            print("Error: 'Checklist Items' tab not found")
            return None
        
        print(f"Extracting from range A1:G1269...")
        
        # Get merged cell ranges for proper header handling
        merged_ranges = sheet.merged_cells.ranges
        
        current_section = ""
        current_subsection = ""
        
        for row in range(1, 1270):  # A1:G1269
            # Get cell values
            col_a = sheet[f'A{row}'].value  # Section headers
            col_b = sheet[f'B{row}'].value  # Dropdown values
            col_c = sheet[f'C{row}'].value  # Additional info
            col_d = sheet[f'D{row}'].value  # Descriptions
            col_e = sheet[f'E{row}'].value  # Additional details
            col_f = sheet[f'F{row}'].value  # Notes
            col_g = sheet[f'G{row}'].value  # References
            
            # Handle merged cells for section headers
            if col_a and str(col_a).strip():
                # Check if this is a main section header (e.g., "TAB 01")
                if "TAB" in str(col_a).upper():
                    current_section = str(col_a).strip()
                    current_subsection = ""
                elif col_a and not col_b:  # Subsection header (no dropdown)
                    current_subsection = str(col_a).strip()
            
            # Extract checklist items (rows with dropdown values)
            if col_b and str(col_b).strip():
                item = {
                    "row": row,
                    "section": current_section,
                    "subsection": current_subsection,
                    "dropdown_value": str(col_b).strip(),
                    "description": str(col_d).strip() if col_d else "",
                    "additional_details": str(col_e).strip() if col_e else "",
                    "notes": str(col_f).strip() if col_f else "",
                    "references": str(col_g).strip() if col_g else "",
                    "col_c": str(col_c).strip() if col_c else ""
                }
                self.checklist_items.append(item)
        
        print(f"Extracted {len(self.checklist_items)} checklist items")
        return self.checklist_items
    
    def filter_at_risk_items(self):
        """Filter items relevant to At-Risk acquisition-renovation projects"""
        at_risk_keywords = [
            "at-risk", "at risk", "preservation", "acquisition", "rehabilitation",
            "acquisition credit", "rehab", "renovation", "existing", "occupied"
        ]
        
        filtered_items = []
        
        for item in self.checklist_items:
            # Check if item is relevant to at-risk projects
            text_to_search = (
                item["description"] + " " + 
                item["additional_details"] + " " + 
                item["notes"] + " " +
                item["section"] + " " +
                item["subsection"]
            ).lower()
            
            # Include items that mention at-risk or acquisition/rehab
            is_at_risk_specific = any(keyword in text_to_search for keyword in at_risk_keywords)
            
            # Include all items from certain sections that are always needed
            required_sections = [
                "TAB 00", "TAB 01", "TAB 02", "TAB 05", "TAB 06", "TAB 07", "TAB 08", 
                "TAB 09", "TAB 10", "TAB 12", "TAB 13", "TAB 14", "TAB 15", "TAB 16",
                "TAB 17", "TAB 19", "TAB 20", "TAB 21", "TAB 22", "TAB 26"
            ]
            
            is_required_section = any(section in item["section"] for section in required_sections)
            
            # Exclude items that are clearly not applicable
            exclusion_keywords = [
                "new construction only", "farmworker", "special needs", "sro",
                "large family only", "tribal", "not applicable to at-risk"
            ]
            
            is_excluded = any(keyword in text_to_search for keyword in exclusion_keywords)
            
            if (is_at_risk_specific or is_required_section) and not is_excluded:
                filtered_items.append(item)
        
        print(f"Filtered to {len(filtered_items)} items relevant to At-Risk projects")
        return filtered_items
    
    def create_clickup_format(self, items):
        """Format checklist for ClickUp import"""
        
        # Define team members
        team_members = {
            "Bill Rice": "bill@structuredconsultants.com",
            "Vitor Faroni": "vitor@structuredconsultants.com", 
            "Duane Henry": "duane@structuredconsultants.com",
            "Brian Corbell": "brian@structuredconsultants.com",
            "Jason Hobson": "jason@structuredconsultants.com",
            "Andrew Sanders": "andrew@structuredconsultants.com",
            "Molly O'Dell": "molly@structuredconsultants.com",
            "Greg Howard": "greg@structuredconsultants.com",
            "Hayden Lockhart": "hayden@structuredconsultants.com",
            "Carmen Johnston": "carmen@structuredconsultants.com"
        }
        
        # Assign responsibilities based on typical roles
        responsibility_mapping = {
            "TAB 00": "Bill Rice",  # Application overview
            "TAB 01": "Duane Henry",  # Site control
            "TAB 02": "Vitor Faroni",  # Financial feasibility
            "TAB 05": "Bill Rice",  # Applicant info
            "TAB 06": "Bill Rice",  # Development team
            "TAB 07": "Vitor Faroni",  # Acquisition credits
            "TAB 08": "Brian Corbell",  # Rehabilitation
            "TAB 09": "Molly O'Dell",  # Tenant information
            "TAB 10": "Andrew Sanders",  # Project/Land/Building
            "TAB 12": "Andrew Sanders",  # Site limitations
            "TAB 13": "Jason Hobson",  # Market analysis
            "TAB 14": "Duane Henry",  # Local approvals
            "TAB 15": "Vitor Faroni",  # Financing commitments
            "TAB 16": "Vitor Faroni",  # Syndication
            "TAB 17": "Carmen Johnston",  # Subsidies
            "TAB 19": "Greg Howard",  # Eligible basis
            "TAB 20": "Carmen Johnston",  # Public funds
            "TAB 21": "Hayden Lockhart",  # GP/Mgmt characteristics
            "TAB 22": "Hayden Lockhart",  # Management experience
            "TAB 26": "Bill Rice"  # Readiness to proceed
        }
        
        clickup_tasks = []
        
        # Group items by section
        sections = {}
        for item in items:
            section = item["section"]
            if section not in sections:
                sections[section] = []
            sections[section].append(item)
        
        # Create ClickUp tasks
        for section, section_items in sections.items():
            # Determine assignee
            assignee = responsibility_mapping.get(section, "Bill Rice")
            
            # Create main section task
            section_task = {
                "name": f"CTCAC 9% At-Risk Application - {section}",
                "description": f"Complete all requirements for {section}",
                "assignee": assignee,
                "priority": "High",
                "status": "To Do",
                "folder": "CTCAC 9% At-Risk Application",
                "subtasks": []
            }
            
            # Add subtasks for each checklist item
            for item in section_items:
                subtask = {
                    "name": f"Row {item['row']}: {item['description'][:100]}...",
                    "description": f"""
**Section**: {item['section']} - {item['subsection']}
**Requirement**: {item['description']}
**Details**: {item['additional_details']}
**Notes**: {item['notes']}
**References**: {item['references']}
**Dropdown Value**: {item['dropdown_value']}
**File Location**: /Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CA_9p_2025_R2_Perris/9_Percent_Applications/{section.replace(' ', '_')}/
                    """,
                    "assignee": assignee,
                    "priority": "Medium",
                    "status": "To Do",
                    "due_date": None,  # To be set based on application timeline
                    "checklist_items": [
                        "Review requirement details",
                        "Gather required documentation", 
                        "Complete application section",
                        "Review with team lead",
                        "Submit for final review"
                    ]
                }
                section_task["subtasks"].append(subtask)
            
            clickup_tasks.append(section_task)
        
        return clickup_tasks
    
    def create_smartsheet_format(self, items):
        """Format checklist for SmartSheet import"""
        
        smartsheet_rows = []
        
        # Add header row
        headers = [
            "Section", "Subsection", "Row", "Task Name", "Description", 
            "Assignee", "Priority", "Status", "Due Date", "Notes", 
            "File Location", "Dropdown Value", "References"
        ]
        smartsheet_rows.append(headers)
        
        # Define responsibility mapping (same as ClickUp)
        responsibility_mapping = {
            "TAB 00": "Bill Rice", "TAB 01": "Duane Henry", "TAB 02": "Vitor Faroni",
            "TAB 05": "Bill Rice", "TAB 06": "Bill Rice", "TAB 07": "Vitor Faroni",
            "TAB 08": "Brian Corbell", "TAB 09": "Molly O'Dell", "TAB 10": "Andrew Sanders",
            "TAB 12": "Andrew Sanders", "TAB 13": "Jason Hobson", "TAB 14": "Duane Henry",
            "TAB 15": "Vitor Faroni", "TAB 16": "Vitor Faroni", "TAB 17": "Carmen Johnston",
            "TAB 19": "Greg Howard", "TAB 20": "Carmen Johnston", "TAB 21": "Hayden Lockhart",
            "TAB 22": "Hayden Lockhart", "TAB 26": "Bill Rice"
        }
        
        for item in items:
            assignee = responsibility_mapping.get(item["section"], "Bill Rice")
            file_location = f"/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CA_9p_2025_R2_Perris/9_Percent_Applications/{item['section'].replace(' ', '_')}/"
            
            row = [
                item["section"],
                item["subsection"],
                item["row"],
                f"{item['section']} - {item['description'][:50]}...",
                item["description"],
                assignee,
                "High" if "TAB 0" in item["section"] else "Medium",
                "Not Started",
                "",  # Due date to be filled
                item["notes"],
                file_location,
                item["dropdown_value"],
                item["references"]
            ]
            smartsheet_rows.append(row)
        
        return smartsheet_rows
    
    def save_results(self, output_dir: str):
        """Save all extracted and formatted results"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Extract all checklist items
        all_items = self.extract_checklist()
        
        # Filter for At-Risk items
        at_risk_items = self.filter_at_risk_items()
        
        # Create ClickUp format
        clickup_format = self.create_clickup_format(at_risk_items)
        
        # Create SmartSheet format
        smartsheet_format = self.create_smartsheet_format(at_risk_items)
        
        # Save raw extracted data
        with open(output_path / "ctcac_checklist_raw.json", 'w') as f:
            json.dump(all_items, f, indent=2)
        
        # Save filtered at-risk items
        with open(output_path / "ctcac_at_risk_checklist.json", 'w') as f:
            json.dump(at_risk_items, f, indent=2)
        
        # Save ClickUp format
        with open(output_path / "ctcac_clickup_format.json", 'w') as f:
            json.dump(clickup_format, f, indent=2)
        
        # Save SmartSheet format as CSV
        import csv
        with open(output_path / "ctcac_smartsheet_format.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(smartsheet_format)
        
        print(f"Results saved to {output_path}")
        print(f"Total items: {len(all_items)}")
        print(f"At-Risk relevant items: {len(at_risk_items)}")
        print(f"ClickUp tasks created: {len(clickup_format)}")
        print(f"SmartSheet rows: {len(smartsheet_format)}")
        
        return {
            "all_items": len(all_items),
            "at_risk_items": len(at_risk_items),
            "clickup_tasks": len(clickup_format),
            "smartsheet_rows": len(smartsheet_format)
        }

def main():
    excel_path = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/raw_data/Blank_Applications_2025/2025-9-percent-E-App.xlsx"
    output_dir = "/Users/williamrice/HERR Dropbox/Bill Rice/Structured Consultants/AI Projects/CTCAC_RAG/code/ctcac_checklist_output"
    
    extractor = CTCACChecklistExtractor(excel_path)
    results = extractor.save_results(output_dir)
    
    print("\nExtraction complete!")
    print(f"Files saved to: {output_dir}")

if __name__ == "__main__":
    main()