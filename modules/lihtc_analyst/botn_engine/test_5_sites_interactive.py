#!/usr/bin/env python3
"""
Test 5 Sites with Interactive Input
Runs the batch processor with user inputs applied to all 5 sites
"""

from botn_final_working_batch import FinalWorkingBOTNBatch

def main():
    print("\n" + "="*70)
    print("🎯 TESTING 5 SITES WITH YOUR INPUTS")
    print("="*70)
    print("You'll enter the inputs once, and they'll be applied to all 5 sites")
    print()
    
    processor = FinalWorkingBOTNBatch()
    
    # Process exactly 5 sites with interactive inputs
    results = processor.process_batch(num_sites=5)
    
    # Results summary
    if results:
        success_rate = results['success_rate']
        print(f"\n🏆 FINAL RESULTS:")
        print(f"✅ Successful sites: {len(results['successful'])}")
        print(f"❌ Failed sites: {len(results['failed'])}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"\n🎉 EXCELLENT! Permission-free batch processing works perfectly!")
        elif success_rate >= 80:
            print(f"\n✅ GOOD! Minor issues but overall success")
        else:
            print(f"\n⚠️ Some issues need attention")
            
        print(f"\n📁 Check your output files in the 'outputs' directory")
    else:
        print("\n❌ Processing failed or was cancelled")

if __name__ == "__main__":
    main()