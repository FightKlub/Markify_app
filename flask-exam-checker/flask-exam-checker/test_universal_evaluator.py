#!/usr/bin/env python3
"""
Test the Universal MCQ Evaluator with the user's sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from universal_mcq_evaluator import UniversalMCQEvaluator
import json

def test_user_sample_data():
    """Test with the user's exact sample data from the images"""
    
    print("🧪 Testing Universal MCQ Evaluator")
    print("=" * 50)
    
    # Teacher's answer key (from user's images)
    teacher_data = {
        "Q1": {"correct": ["B"], "marks_text": "Mark: 2"},
        "Q2": {"correct": ["C"], "marks_text": "Mark: 3"},
        "Q3": {"correct": ["A", "D", "E"], "marks_text": "mark: a=2, d=3, e=1"},
        "Q4": {"correct": ["A", "B"], "marks_text": "Mark: 2"},
        "Q5": {"correct": ["C", "D"], "marks_text": "Mark: 2"},
        "Q6": {"correct": ["E", "F"], "marks_text": "Mark: 4"},
        "Q7": {"correct": ["A", "C"], "marks_text": "Mark: 4"},
        "Q8": {"correct": ["B", "D"], "marks_text": "mark: b=2, d=3"},
        "Q9": {"correct": ["B", "C"], "marks_text": "Mark: 3"},
        "Q10": {"correct": ["A", "B"], "marks_text": "Mark: 4"}
    }
    
    # Student's answers (from user's images)
    student_data = {
        "Q1": ["B"],
        "Q2": ["A", "C"],  # A is wrong
        "Q3": ["D", "E"],  # Correct subset from A,D,E
        "Q4": ["A", "C"],  # C is wrong
        "Q5": ["B", "D", "F"],  # B,F are wrong
        "Q6": ["E"],  # Missing F (partial)
        "Q7": ["A", "C"],  # All correct
        "Q8": ["B", "D"],  # All correct
        "Q9": ["A", "B"],  # A is wrong
        "Q10": ["B", "C"]  # C is wrong
    }
    
    # Expected results based on user's requirements
    expected_results = {
        "Q1": 2,   # Full match B
        "Q2": 0,   # A is wrong (strict penalty)
        "Q3": 4,   # d=3 + e=1 = 4 (weightage)
        "Q4": 0,   # C is wrong (strict penalty)
        "Q5": 0,   # B,F are wrong (strict penalty)
        "Q6": 2,   # 1/2 correct options = 50% of 4 = 2
        "Q7": 4,   # Full match A,C
        "Q8": 5,   # b=2 + d=3 = 5 (weightage)
        "Q9": 0,   # A is wrong (strict penalty)
        "Q10": 0,  # C is wrong (strict penalty)
        "Total": 17
    }
    
    # Initialize evaluator
    evaluator = UniversalMCQEvaluator()
    
    # Perform evaluation
    results = evaluator.evaluate_mcq_sheets(teacher_data, student_data)
    
    # Display results
    print("📊 EVALUATION RESULTS:")
    print("-" * 30)
    
    total_expected = 0
    total_actual = 0
    all_correct = True
    
    for question_id in sorted([k for k in results.keys() if k.startswith('Q')]):
        expected = expected_results.get(question_id, 0)
        actual = results.get(question_id, 0)
        
        status = "✅" if expected == actual else "❌"
        if expected != actual:
            all_correct = False
        
        print(f"{question_id}: {actual} marks (expected: {expected}) {status}")
        
        total_expected += expected
        total_actual += actual
    
    print("-" * 30)
    print(f"TOTAL: {results['Total']} marks (expected: {expected_results['Total']}) {'✅' if results['Total'] == expected_results['Total'] else '❌'}")
    
    print("\n🎯 DETAILED ANALYSIS:")
    print("-" * 30)
    
    # Analyze each question
    for question_id in sorted([k for k in results.keys() if k.startswith('Q')]):
        teacher_info = teacher_data[question_id]
        student_options = student_data[question_id]
        correct_options = teacher_info['correct']
        marks_text = teacher_info['marks_text']
        
        total_marks, weightage = evaluator.parse_marking_scheme(marks_text)
        
        print(f"\n{question_id}:")
        print(f"  Student selected: {student_options}")
        print(f"  Correct options: {correct_options}")
        print(f"  Marking scheme: {marks_text}")
        print(f"  Parsed: total={total_marks}, weightage={weightage}")
        print(f"  Result: {results[question_id]} marks")
        
        # Explain the logic
        student_set = set(student_options)
        correct_set = set(correct_options)
        wrong_options = student_set - correct_set
        
        if wrong_options:
            print(f"  Logic: Wrong options {list(wrong_options)} → 0 marks (strict penalty)")
        elif student_set == correct_set:
            print(f"  Logic: Perfect match → Full marks")
        elif weightage:
            selected_weights = {opt: weightage[opt] for opt in student_set if opt in weightage}
            print(f"  Logic: Weightage sum {selected_weights} = {sum(selected_weights.values())} marks")
        else:
            proportion = len(student_set & correct_set) / len(correct_set)
            print(f"  Logic: Proportional {len(student_set & correct_set)}/{len(correct_set)} = {proportion:.2f} × {total_marks} = {results[question_id]} marks")
    
    print(f"\n{'🎉 ALL TESTS PASSED!' if all_correct else '⚠️ SOME TESTS FAILED!'}")
    print(f"Expected total: {expected_results['Total']} marks")
    print(f"Actual total: {results['Total']} marks")
    
    return results, all_correct

def test_various_formats():
    """Test with various marking scheme formats"""
    
    print("\n\n🔧 Testing Various Formats")
    print("=" * 50)
    
    evaluator = UniversalMCQEvaluator()
    
    # Test different marking scheme formats
    test_cases = [
        ("Mark: 3", 3.0, None),
        ("mark: a=2, b=1", 3.0, {"A": 2.0, "B": 1.0}),
        ("A=1.5, B=2.5", 4.0, {"A": 1.5, "B": 2.5}),
        ("a:2 b:3", 5.0, {"A": 2.0, "B": 3.0}),
        ("option a=1, option b=2", 3.0, {"A": 1.0, "B": 2.0}),
        ("4", 4.0, None),
        ("marks: 2.5", 2.5, None),
    ]
    
    for marks_text, expected_total, expected_weightage in test_cases:
        total, weightage = evaluator.parse_marking_scheme(marks_text)
        
        status_total = "✅" if abs(total - expected_total) < 0.01 else "❌"
        status_weightage = "✅" if weightage == expected_weightage else "❌"
        
        print(f"'{marks_text}' → total={total} {status_total}, weightage={weightage} {status_weightage}")

if __name__ == "__main__":
    # Test with user's sample data
    results, success = test_user_sample_data()
    
    # Test various formats
    test_various_formats()
    
    if success:
        print("\n🚀 Universal MCQ Evaluator is working perfectly!")
        print("Ready to handle ANY question paper format!")
    else:
        print("\n⚠️ Some issues found. Check the logic above.")
