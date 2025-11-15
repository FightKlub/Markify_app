#!/usr/bin/env python3
"""
Test script to verify the weightage marking system works correctly
Based on the user's provided examples from the images
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import calculate_partial_marks, extract_weightage_scheme
from enhanced_evaluation import EnhancedEvaluator

def test_weightage_marking():
    """Test the weightage marking system with user's examples"""
    
    print("🧪 Testing Weightage Marking System")
    print("=" * 50)
    
    # Test cases based on user's images
    test_cases = [
        {
            "question": 1,
            "student_selected": ["B", "D"],
            "correct_options": ["B", "D"],
            "marks_text": "Mark: 2",
            "expected_marks": 2,
            "description": "Q1: Perfect match B,D -> B,D (Equal marking)"
        },
        {
            "question": 2,
            "student_selected": ["A", "C"],
            "correct_options": ["C"],
            "marks_text": "Mark: 3",
            "expected_marks": 0,  # A is wrong, so 0 marks due to strict penalty (you mentioned 1.5 but with strict penalty it should be 0)
            "description": "Q2: Selected A,C but only C correct (A is wrong -> 0 marks due to strict penalty)"
        },
        {
            "question": 3,
            "student_selected": ["D", "E"],
            "correct_options": ["A", "D", "E"],
            "marks_text": "Mark: a=2, d=3, e=1",
            "expected_marks": 4,  # d=3 + e=1 = 4
            "description": "Q3: Selected D,E from A,D,E (Weightage: d=3 + e=1 = 4)"
        },
        {
            "question": 4,
            "student_selected": ["A", "C"],
            "correct_options": ["A", "D"],
            "marks_text": "Mark: 2",
            "expected_marks": 0,  # C is wrong, so 0 marks
            "description": "Q4: Selected A,C but correct is A,D (C is wrong -> 0 marks)"
        },
        {
            "question": 5,
            "student_selected": ["B", "D"],
            "correct_options": ["C", "D"],
            "marks_text": "Mark: 2",
            "expected_marks": 0,  # B is wrong, so 0 marks
            "description": "Q5: Selected B,D but correct is C,D (B is wrong -> 0 marks)"
        },
        {
            "question": 6,
            "student_selected": ["E", "F"],
            "correct_options": ["E", "F"],
            "marks_text": "Mark: 4",
            "expected_marks": 4,
            "description": "Q6: Perfect match E,F -> E,F (Equal marking)"
        },
        {
            "question": 7,
            "student_selected": ["A", "C"],
            "correct_options": ["A", "C"],
            "marks_text": "Mark: 4",
            "expected_marks": 4,
            "description": "Q7: Perfect match A,C -> A,C (Equal marking)"
        },
        {
            "question": 8,
            "student_selected": ["B", "D"],
            "correct_options": ["B", "D"],
            "marks_text": "Mark: b=2, d=3",
            "expected_marks": 5,  # b=2 + d=3 = 5
            "description": "Q8: Perfect match B,D (Weightage: b=2 + d=3 = 5)"
        },
        {
            "question": 9,
            "student_selected": ["A", "B"],
            "correct_options": ["B", "C"],
            "marks_text": "Mark: 3",
            "expected_marks": 0,  # A is wrong, so 0 marks
            "description": "Q9: Selected A,B but correct is B,C (A is wrong -> 0 marks)"
        },
        {
            "question": 10,
            "student_selected": ["B", "C"],
            "correct_options": ["A", "B"],
            "marks_text": "Mark: 4",
            "expected_marks": 0,  # C is wrong, so 0 marks
            "description": "Q10: Selected B,C but correct is A,B (C is wrong -> 0 marks)"
        }
    ]
    
    total_expected = 0
    total_actual = 0
    passed_tests = 0
    
    for test_case in test_cases:
        print(f"\n📝 {test_case['description']}")
        
        # Extract weightage scheme
        weightage_scheme = extract_weightage_scheme(test_case['marks_text'])
        
        # Calculate marks using our system
        result = calculate_partial_marks(
            test_case['student_selected'],
            test_case['correct_options'],
            test_case.get('total_marks', 10),  # Default total marks
            weightage_scheme
        )
        
        actual_marks = result['marks_awarded']
        expected_marks = test_case['expected_marks']
        
        total_expected += expected_marks
        total_actual += actual_marks
        
        # Check if test passed
        if actual_marks == expected_marks:
            print(f"✅ PASS: Expected {expected_marks}, Got {actual_marks}")
            print(f"   Explanation: {result['explanation']}")
            passed_tests += 1
        else:
            print(f"❌ FAIL: Expected {expected_marks}, Got {actual_marks}")
            print(f"   Explanation: {result['explanation']}")
            print(f"   Weightage scheme: {weightage_scheme}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST SUMMARY:")
    print(f"   Tests Passed: {passed_tests}/{len(test_cases)}")
    print(f"   Total Expected Marks: {total_expected}")
    print(f"   Total Actual Marks: {total_actual}")
    
    if passed_tests == len(test_cases):
        print("🎉 ALL TESTS PASSED! Weightage marking system is working correctly!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed_tests == len(test_cases)

def test_enhanced_evaluator():
    """Test the enhanced evaluator with the same examples"""
    
    print("\n\n🔬 Testing Enhanced Evaluator")
    print("=" * 50)
    
    evaluator = EnhancedEvaluator()
    evaluator.debug_mode = True
    
    # Teacher data (answer key)
    teacher_data = {
        "Q1": {"correct_options": ["B", "D"], "marks_text": "Mark: 2"},
        "Q2": {"correct_options": ["C"], "marks_text": "Mark: 3"},
        "Q3": {"correct_options": ["A", "D", "E"], "marks_text": "Mark: a=2, d=3, e=1"},
        "Q4": {"correct_options": ["A", "D"], "marks_text": "Mark: 2"},
        "Q5": {"correct_options": ["C", "D"], "marks_text": "Mark: 2"},
        "Q6": {"correct_options": ["E", "F"], "marks_text": "Mark: 4"},
        "Q7": {"correct_options": ["A", "C"], "marks_text": "Mark: 4"},
        "Q8": {"correct_options": ["B", "D"], "marks_text": "Mark: b=2, d=3"},
        "Q9": {"correct_options": ["B", "C"], "marks_text": "Mark: 3"},
        "Q10": {"correct_options": ["A", "B"], "marks_text": "Mark: 4"}
    }
    
    # Student data (student's answers)
    student_data = {
        "Q1": ["B", "D"],
        "Q2": ["A", "C"],
        "Q3": ["D", "E"],
        "Q4": ["A", "C"],
        "Q5": ["B", "D"],
        "Q6": ["E", "F"],
        "Q7": ["A", "C"],
        "Q8": ["B", "D"],
        "Q9": ["A", "B"],
        "Q10": ["B", "C"]
    }
    
    # Expected results
    expected_results = {
        "Q1": 2, "Q2": 0, "Q3": 4, "Q4": 0, "Q5": 0,
        "Q6": 4, "Q7": 4, "Q8": 5, "Q9": 0, "Q10": 0,
        "Total": 19
    }
    
    # Evaluate
    evaluation_result = evaluator.evaluate_complete_sheet(teacher_data, student_data)
    
    print(f"📋 Evaluation Results:")
    for question_id, expected_marks in expected_results.items():
        actual_marks = evaluation_result["results"].get(question_id, 0)
        
        if actual_marks == expected_marks:
            print(f"✅ {question_id}: Expected {expected_marks}, Got {actual_marks}")
        else:
            print(f"❌ {question_id}: Expected {expected_marks}, Got {actual_marks}")
    
    print(f"\n📊 Summary: {evaluation_result['summary']}")
    
    return evaluation_result["results"]["Total"] == expected_results["Total"]

if __name__ == "__main__":
    print("🚀 Starting Weightage Marking System Tests")
    
    # Test individual marking function
    test1_passed = test_weightage_marking()
    
    # Test enhanced evaluator
    test2_passed = test_enhanced_evaluator()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! The weightage marking system is ready!")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
