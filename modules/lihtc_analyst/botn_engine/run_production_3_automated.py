#!/usr/bin/env python3
"""
Production 3 Automated Runner - Process sites 101-150 with preset inputs
"""

from production_batch_processor import ProductionBatchProcessor
import sys
import io

def main():
    print("\n" + "="*70)
    print("🏭 PRODUCTION BATCH 3 - SITES 101-150 (AUTOMATED)")
    print("="*70)
    print("Processing sites 101-150 with standard LIHTC inputs:")
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
    
    # Simulate user inputs
    inputs = "b\n80 cents\nb\n36\n5\n6\nb\n2M\n100\n900\n250\n"
    
    # Redirect stdin to provide inputs
    original_stdin = sys.stdin
    sys.stdin = io.StringIO(inputs)
    
    try:
        # Initialize processor for Production 3
        processor = ProductionBatchProcessor(
            batch_name="Production 3",
            start_index=100,  # Start from row 101 (0-based index 100)
            batch_size=50
        )
        
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
            
    finally:
        # Restore stdin
        sys.stdin = original_stdin

if __name__ == "__main__":
    main()