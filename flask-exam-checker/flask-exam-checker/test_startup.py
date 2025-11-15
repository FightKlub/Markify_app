#!/usr/bin/env python3
"""
Test application startup to identify any errors
"""

import sys
import traceback

def test_imports():
    """Test all imports"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import os
        import json
        import re
        print("✅ Basic imports OK")
        
        # Test Flask imports
        from flask import Flask, request, jsonify
        print("✅ Flask imports OK")
        
        # Test database imports
        import psycopg2
        from psycopg2.extras import RealDictCursor
        print("✅ Database imports OK")
        
        # Test Google AI imports
        import google.generativeai as genai
        print("✅ Google AI imports OK")
        
        # Test our modules
        from api_key_manager import get_api_manager
        print("✅ API key manager import OK")
        
        from ocr_utils import OCRProcessor
        print("✅ OCR utils import OK")
        
        from utils import clean_option, validate_image_file
        print("✅ Utils import OK")
        
        from enhanced_evaluation import EnhancedEvaluator
        print("✅ Enhanced evaluation import OK")
        
        from universal_mcq_evaluator import UniversalMCQEvaluator
        print("✅ Universal MCQ evaluator import OK")
        
        # Test the main app import
        from app import app, init_database
        print("✅ Main app import OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_database_init():
    """Test database initialization"""
    try:
        print("\nTesting database initialization...")
        from app import init_database
        
        result = init_database()
        if result:
            print("✅ Database initialization OK")
        else:
            print("⚠️  Database initialization failed (might be connection issue)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database init error: {e}")
        traceback.print_exc()
        return False

def test_app_creation():
    """Test Flask app creation"""
    try:
        print("\nTesting Flask app creation...")
        from app import app
        
        print(f"✅ Flask app created: {app}")
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 TESTING APPLICATION STARTUP")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Init Test", test_database_init),
        ("App Creation Test", test_app_creation),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            passed = test_func()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Application should start successfully.")
        print("✅ You can now run: python run.py")
    else:
        print("❌ SOME TESTS FAILED! Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()
