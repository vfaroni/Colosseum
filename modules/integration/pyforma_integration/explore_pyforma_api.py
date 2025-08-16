#!/usr/bin/env python3
"""
Explore pyforma API to understand available functions and methods
"""

def explore_pyforma():
    """Examine the pyforma module to understand its API"""
    print("Exploring pyforma API...")
    
    try:
        import pyforma
        print("✅ pyforma imported successfully")
        
        # Get all attributes
        print(f"\npyforma module location: {pyforma.__file__}")
        print(f"pyforma version: {getattr(pyforma, '__version__', 'Not specified')}")
        
        # List all attributes
        attributes = [attr for attr in dir(pyforma) if not attr.startswith('_')]
        print(f"\nAvailable attributes and functions:")
        for attr in attributes:
            obj = getattr(pyforma, attr)
            obj_type = type(obj).__name__
            print(f"  {attr}: {obj_type}")
            
            # If it's a function, try to get docstring
            if callable(obj):
                doc = getattr(obj, '__doc__', None)
                if doc:
                    first_line = doc.split('\n')[0]
                    print(f"    → {first_line}")
        
        # Try to get module docstring
        module_doc = getattr(pyforma, '__doc__', None)
        if module_doc:
            print(f"\nModule documentation:")
            print(module_doc[:500] + "..." if len(module_doc) > 500 else module_doc)
            
        return True
        
    except Exception as e:
        print(f"❌ Error exploring pyforma: {e}")
        return False

if __name__ == "__main__":
    print("pyforma API Explorer")
    print("=" * 50)
    explore_pyforma()