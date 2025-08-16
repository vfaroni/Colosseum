#!/usr/bin/env python3
"""
Production 4 Automated Runner - Process sites 151-200 with preset inputs
"""

from production_batch_processor import ProductionBatchProcessor
import sys
import io

def main():
    print("\n" + "="*70)
    print("🏭 PRODUCTION BATCH 4 - SITES 151-200 (AUTOMATED)")
    print("="*70)
    print("Processing sites 151-200 with standard LIHTC inputs:")
    print("• Housing Type: Large Family")
    print("• Credit Pricing: 80 cents") 
    print("• Credit Type: 9%")
    print("• Construction Loan: 36 months")
    print("• Cap Rate: 5%")
    print("• Interest Rate: 6%")
    print("• Building Type: Non-Elevator")
    print("• Purchase Price: $2M default")
    print("• Units: 100")
    print("• Unit Size: 900 SF")
    print("• Hard Cost: $250/SF")
    print()
    
    # Progress update
    print("📈 PORTFOLIO PROGRESS:")
    print("✅ Production 1: 50 sites complete")
    print("✅ Production 2: 50 sites complete") 
    print("✅ Production 3: 50 sites complete")
    print("🟡 Production 4: 50 sites (STARTING NOW)")
    print("⏳ Production 5: 63 sites remaining")
    print()
    
    # Simulate user inputs
    inputs = "b\n80 cents\nb\n36\n5\n6\nb\n2M\n100\n900\n250\n"
    
    # Redirect stdin to provide inputs
    original_stdin = sys.stdin
    sys.stdin = io.StringIO(inputs)
    
    try:
        # Initialize processor for Production 4
        # start_index=150 because pandas uses 0-based indexing (site 151 = index 150)
        processor = ProductionBatchProcessor(
            batch_name="Production 4",
            start_index=150,  # Start from row 151 (0-based index 150)
            batch_size=50
        )
        
        results = processor.process_production_batch(num_sites=50)
        
        if results and results['success_rate'] >= 90:
            print(f"\n🎉 EXCELLENT! Production 4 batch completed successfully!")
            print(f"📊 Check your ranking spreadsheet for broker contact information")
            print(f"🏆 Top site: {results['top_sites'][0]['Property_Name'] if results['top_sites'] else 'N/A'}")
            print(f"\n📈 FINAL PORTFOLIO PROGRESS:")
            print(f"✅ Production 1: 50 sites complete")
            print(f"✅ Production 2: 50 sites complete") 
            print(f"✅ Production 3: 50 sites complete")
            print(f"✅ Production 4: 50 sites complete")
            print(f"⏳ Production 5: 63 sites remaining (FINAL BATCH)")
            print(f"\n🎯 Total Progress: 200/263 sites (76% complete)")
        elif results and results['success_rate'] >= 80:
            print(f"\n✅ Good results! {results['success_rate']:.1f}% success rate")
        else:
            print(f"\n⚠️ Some issues detected")
            
    finally:
        # Restore stdin
        sys.stdin = original_stdin

if __name__ == "__main__":
    main()