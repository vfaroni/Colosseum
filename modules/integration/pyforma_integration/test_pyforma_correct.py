#!/usr/bin/env python3
"""
Test pyforma with correct import pattern
"""

def test_pyforma_correct_import():
    """Test pyforma with various import patterns"""
    print("Testing different pyforma import patterns...")
    
    # Try different import methods
    import_methods = [
        ("import pyforma.pyforma", "pyforma.pyforma"),
        ("from pyforma import pyforma", "pyforma"),
        ("import pyforma", "pyforma")
    ]
    
    for import_statement, module_name in import_methods:
        try:
            print(f"\nTrying: {import_statement}")
            exec(import_statement)
            
            # Get the module object
            if module_name == "pyforma.pyforma":
                import pyforma.pyforma as pf
            elif module_name == "pyforma":
                from pyforma import pyforma as pf
            else:
                import pyforma as pf
            
            # List available functions
            functions = [attr for attr in dir(pf) if not attr.startswith('_') and callable(getattr(pf, attr))]
            print(f"✅ Import successful! Available functions:")
            for func in functions[:10]:  # Show first 10
                print(f"  - {func}")
            
            # Try to find the main function
            likely_functions = [f for f in functions if 'proforma' in f.lower() or 'spot' in f.lower()]
            if likely_functions:
                print(f"  Likely pro forma functions: {likely_functions}")
            
            return pf, True
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return None, False

def test_basic_functionality(pf):
    """Test basic functionality once we have the correct module"""
    print("\nTesting basic functionality...")
    
    try:
        # Get all callable functions
        functions = [attr for attr in dir(pf) if not attr.startswith('_') and callable(getattr(pf, attr))]
        print(f"All available functions: {functions}")
        
        # Look for likely pro forma function
        main_function = None
        for func_name in functions:
            if 'proforma' in func_name.lower() or 'spot' in func_name.lower():
                main_function = func_name
                break
        
        if not main_function and functions:
            # Try the first function
            main_function = functions[0]
        
        if main_function:
            print(f"Testing function: {main_function}")
            func = getattr(pf, main_function)
            
            # Get function signature/docstring
            doc = getattr(func, '__doc__', 'No documentation')
            print(f"Function documentation: {doc[:200]}...")
            
            return True
        else:
            print("❌ No suitable functions found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing functionality: {e}")
        return False

if __name__ == "__main__":
    print("pyforma Correct Import Test")
    print("=" * 50)
    
    pf, success = test_pyforma_correct_import()
    
    if success and pf:
        test_basic_functionality(pf)
    else:
        print("❌ Unable to import pyforma correctly")