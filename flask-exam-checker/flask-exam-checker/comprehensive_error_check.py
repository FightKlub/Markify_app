#!/usr/bin/env python3
"""
Comprehensive error checker for the Flask exam checker system
"""

import ast
import sys
import os
import traceback

def check_syntax_errors(file_path):
    """Check for syntax errors in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Try to parse the AST
        ast.parse(source, filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error in {file_path}: {e}"
    except Exception as e:
        return False, f"Error reading {file_path}: {e}"

def check_import_errors():
    """Check for import errors"""
    modules_to_test = [
        'app',
        'ocr_utils', 
        'utils',
        'api_key_manager',
        'enhanced_evaluation',
        'universal_mcq_evaluator',
        'universal_dynamic_evaluator'
    ]
    
    errors = []
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module} imports successfully")
        except Exception as e:
            error_msg = f"❌ {module} import failed: {e}"
            print(error_msg)
            errors.append(error_msg)
    
    return len(errors) == 0, errors

def check_flask_app():
    """Check if Flask app can be created"""
    try:
        from app import app, init_database
        print(f"✅ Flask app created: {app.name}")
        
        # Test database initialization
        try:
            db_result = init_database()
            if db_result:
                print("✅ Database initialization successful")
            else:
                print("⚠️  Database initialization failed (connection issue)")
        except Exception as e:
            print(f"⚠️  Database initialization error: {e}")
        
        return True, None
    except Exception as e:
        return False, f"Flask app creation failed: {e}"

def check_circular_imports():
    """Check for potential circular import issues"""
    try:
        # Test the problematic imports
        from utils import calculate_partial_marks
        from universal_dynamic_evaluator import UniversalDynamicEvaluator
        
        # Test if they work together
        evaluator = UniversalDynamicEvaluator()
        result = calculate_partial_marks(['A'], ['A'], 2)
        
        print("✅ No circular import issues detected")
        return True, None
    except Exception as e:
        return False, f"Circular import issue: {e}"

def main():
    """Run comprehensive error check"""
    print("🔍 COMPREHENSIVE ERROR CHECK")
    print("=" * 60)
    
    # Check syntax errors in main files
    files_to_check = [
        'app.py',
        'ocr_utils.py',
        'utils.py',
        'api_key_manager.py',
        'enhanced_evaluation.py',
        'universal_mcq_evaluator.py',
        'universal_dynamic_evaluator.py',
        'run.py'
    ]
    
    print("\n1. CHECKING SYNTAX ERRORS...")
    syntax_ok = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            ok, error = check_syntax_errors(file_path)
            if ok:
                print(f"✅ {file_path} - No syntax errors")
            else:
                print(f"❌ {file_path} - {error}")
                syntax_ok = False
        else:
            print(f"⚠️  {file_path} - File not found")
    
    print("\n2. CHECKING IMPORT ERRORS...")
    imports_ok, import_errors = check_import_errors()
    
    print("\n3. CHECKING FLASK APP...")
    flask_ok, flask_error = check_flask_app()
    if not flask_ok:
        print(f"❌ {flask_error}")
    
    print("\n4. CHECKING CIRCULAR IMPORTS...")
    circular_ok, circular_error = check_circular_imports()
    if not circular_ok:
        print(f"❌ {circular_error}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"Syntax Check: {'✅ PASSED' if syntax_ok else '❌ FAILED'}")
    print(f"Import Check: {'✅ PASSED' if imports_ok else '❌ FAILED'}")
    print(f"Flask App Check: {'✅ PASSED' if flask_ok else '❌ FAILED'}")
    print(f"Circular Import Check: {'✅ PASSED' if circular_ok else '❌ FAILED'}")
    
    all_ok = syntax_ok and imports_ok and flask_ok and circular_ok
    
    if all_ok:
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ Your application should start successfully with: python run.py")
    else:
        print("\n❌ SOME CHECKS FAILED!")
        print("Please fix the errors above before running the application.")
        
        if import_errors:
            print("\nImport Errors:")
            for error in import_errors:
                print(f"  - {error}")
    
    return all_ok

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error checker failed: {e}")
        traceback.print_exc()
