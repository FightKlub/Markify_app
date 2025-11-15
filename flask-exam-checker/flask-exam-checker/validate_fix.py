#!/usr/bin/env python3
"""
Validation script to check if OCR fixes are working
"""

import sys
import os

def validate_imports():
    """Validate that all imports work correctly"""
    print("🔍 Validating imports...")
    
    try:
        from ocr_utils import OCRProcessor
        print("✅ OCRProcessor import successful")
        
        from api_key_manager import get_api_manager
        print("✅ API Key Manager import successful")
        
        from enhanced_evaluation import EnhancedEvaluator
        print("✅ Enhanced Evaluator import successful")
        
        from universal_mcq_evaluator import UniversalMCQEvaluator
        print("✅ Universal MCQ Evaluator import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def validate_ocr_processor():
    """Validate OCR processor initialization"""
    print("\n🔍 Validating OCR Processor...")
    
    try:
        from ocr_utils import OCRProcessor
        
        # Initialize processor
        processor = OCRProcessor()
        print("✅ OCR Processor initialized successfully")
        
        # Check if required methods exist
        required_methods = [
            'extract_teacher_answers',
            'extract_student_answers',
            '_process_with_gemini',
            '_try_fallback_ocr_strategies',
            '_extract_response_text'
        ]
        
        for method in required_methods:
            if hasattr(processor, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ OCR Processor validation failed: {e}")
        return False

def validate_api_manager():
    """Validate API manager"""
    print("\n🔍 Validating API Manager...")
    
    try:
        from api_key_manager import get_api_manager
        
        api_manager = get_api_manager()
        print("✅ API Manager initialized successfully")
        
        status = api_manager.get_status()
        print(f"✅ API Manager status: {status['total_keys']} keys available")
        
        return True
        
    except Exception as e:
        print(f"❌ API Manager validation failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 Starting OCR Fix Validation")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not validate_imports():
        all_passed = False
    
    # Test OCR processor
    if not validate_ocr_processor():
        all_passed = False
    
    # Test API manager
    if not validate_api_manager():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validations passed! OCR fixes are ready.")
        print("\n💡 Next steps:")
        print("1. Start the Flask app: python app.py")
        print("2. Test teacher answer key upload")
        print("3. Check for improved error handling")
    else:
        print("❌ Some validations failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
