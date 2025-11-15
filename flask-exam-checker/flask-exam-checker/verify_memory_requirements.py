#!/usr/bin/env python3
"""
Verify that the memory requirements are correctly implemented
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import calculate_partial_marks, extract_weightage_scheme

def verify_memory_cases():
    """Verify all cases from memory requirements"""
    print("🔍 Verifying Memory Requirements Implementation...")
    print("=" * 60)
    
    # Test cases from memory with corrected expectations
    test_cases = [
        {
            "question": "Q1",
            "student": ["B", "D"],
            "correct": ["B", "D"], 
            "marks_text": "Mark: 2",
            "expected": 2,
            "description": "Full match"
        },
        {
            "question": "Q2", 
            "student": ["A", "C"],
            "correct": ["C"],
            "marks_text": "Mark: 3",
            "expected": 0,  # A is wrong, so 0 marks (strict penalty)
            "description": "A is wrong, strict penalty = 0 marks"
        },
        {
            "question": "Q3",
            "student": ["D", "E"],
            "correct": ["A", "D", "E"],
            "marks_text": "Mark: a=2, d=3, e=1",
            "expected": 4,  # d=3 + e=1 = 4 marks
            "description": "Weightage: d=3 + e=1 = 4 marks"
        },
        {
            "question": "Q4",
            "student": ["A", "C"],
            "correct": ["A", "D"],
            "marks_text": "Mark: 2", 
            "expected": 0,  # C is wrong, so 0 marks
            "description": "C is wrong, strict penalty = 0 marks"
        },
        {
            "question": "Q5",
            "student": ["B", "D"],
            "correct": ["C", "D"],
            "marks_text": "Mark: 2",
            "expected": 0,  # B is wrong, so 0 marks
            "description": "B is wrong, strict penalty = 0 marks"
        },
        {
            "question": "Q6",
            "student": ["E", "F"],
            "correct": ["E", "F"],
            "marks_text": "Mark: 4",
            "expected": 4,  # Full match
            "description": "Full match"
        },
        {
            "question": "Q7",
            "student": ["A", "C"],
            "correct": ["A", "C"],
            "marks_text": "Mark: 4",
            "expected": 4,  # Full match
            "description": "Full match"
        },
        {
            "question": "Q8",
            "student": ["B", "D"],
            "correct": ["B", "D"],
            "marks_text": "Mark: b=2, d=3",
            "expected": 5,  # b=2 + d=3 = 5 marks
            "description": "Weightage: b=2 + d=3 = 5 marks"
        },
        {
            "question": "Q9",
            "student": ["A", "B"],
            "correct": ["B", "C"],
            "marks_text": "Mark: 3",
            "expected": 0,  # A is wrong, so 0 marks
            "description": "A is wrong, strict penalty = 0 marks"
        },
        {
            "question": "Q10",
            "student": ["B", "C"],
            "correct": ["A", "B"],
            "marks_text": "Mark: 4",
            "expected": 0,  # C is wrong, so 0 marks
            "description": "C is wrong, strict penalty = 0 marks"
        }
    ]
    
    all_passed = True
    total_expected = 0
    total_actual = 0
    
    for test in test_cases:
        print(f"\n--- {test['question']}: {test['description']} ---")
        print(f"Student: {test['student']} | Correct: {test['correct']}")
        print(f"Marks text: {test['marks_text']}")
        
        # Extract weightage scheme
        weightage_scheme = extract_weightage_scheme(test['marks_text'])
        
        # Calculate total marks
        if weightage_scheme:
            total_marks = sum(weightage_scheme.values())
        else:
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', test['marks_text'])
            total_marks = float(match.group(1)) if match else 1
        
        # Calculate marks
        result = calculate_partial_marks(
            test['student'], 
            test['correct'], 
            total_marks, 
            weightage_scheme
        )
        
        actual_marks = result['marks_awarded']
        expected_marks = test['expected']
        
        total_expected += expected_marks
        total_actual += actual_marks
        
        if actual_marks == expected_marks:
            print(f"✅ {test['question']}: PASSED ({actual_marks} marks)")
        else:
            print(f"❌ {test['question']}: FAILED - Expected {expected_marks}, got {actual_marks}")
            print(f"   Explanation: {result['explanation']}")
            all_passed = False
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY:")
    print(f"Total Expected Marks: {total_expected}")
    print(f"Total Actual Marks: {total_actual}")
    print(f"Match: {'✅ YES' if total_expected == total_actual else '❌ NO'}")
    
    if all_passed:
        print("🎉 ALL MEMORY REQUIREMENTS CORRECTLY IMPLEMENTED!")
    else:
        print("❌ SOME MEMORY REQUIREMENTS NOT MET!")
    
    return all_passed

def test_edge_cases():
    """Test edge cases for the evaluation system"""
    print("\n🧪 Testing Edge Cases...")
    print("=" * 40)
    
    edge_cases = [
        {
            "name": "Empty student selection",
            "student": [],
            "correct": ["A", "B"],
            "marks_text": "Mark: 4",
            "expected": 0
        },
        {
            "name": "Empty correct options",
            "student": ["A"],
            "correct": [],
            "marks_text": "Mark: 2",
            "expected": 0
        },
        {
            "name": "Partial weightage selection",
            "student": ["A"],
            "correct": ["A", "B", "C"],
            "marks_text": "Mark: a=3, b=2, c=1",
            "expected": 3  # Only a=3
        },
        {
            "name": "All wrong options",
            "student": ["X", "Y"],
            "correct": ["A", "B"],
            "marks_text": "Mark: 5",
            "expected": 0
        }
    ]
    
    all_passed = True
    
    for case in edge_cases:
        print(f"\n--- {case['name']} ---")
        
        weightage_scheme = extract_weightage_scheme(case['marks_text'])
        
        if weightage_scheme:
            total_marks = sum(weightage_scheme.values())
        else:
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', case['marks_text'])
            total_marks = float(match.group(1)) if match else 1
        
        result = calculate_partial_marks(
            case['student'], 
            case['correct'], 
            total_marks, 
            weightage_scheme
        )
        
        actual = result['marks_awarded']
        expected = case['expected']
        
        if actual == expected:
            print(f"✅ PASSED: {actual} marks")
        else:
            print(f"❌ FAILED: Expected {expected}, got {actual}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE VERIFICATION OF MEMORY REQUIREMENTS")
    print("=" * 80)
    
    memory_passed = verify_memory_cases()
    edge_passed = test_edge_cases()
    
    print("\n" + "=" * 80)
    if memory_passed and edge_passed:
        print("🎉 ALL TESTS PASSED! SYSTEM IS PERFECT!")
    else:
        print("❌ SOME TESTS FAILED! NEEDS ATTENTION!")
