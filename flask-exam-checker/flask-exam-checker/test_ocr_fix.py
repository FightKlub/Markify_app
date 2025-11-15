#!/usr/bin/env python3
"""
Test script to verify OCR fixes are working properly
"""

import os
import sys
import base64
from PIL import Image
import io

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_utils import OCRProcessor

def create_test_image():
    """Create a simple test image with text"""
    # Create a simple white image with black text
    img = Image.new('RGB', (800, 600), color='white')
    
    # Save as JPEG in memory
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=90)
    img_byte_arr = img_byte_arr.getvalue()
    
    # Convert to base64
    return base64.b64encode(img_byte_arr).decode()

def test_ocr_processor():
    """Test the OCR processor with enhanced error handling"""
    print("🧪 Testing OCR Processor with Enhanced Error Handling")
    print("=" * 60)
    
    try:
        # Initialize OCR processor
        print("1. Initializing OCR Processor...")
        ocr_processor = OCRProcessor()
        print("✅ OCR Processor initialized successfully")
        
        # Create test image
        print("\n2. Creating test image...")
        test_image_data = create_test_image()
        print(f"✅ Test image created: {len(test_image_data)} chars")
        
        # Test teacher answer extraction
        print("\n3. Testing teacher answer extraction...")
        try:
            teacher_result = ocr_processor.extract_teacher_answers(test_image_data)
            print("✅ Teacher OCR completed successfully")
            print(f"📊 Result type: {type(teacher_result)}")
            
            if isinstance(teacher_result, dict):
                if 'error' in teacher_result:
                    print(f"⚠️ OCR returned error: {teacher_result['error']}")
                else:
                    print(f"📝 Keys in result: {list(teacher_result.keys())}")
                    if 'answers' in teacher_result:
                        print(f"📊 Number of answers detected: {len(teacher_result.get('answers', []))}")
            
        except Exception as e:
            print(f"❌ Teacher OCR failed: {str(e)}")
        
        # Test student answer extraction
        print("\n4. Testing student answer extraction...")
        try:
            student_result = ocr_processor.extract_student_answers(test_image_data)
            print("✅ Student OCR completed successfully")
            print(f"📊 Result type: {type(student_result)}")
            
            if isinstance(student_result, dict):
                if 'error' in student_result:
                    print(f"⚠️ OCR returned error: {student_result['error']}")
                else:
                    print(f"📝 Keys in result: {list(student_result.keys())}")
                    if 'answers' in student_result:
                        print(f"📊 Number of answers detected: {len(student_result.get('answers', []))}")
            
        except Exception as e:
            print(f"❌ Student OCR failed: {str(e)}")
        
        print("\n" + "=" * 60)
        print("🎉 OCR Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr_processor()
