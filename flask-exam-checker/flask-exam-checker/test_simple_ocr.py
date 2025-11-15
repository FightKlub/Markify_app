#!/usr/bin/env python3
"""
Test the new simple OCR processor
"""

import base64
from io import BytesIO
from PIL import Image
from simple_ocr_processor import SimpleOCRProcessor

def test_simple_ocr():
    """Test the simple OCR processor"""
    
    # Create test image
    img = Image.new('RGB', (800, 600), color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_data = base64.b64encode(img_byte_arr.getvalue()).decode()
    
    # Test the processor
    processor = SimpleOCRProcessor()
    
    print("🔍 Testing teacher OCR...")
    teacher_result = processor.extract_teacher_answers(image_data)
    print(f"Teacher result: {teacher_result}")
    
    print("\n🔍 Testing student OCR...")
    student_result = processor.extract_student_answers(image_data)
    print(f"Student result: {student_result}")
    
    # Test validation
    print("\n🔍 Testing validation...")
    teacher_valid, teacher_msg = processor.validate_teacher_response(teacher_result)
    student_valid, student_msg = processor.validate_student_response(student_result)
    
    print(f"Teacher validation: {teacher_valid} - {teacher_msg}")
    print(f"Student validation: {student_valid} - {student_msg}")
    
    if teacher_valid and student_valid:
        print("\n✅ Simple OCR processor working correctly!")
    else:
        print("\n❌ Issues detected with simple OCR processor")

if __name__ == "__main__":
    test_simple_ocr()
