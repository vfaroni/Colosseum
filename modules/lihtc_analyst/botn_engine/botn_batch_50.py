#!/usr/bin/env python3
"""
Batch 50 BOTN Generator - Process first 50 sites to verify performance
"""

from botn_mass_generator import MassBOTNGenerator
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Batch50BOTNGenerator(MassBOTNGenerator):
    """Generate BOTN for first 50 sites"""
    
    def generate_batch_50_botn(self):
        """Generate BOTN for first 50 sites"""
        
        # User inputs (these will be applied to all sites)
        user_inputs_raw = [
            "new Construction", "80 cents", "4%", "36 months", "5%", "6%", 
            "No", "100 units", "900SF", "250/SF"
        ]
        
        # Process inputs
        processed_inputs = self.process_user_inputs(user_inputs_raw)
        
        # Load site data
        final_portfolio_path = self.sites_path / "BOTN_COMPLETE_FINAL_PORTFOLIO_20250731_130415.xlsx"
        df = pd.read_excel(final_portfolio_path)
        
        # Process first 50 sites
        batch_df = df.head(50)
        
        # Display info
        logger.info("\n" + "="*70)
        logger.info("🚀 BATCH 50 BOTN GENERATION")
        logger.info("="*70)
        logger.info(f"📊 Total sites to process: {len(batch_df)}")
        logger.info(f"🔧 Method: Comprehensive BOTN with NaN handling")
        logger.info(f"✨ Features: Inputs + Calculations + Summary + Dropdowns")
        
        # Process sites
        successful_sites = []
        failed_sites = []
        
        for index, site in batch_df.iterrows():
            logger.info(f"\n🏗️ Processing site {index + 1}/{len(batch_df)}: {site.get('Property Name', 'Unknown')}")
            
            output_path = self.create_site_botn(site, processed_inputs, index + 1)
            
            if output_path:
                successful_sites.append({
                    'name': site.get('Property Name', f'Site_{index + 1}'),
                    'path': output_path
                })
                logger.info(f"   ✅ Success: {output_path.name}")
            else:
                failed_sites.append({
                    'name': site.get('Property Name', f'Site_{index + 1}'),
                    'index': index + 1
                })
                logger.error(f"   ❌ Failed: {site.get('Property Name', f'Site_{index + 1}')}")
        
        # Final summary
        logger.info(f"\n🏆 BATCH 50 BOTN GENERATION COMPLETE!")
        logger.info("="*70)
        logger.info(f"✅ Successful sites: {len(successful_sites)}")
        logger.info(f"❌ Failed sites: {len(failed_sites)}")
        logger.info(f"📁 All files saved in: {self.base_path / 'outputs'}")
        
        if successful_sites:
            logger.info(f"\n📋 FIRST 10 SUCCESSFUL SITES:")
            for site in successful_sites[:10]:
                logger.info(f"   • {site['name']}")
            if len(successful_sites) > 10:
                logger.info(f"   ... and {len(successful_sites) - 10} more")
        
        if failed_sites:
            logger.info(f"\n⚠️ FAILED SITES:")
            for site in failed_sites:
                logger.info(f"   • {site['name']} (index {site['index']})")
        
        logger.info(f"\n🎯 SUCCESS RATE: {len(successful_sites)}/{len(batch_df)} ({len(successful_sites)/len(batch_df)*100:.1f}%)")

def main():
    generator = Batch50BOTNGenerator()
    generator.generate_batch_50_botn()

if __name__ == "__main__":
    main()