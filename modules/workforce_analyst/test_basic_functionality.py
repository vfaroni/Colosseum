#!/usr/bin/env python3
"""
Basic functionality test for connectivity fixes
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from session_manager import SessionManager
        print("✅ SessionManager import successful")
    except Exception as e:
        print(f"❌ SessionManager import failed: {e}")
        
    try:
        from connection_manager import ConnectionManager
        print("✅ ConnectionManager import successful")
    except Exception as e:
        print(f"❌ ConnectionManager import failed: {e}")
        
    try:
        from google_auth_manager import GoogleAuthManager
        print("✅ GoogleAuthManager import successful")
    except Exception as e:
        print(f"❌ GoogleAuthManager import failed: {e}")
        
    try:
        from app_launcher import AppLauncher
        print("✅ AppLauncher import successful")
    except Exception as e:
        print(f"❌ AppLauncher import failed: {e}")

def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("\n🧪 Testing basic functionality...")
    
    # Test SessionManager port checking
    try:
        from session_manager import SessionManager
        session_mgr = SessionManager()
        
        # Test port availability check
        available = session_mgr.is_port_available(9999)  # Likely available port
        print(f"✅ Port availability check: {available}")
        
        # Test status check
        status = session_mgr.get_session_status()
        print(f"✅ Session status check: {len(status)} fields")
        
    except Exception as e:
        print(f"❌ SessionManager basic test failed: {e}")
    
    # Test GoogleAuthManager file operations
    try:
        from google_auth_manager import GoogleAuthManager
        auth_mgr = GoogleAuthManager(
            creds_file="/tmp/test_creds.json",
            token_file="/tmp/test_token.pickle"
        )
        
        # Test save/load credentials
        test_creds = {"test": "data"}
        if auth_mgr.save_credentials(test_creds):
            loaded = auth_mgr.load_credentials()
            if loaded and loaded.get("test") == "data":
                print("✅ Credential save/load working")
            else:
                print("❌ Credential load failed")
        else:
            print("❌ Credential save failed")
            
        # Cleanup
        import os
        for file_path in ["/tmp/test_creds.json", "/tmp/test_token.pickle"]:
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        print(f"❌ GoogleAuthManager basic test failed: {e}")
    
    # Test AppLauncher basic methods
    try:
        from app_launcher import AppLauncher
        launcher = AppLauncher()
        
        # Test instruction generation
        instructions = launcher.get_startup_instructions()
        if len(instructions) > 100:
            print("✅ Startup instructions generated")
        else:
            print("❌ Startup instructions too short")
            
        # Test error suggestions
        suggestions = launcher.get_error_recovery_suggestions("timeout")
        if isinstance(suggestions, list) and len(suggestions) > 0:
            print("✅ Error recovery suggestions generated")
        else:
            print("❌ Error recovery suggestions failed")
            
    except Exception as e:
        print(f"❌ AppLauncher basic test failed: {e}")

if __name__ == "__main__":
    print("🧪 Basic Connectivity Fix Tests")
    print("=" * 40)
    
    test_imports()
    test_basic_functionality()
    
    print("\n✅ Basic tests completed")