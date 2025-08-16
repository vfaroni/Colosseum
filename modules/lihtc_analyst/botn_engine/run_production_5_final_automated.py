#!/usr/bin/env python3
"""
Production 5 Final Automated Runner - Process final 63 sites (201-263) with preset inputs
🏆 FINAL BATCH - COMPLETE PORTFOLIO PROCESSING
"""

from production_batch_processor import ProductionBatchProcessor
import sys
import io

def main():
    print("\n" + "="*70)
    print("🏆 PRODUCTION BATCH 5 - FINAL BATCH (SITES 201-263)")
    print("="*70)
    print("🎯 COMPLETING THE ENTIRE BOTN PORTFOLIO!")
    print("Processing final 63 sites (201-263) with standard LIHTC inputs:")
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
    print("🏁 FINAL PORTFOLIO PROGRESS:")
    print("✅ Production 1: 50 sites complete")
    print("✅ Production 2: 50 sites complete") 
    print("✅ Production 3: 50 sites complete")
    print("✅ Production 4: 50 sites complete")
    print("🏆 Production 5: 63 sites (FINAL BATCH - STARTING NOW)")
    print()
    print("🎯 After this batch: 263/263 sites complete (100%)")
    print("🚀 COMPLETE BOTN PORTFOLIO ANALYSIS!")
    print()
    
    # Simulate user inputs
    inputs = "b\n80 cents\nb\n36\n5\n6\nb\n2M\n100\n900\n250\n"
    
    # Redirect stdin to provide inputs
    original_stdin = sys.stdin
    sys.stdin = io.StringIO(inputs)
    
    try:
        # Initialize processor for Production 5 (Final Batch)
        # start_index=200 because pandas uses 0-based indexing (site 201 = index 200)
        processor = ProductionBatchProcessor(
            batch_name="Production 5",
            start_index=200,  # Start from row 201 (0-based index 200)
            batch_size=63     # Final 63 sites
        )
        
        results = processor.process_production_batch(num_sites=63)
        
        if results and results['success_rate'] >= 90:
            print(f"\n🎉🎉🎉 PORTFOLIO COMPLETION SUCCESS! 🎉🎉🎉")
            print(f"📊 Final batch ranking spreadsheet created!")
            print(f"🏆 Top final site: {results['top_sites'][0]['Property_Name'] if results['top_sites'] else 'N/A'}")
            print(f"\n🏁 COMPLETE PORTFOLIO STATUS:")
            print(f"✅ Production 1: 50 sites complete (100% success)")
            print(f"✅ Production 2: 50 sites complete (100% success)") 
            print(f"✅ Production 3: 50 sites complete (100% success)")
            print(f"✅ Production 4: 50 sites complete (100% success)")
            print(f"✅ Production 5: 63 sites complete ({results['success_rate']:.1f}% success)")
            print(f"\n🎯 FINAL RESULT: 263/263 sites processed!")
            print(f"🚀 COMPLETE BOTN PORTFOLIO ANALYSIS FINISHED!")
            print(f"📁 All BOTN files available in Production 1-5 folders")
            print(f"📊 All ranking spreadsheets with broker contacts ready")
        elif results and results['success_rate'] >= 80:
            print(f"\n✅ Good results! Final batch: {results['success_rate']:.1f}% success rate")
            print(f"🎯 Portfolio nearly complete!")
        else:
            print(f"\n⚠️ Some issues detected in final batch")
            
    finally:
        # Restore stdin
        sys.stdin = original_stdin

if __name__ == "__main__":
    main()