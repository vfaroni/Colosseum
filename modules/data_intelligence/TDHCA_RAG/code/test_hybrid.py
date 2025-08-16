  from hybrid_extraction_orchestrator import HybridExtractionOrchestrator
  from pathlib import Path

  base_path = "/Users/williamrice/Library/CloudStorage/Dropbox-HERR/Bill Rice/Structured Consultants/AI 
  Projects/TDHCA_RAG/D'Marco_Sites"
  orchestrator = HybridExtractionOrchestrator(base_path)

  # Test with the PDF we know works
  test_file = Path(base_path) / "Successful_2023_Applications" / "Dallas_Fort_Worth" /
  "TDHCA_23461_Estates_at_Ferguson.pdf"

  print(f"Looking for: {test_file}")
  print(f"File exists: {test_file.exists()}")

  if test_file.exists():
      print(f"Testing with: {test_file.name}")
      result = orchestrator.extract_hybrid(test_file)
      if result:
          print(f"Success! Project: {result.project_data.project_name}")
      else:
          print("Extraction failed")
  else:
      print("Test file not found!")
      # Let's see what's actually in the directory
      base_dir = Path(base_path)
      if base_dir.exists():
          print(f"Base directory exists, contents:")
          for item in base_dir.iterdir():
              print(f"  {item.name}")
  EOF

  python3 test_hybrid.py






