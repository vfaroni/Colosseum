#!/usr/bin/env python3
"""
Enhanced startup script for AcqUnderwriter with connectivity fixes
Handles session management, connection resilience, and Google auth persistence
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from app_launcher import launch_acq_underwriter

def main():
    """Main entry point with user-friendly interface"""
    
    print("🏢 AcqUnderwriter - Real Estate Acquisition Analysis Tool")
    print("=" * 60)
    print()
    
    # Progress callback for user feedback
    def show_progress(message):
        print(f"  {message}")
    
    print("🚀 Starting application with connectivity fixes...")
    print()
    
    try:
        # Launch with all fixes
        result = launch_acq_underwriter(progress_callback=show_progress)
        
        print()
        print("=" * 60)
        
        if result['success']:
            print("🎉 SUCCESS!")
            print()
            print(f"🌐 Your application is ready at: {result['url']}")
            print()
            print("📋 Next steps:")
            print("  1. Browser should open automatically")
            print("  2. Select a deal from your Dropbox folder")
            print("  3. Let AI extract the data")
            print("  4. Review and export to Google Sheets")
            
            if result.get('auth_ready'):
                print("  ✅ Google Sheets ready to use")
            else:
                print("  🔐 Google authentication will be required for Sheets export")
                
        else:
            print("⚠️  PARTIAL SUCCESS")
            print()
            print(f"🌐 Application started at: {result['url']}")
            print()
            print("ℹ️  If not working immediately:")
            print("  • Wait 30-60 seconds for full startup")
            print("  • Refresh your browser")
            print("  • Application may still be initializing")
            
        # Show any warnings
        if result.get('warnings'):
            print()
            print("⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"  • {warning}")
                
        # Show instructions
        if result.get('instructions'):
            print()
            print("📖 Additional Information:")
            print(result['instructions'])
            
        print()
        print("=" * 60)
        print("🔧 Need help? Check the README.md or contact support")
        print("⏹️  To stop: Press Ctrl+C in this terminal")
        
        # Keep script running so user can see the output
        try:
            print("\n⏳ Application running... Press Ctrl+C to stop")
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            
    except Exception as e:
        print(f"❌ STARTUP FAILED: {e}")
        print()
        print("🔧 Troubleshooting steps:")
        print("  1. Check Python and Streamlit installation")
        print("  2. Verify requirements: pip install -r requirements.txt")
        print("  3. Try manual start: streamlit run AcquisitionAnalyst.py")
        print("  4. Check for error details above")
        
        sys.exit(1)

if __name__ == "__main__":
    main()