#!/usr/bin/env python3
"""
Production 3 Batch Runner - Process sites 101-150
Continuing from Production 1 (sites 1-50) and Production 2 (sites 51-100)
"""

from production_batch_processor import ProductionBatchProcessor

def main():
    print("\n" + "="*70)
    print("🏭 PRODUCTION BATCH 3 - SITES 101-150")
    print("="*70)
    print("Processing sites 101-150 from the BOTN portfolio")
    print("Previous batches completed:")
    print("• Production 1: Sites 1-50 ✅")
    print("• Production 2: Sites 51-100 ✅") 
    print("• Production 3: Sites 101-150 (STARTING NOW)")
    print()
    
    # Initialize processor for Production 3
    # start_index=100 because pandas uses 0-based indexing (site 101 = index 100)
    processor = ProductionBatchProcessor(
        batch_name="Production 3",
        start_index=100,  # Start from row 101 (0-based index 100)
        batch_size=50
    )
    
    print("This will process 50 sites and create:")
    print("• 50 individual BOTN Excel files in Production 3 folder")
    print("• Comprehensive ranking spreadsheet with broker contacts")
    print("• Development opportunity scores for each site")
    print()
    
    results = processor.process_production_batch(num_sites=50)
    
    if results and results['success_rate'] >= 90:
        print(f"\n🎉 EXCELLENT! Production 3 batch completed successfully!")
        print(f"📊 Check your ranking spreadsheet for broker contact information")
        print(f"🏆 Top site: {results['top_sites'][0]['Property_Name'] if results['top_sites'] else 'N/A'}")
        print(f"\n📈 PORTFOLIO PROGRESS:")
        print(f"✅ Production 1: 50 sites complete")
        print(f"✅ Production 2: 50 sites complete") 
        print(f"✅ Production 3: 50 sites complete")
        print(f"⏳ Remaining: 113 sites (Production 4: 50 sites, Production 5: 63 sites)")
    elif results and results['success_rate'] >= 80:
        print(f"\n✅ Good results! {results['success_rate']:.1f}% success rate")
    else:
        print(f"\n⚠️ Some issues detected")

if __name__ == "__main__":
    main()