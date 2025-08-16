  #!/usr/bin/env python3
  import re

  def fix_prompts():
      with open('ollama_tdhca_extractor.py', 'r') as f:
          content = f.read()

      fixes = [
          ('{\n  "application_number": "5-digit number",', '{{\n  "application_number": "5-digit number",'),
          ('{\n  "street_address": "number and street name",', '{{\n  "street_address": "number and street name",'),
          ('{\n  "total_units": integer,', '{{\n  "total_units": integer,'),
          ('{\n  "total_development_cost": number,', '{{\n  "total_development_cost": number,'),
          ('{\n  "developer_name": "company name",', '{{\n  "developer_name": "company name",'),
          ('{\n  "application_date": "YYYY-MM-DD format",', '{{\n  "application_date": "YYYY-MM-DD format",'),
          ('}\n\nRules:', '}}\n\nRules:'),
          ('}\n\nText to analyze:', '}}\n\nText to analyze:'),
      ]

      for old, new in fixes:
          content = content.replace(old, new)

      with open('ollama_tdhca_extractor.py', 'w') as f:
          f.write(content)

      print("Fixed prompt formatting!")

  fix_prompts()
  EOF

  python3 fix_ollama_prompts.py
  python3 ollama_tdhca_extractor.py
