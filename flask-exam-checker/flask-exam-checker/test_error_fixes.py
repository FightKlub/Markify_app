#!/usr/bin/env python3
"""
Test script to verify all error fixes work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import calculate_partial_marks, extract_weightage_scheme, clean_multiple_options
from enhanced_evaluation import EnhancedEvaluator
from universal_mcq_evaluator import UniversalMCQEvaluator

def test_memory_requirements():
    """Test the specific examples from memory requirements"""
    print("🧪 Testing Memory Requirements Examples...")
    
    # Test cases from memory
    test_cases = [
        {
            "question": "Q1",
            "student": ["B", "D"],
            "correct": ["B", "D"], 
            "marks_text": "Mark: 2",
            "expected": 2
        },
        {
            "question": "Q2", 
            "student": ["A", "C"],
            "correct": ["C"],
            "marks_text": "Mark: 3",
            "expected": 0  # A is wrong, so 0 marks (strict penalty)
        },
        {
            "question": "Q3",
            "student": ["D", "E"],
            "correct": ["A", "D", "E"],
            "marks_text": "Mark: a=2, d=3, e=1",
            "expected": 4  # d=3 + e=1 = 4 marks
        },
        {
            "question": "Q4",
            "student": ["A", "C"],
            "correct": ["A", "D"],
            "marks_text": "Mark: 2", 
            "expected": 0  # C is wrong, so 0 marks
        },
        {
            "question": "Q5",
            "student": ["B", "D"],
            "correct": ["C", "D"],
            "marks_text": "Mark: 2",
            "expected": 0  # B is wrong, so 0 marks
        },
        {
            "question": "Q6",
            "student": ["E", "F"],
            "correct": ["E", "F"],
            "marks_text": "Mark: 4",
            "expected": 4  # Full match
        },
        {
            "question": "Q7",
            "student": ["A", "C"],
            "correct": ["A", "C"],
            "marks_text": "Mark: 4",
            "expected": 4  # Full match
        },
        {
            "question": "Q8",
            "student": ["B", "D"],
            "correct": ["B", "D"],
            "marks_text": "Mark: b=2, d=3",
            "expected": 5  # b=2 + d=3 = 5 marks
        },
        {
            "question": "Q9",
            "student": ["A", "B"],
            "correct": ["B", "C"],
            "marks_text": "Mark: 3",
            "expected": 0  # A is wrong, so 0 marks
        },
        {
            "question": "Q10",
            "student": ["B", "C"],
            "correct": ["A", "B"],
            "marks_text": "Mark: 4",
            "expected": 0  # C is wrong, so 0 marks
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases):
        print(f"\n--- Testing {test['question']} ---")
        print(f"Student selected: {test['student']}")
        print(f"Correct options: {test['correct']}")
        print(f"Marks text: {test['marks_text']}")
        print(f"Expected marks: {test['expected']}")
        
        # Extract weightage scheme
        weightage_scheme = extract_weightage_scheme(test['marks_text'])
        print(f"Extracted weightage: {weightage_scheme}")
        
        # Calculate marks using our function
        if weightage_scheme:
            # Weightage mode - calculate total marks from scheme
            total_marks = sum(weightage_scheme.values())
        else:
            # Equal mode - extract total from marks_text
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', test['marks_text'])
            total_marks = float(match.group(1)) if match else 1
        
        result = calculate_partial_marks(
            test['student'], 
            test['correct'], 
            total_marks, 
            weightage_scheme
        )
        
        actual_marks = result['marks_awarded']
        print(f"Actual marks: {actual_marks}")
        print(f"Explanation: {result['explanation']}")
        
        if actual_marks == test['expected']:
            print(f"✅ {test['question']}: PASSED")
        else:
            print(f"❌ {test['question']}: FAILED - Expected {test['expected']}, got {actual_marks}")
            all_passed = False
    
    return all_passed

def test_weightage_extraction():
    """Test weightage scheme extraction"""
    print("\n🧪 Testing Weightage Extraction...")
    
    test_cases = [
        ("Mark: a=2, d=3, e=1", {"A": 2, "D": 3, "E": 1}),
        ("Mark: b=2, d=3", {"B": 2, "D": 3}),
        ("Mark: A=1.5, B=2.5", {"A": 1.5, "B": 2.5}),
        ("Mark: 4", None),  # Equal marking, no weightage
        ("marks: 2", None),  # Equal marking, no weightage
        ("a:2 b:3 c:1", {"A": 2, "B": 3, "C": 1}),
    ]
    
    all_passed = True
    
    for marks_text, expected in test_cases:
        result = extract_weightage_scheme(marks_text)
        print(f"Input: '{marks_text}' -> Output: {result}")
        
        if result == expected:
            print("✅ PASSED")
        else:
            print(f"❌ FAILED - Expected {expected}, got {result}")
            all_passed = False
    
    return all_passed

def test_option_cleaning():
    """Test option cleaning and normalization"""
    print("\n🧪 Testing Option Cleaning...")
    
    from utils import clean_option
    
    test_cases = [
        ("a", "A"),
        ("A", "A"), 
        ("1", "A"),  # 1 -> A
        ("2", "B"),  # 2 -> B
        ("(a)", "A"),
        ("[B]", "B"),
        ("option A", "A"),
        ("choice b", "B"),
        ("", None),
        (None, None),
    ]
    
    all_passed = True
    
    for input_val, expected in test_cases:
        result = clean_option(input_val)
        print(f"Input: '{input_val}' -> Output: '{result}'")
        
        if result == expected:
            print("✅ PASSED")
        else:
            print(f"❌ FAILED - Expected '{expected}', got '{result}'")
            all_passed = False
    
    return all_passed

def test_enhanced_evaluator():
    """Test the enhanced evaluator"""
    print("\n🧪 Testing Enhanced Evaluator...")
    
    evaluator = EnhancedEvaluator()
    
    # Test weightage mode
    teacher_data = {
        "Q3": {"correct_options": ["A", "D", "E"], "marks_text": "Mark: a=2, d=3, e=1"}
    }
    
    student_data = {
        "Q3": ["D", "E"]  # Should get d=3 + e=1 = 4 marks
    }
    
    result = evaluator.evaluate_complete_sheet(teacher_data, student_data)
    actual_marks = result["results"]["Q3"]
    expected_marks = 4
    
    print(f"Q3 result: {actual_marks} marks (expected: {expected_marks})")
    
    if actual_marks == expected_marks:
        print("✅ Enhanced Evaluator: PASSED")
        return True
    else:
        print(f"❌ Enhanced Evaluator: FAILED - Expected {expected_marks}, got {actual_marks}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Error Fix Tests...")
    print("=" * 50)
    
    tests = [
        ("Memory Requirements", test_memory_requirements),
        ("Weightage Extraction", test_weightage_extraction), 
        ("Option Cleaning", test_option_cleaning),
        ("Enhanced Evaluator", test_enhanced_evaluator),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            passed = test_func()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()
