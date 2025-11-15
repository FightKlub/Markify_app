#!/usr/bin/env python3
"""
Test script to verify JSON parsing fixes
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_utils import OCRProcessor

def test_json_fixes():
    """Test the JSON fixing methods"""
    print("🧪 Testing JSON Parsing Fixes")
    print("=" * 50)
    
    # Initialize OCR processor
    processor = OCRProcessor()
    
    # Test cases with problematic JSON
    test_cases = [
        {
            "name": "Malformed JSON with extra quotes",
            "json": '{ "total_questions": 10, "answers": [ { "question_number": 1, "correct_options": ["B", "D"], "marks": 2, "marks_text": ""mark" : 2", "question_type": "multiple" } ] }',
            "expected_keys": ["total_questions", "answers"]
        },
        {
            "name": "Incomplete JSON",
            "json": '{ "roll_number": "48", "section": "A", "answers": [ {"question_number": 1, "selected_options": ["B", "D", "E"]}, {"question_number": 2, "selected_options": ["A", "C", "E"]}',
            "expected_keys": ["roll_number", "section", "answers"]
        },
        {
            "name": "JSON with trailing comma",
            "json": '{ "total_questions": 5, "answers": [{"question_number": 1, "correct_options": ["A"],}], }',
            "expected_keys": ["total_questions", "answers"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Original JSON: {test_case['json'][:100]}...")
        
        try:
            # Try standard JSON parsing first
            try:
                result = json.loads(test_case['json'])
                print("   ✅ Standard JSON parsing worked")
            except json.JSONDecodeError:
                print("   ❌ Standard JSON parsing failed")
                
                # Try our fix method
                fixed_json = processor._fix_json_response(test_case['json'])
                print(f"   Fixed JSON: {fixed_json[:100]}...")
                
                try:
                    result = json.loads(fixed_json)
                    print("   ✅ Fixed JSON parsing worked")
                except json.JSONDecodeError:
                    print("   ⚠️ Fixed JSON still failed, trying aggressive fix...")
                    result = processor._aggressive_json_fix(test_case['json'])
                    if result:
                        print("   ✅ Aggressive JSON fix worked")
                    else:
                        print("   ❌ All JSON fixes failed")
                        continue
            
            # Validate result structure
            if isinstance(result, dict):
                found_keys = list(result.keys())
                expected_keys = test_case['expected_keys']
                
                if all(key in found_keys for key in expected_keys):
                    print(f"   ✅ All expected keys found: {expected_keys}")
                else:
                    print(f"   ⚠️ Missing keys. Found: {found_keys}, Expected: {expected_keys}")
                
                if 'answers' in result and isinstance(result['answers'], list):
                    print(f"   📊 Found {len(result['answers'])} answers")
            else:
                print(f"   ❌ Result is not a dict: {type(result)}")
                
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 JSON Fix Testing Complete!")

if __name__ == "__main__":
    test_json_fixes()
