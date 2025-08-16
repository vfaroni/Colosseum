#!/usr/bin/env python3
"""
Excel Session Manager - Permission-Free XLWings Handler
Comprehensive Excel session management with all permission prompts suppressed
"""

import xlwings as xw
import logging
import time
from contextlib import contextmanager
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelSessionManager:
    """Manage Excel sessions with comprehensive permission suppression"""
    
    def __init__(self):
        self.app = None
        self.session_active = False
    
    def start_session(self):
        """Start Excel session with all permission prompts disabled"""
        
        try:
            logger.info("🔧 Starting Excel session with permission suppression...")
            
            # Create Excel app with comprehensive settings
            self.app = xw.App(visible=False, add_book=False)
            
            # Comprehensive permission and prompt suppression
            self.app.display_alerts = False           # Suppress all alert dialogs
            self.app.screen_updating = False          # Disable screen updates for speed
            self.app.enable_events = False            # Disable event handlers
            
            # Try to set interactive mode (Windows only)
            try:
                self.app.interactive = False              # Disable user interaction
            except Exception:
                logger.debug("Interactive mode setting not supported on this platform")
            
            # Additional COM automation settings (with better error handling)
            try:
                self.app.api.DisplayAlerts = False
                self.app.api.ScreenUpdating = False  
                self.app.api.EnableEvents = False
                self.app.api.Visible = False
                
            except AttributeError as e:
                logger.debug(f"Some Excel API properties not available: {e}")
            
            # Try additional dialog suppression (Windows specific)
            try:
                self.app.api.Interactive = False
                self.app.api.AskToUpdateLinks = False
                self.app.api.AlertBeforeOverwriting = False
                
            except (AttributeError, Exception) as e:
                logger.debug(f"Advanced dialog suppression not available: {e}")
            
            self.session_active = True
            logger.info("✅ Excel session started with full permission suppression")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Excel session: {str(e)}")
            self.session_active = False
            raise
    
    def open_workbook(self, file_path, **kwargs):
        """Open workbook with permission suppression"""
        
        if not self.session_active:
            raise RuntimeError("Excel session not active. Call start_session() first.")
        
        # Default parameters to suppress prompts
        open_params = {
            'update_links': False,                    # Don't update external links
            'read_only': False,                       # Allow modifications
            'ignore_read_only_recommended': True,     # Ignore read-only recommendations
            'password': '',                           # Empty password
            'write_res_password': '',                 # Empty write password
        }
        
        # Override with any user-provided parameters
        open_params.update(kwargs)
        
        try:
            logger.debug(f"Opening workbook: {Path(file_path).name}")
            wb = self.app.books.open(str(file_path), **open_params)
            return wb
            
        except Exception as e:
            logger.error(f"❌ Failed to open {Path(file_path).name}: {str(e)}")
            raise
    
    def close_session(self):
        """Close Excel session safely"""
        
        if self.app and self.session_active:
            try:
                # Close all open workbooks first
                for wb in list(self.app.books):
                    try:
                        wb.close()
                    except:
                        pass
                
                # Quit Excel application
                self.app.quit()
                logger.info("🔧 Excel session closed successfully")
                
            except Exception as e:
                logger.warning(f"⚠️ Error closing Excel session: {str(e)}")
            
            finally:
                self.app = None
                self.session_active = False
    
    def __enter__(self):
        """Context manager entry"""
        self.start_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_session()


@contextmanager 
def excel_session():
    """Context manager for Excel sessions"""
    session = ExcelSessionManager()
    try:
        session.start_session()
        yield session
    finally:
        session.close_session()


class BatchWorkbookProcessor:
    """Process multiple workbooks in a single Excel session"""
    
    def __init__(self, session_manager=None):
        self.session = session_manager or ExcelSessionManager()
        self.processed_files = []
        self.failed_files = []
    
    def process_workbooks(self, file_paths, processing_function):
        """
        Process multiple workbooks with a single Excel session
        
        Args:
            file_paths: List of file paths to process
            processing_function: Function that takes (workbook, file_path) and processes it
        """
        
        logger.info(f"🔄 Starting batch processing of {len(file_paths)} workbooks...")
        
        # Start session if not already active
        if not self.session.session_active:
            self.session.start_session()
        
        for i, file_path in enumerate(file_paths, 1):
            try:
                logger.info(f"📝 Processing {i}/{len(file_paths)}: {Path(file_path).name}")
                
                # Open workbook with permission suppression
                wb = self.session.open_workbook(file_path)
                
                # Process the workbook
                processing_function(wb, file_path)
                
                # Save and close
                wb.save()
                wb.close()
                
                self.processed_files.append(file_path)
                
                # Brief pause every 10 files to prevent COM issues
                if i % 10 == 0:
                    time.sleep(0.1)
                    logger.info(f"   ✅ Completed {i}/{len(file_paths)} files")
                
            except Exception as e:
                logger.error(f"   ❌ Failed {Path(file_path).name}: {str(e)}")
                self.failed_files.append({'path': file_path, 'error': str(e)})
                
                # Try to close workbook if it's still open
                try:
                    if 'wb' in locals():
                        wb.close()
                except:
                    pass
                
                continue
        
        # Final summary
        logger.info(f"\n🏆 Batch processing complete!")
        logger.info(f"✅ Successful: {len(self.processed_files)}")
        logger.info(f"❌ Failed: {len(self.failed_files)}")
        
        return {
            'successful': self.processed_files,
            'failed': self.failed_files,
            'success_rate': len(self.processed_files) / len(file_paths) * 100
        }


def test_permission_suppression():
    """Test that Excel session works without permission prompts"""
    
    logger.info("🧪 Testing Excel permission suppression...")
    
    try:
        with excel_session() as session:
            logger.info("✅ Excel session created without prompts")
            
            # Test that we can access Excel properties
            logger.info(f"   Excel version: {session.app.version}")
            logger.info(f"   Display alerts: {session.app.display_alerts}")
            logger.info(f"   Screen updating: {session.app.screen_updating}")
            
        logger.info("🎉 Permission suppression test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Permission suppression test failed: {str(e)}")
        return False


if __name__ == "__main__":
    test_permission_suppression()