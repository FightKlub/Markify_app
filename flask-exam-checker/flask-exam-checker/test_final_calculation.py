#!/usr/bin/env python3
"""
Test script to verify the weightage marking calculation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import calculate_partial_marks, extract_weightage_scheme

def test_question_3():
    """Test Q3: Student selected D,E from correct A,D,E with weightage a=2, d=3, e=1"""
    print("=== Testing Q3 ===")
    
    # Student selected: D, E
    student_options = ["D", "E"]
    
    # Correct options: A, D, E
    correct_options = ["A", "D", "E"]
    
    # Marks text from teacher answer key
    marks_text = "mark: a=2, d=3, e=1"
    
    # Extract weightage scheme
    weightage_scheme = extract_weightage_scheme(marks_text)
    print(f"Extracted weightage scheme: {weightage_scheme}")
    
    # Calculate marks
    result = calculate_partial_marks(
        student_options=student_options,
        correct_options=correct_options,
        total_marks=6,  # Total: a=2+d=3+e=1=6
        weightage_scheme=weightage_scheme
    )
    
    print(f"Student selected: {student_options}")
    print(f"Correct options: {correct_options}")
    print(f"Result: {result}")
    print(f"Expected: 4 marks (d=3 + e=1)")
    print(f"Actual: {result['marks_awarded']} marks")
    print(f"Explanation: {result['explanation']}")
    print()

def test_question_8():
    """Test Q8: Student selected B,D from correct B,D with weightage b=2, d=3"""
    print("=== Testing Q8 ===")
    
    # Student selected: B, D
    student_options = ["B", "D"]
    
    # Correct options: B, D
    correct_options = ["B", "D"]
    
    # Marks text from teacher answer key
    marks_text = "mark: b=2, d=3"
    
    # Extract weightage scheme
    weightage_scheme = extract_weightage_scheme(marks_text)
    print(f"Extracted weightage scheme: {weightage_scheme}")
    
    # Calculate marks
    result = calculate_partial_marks(
        student_options=student_options,
        correct_options=correct_options,
        total_marks=5,  # Total: b=2+d=3=5
        weightage_scheme=weightage_scheme
    )
    
    print(f"Student selected: {student_options}")
    print(f"Correct options: {correct_options}")
    print(f"Result: {result}")
    print(f"Expected: 5 marks (b=2 + d=3)")
    print(f"Actual: {result['marks_awarded']} marks")
    print(f"Explanation: {result['explanation']}")
    print()

def test_question_1():
    """Test Q1: Student selected B from correct B with equal marking"""
    print("=== Testing Q1 ===")
    
    # Student selected: B
    student_options = ["B"]
    
    # Correct options: B
    correct_options = ["B"]
    
    # No weightage scheme (equal marking)
    weightage_scheme = None
    
    # Calculate marks
    result = calculate_partial_marks(
        student_options=student_options,
        correct_options=correct_options,
        total_marks=2,
        weightage_scheme=weightage_scheme
    )
    
    print(f"Student selected: {student_options}")
    print(f"Correct options: {correct_options}")
    print(f"Result: {result}")
    print(f"Expected: 2 marks (full match)")
    print(f"Actual: {result['marks_awarded']} marks")
    print(f"Explanation: {result['explanation']}")
    print()

def test_question_2():
    """Test Q2: Student selected A,C from correct C (strict penalty)"""
    print("=== Testing Q2 ===")
    
    # Student selected: A, C
    student_options = ["A", "C"]
    
    # Correct options: C
    correct_options = ["C"]
    
    # No weightage scheme (equal marking)
    weightage_scheme = None
    
    # Calculate marks
    result = calculate_partial_marks(
        student_options=student_options,
        correct_options=correct_options,
        total_marks=3,
        weightage_scheme=weightage_scheme
    )
    
    print(f"Student selected: {student_options}")
    print(f"Correct options: {correct_options}")
    print(f"Result: {result}")
    print(f"Expected: 0 marks (A is wrong - strict penalty)")
    print(f"Actual: {result['marks_awarded']} marks")
    print(f"Explanation: {result['explanation']}")
    print()

if __name__ == "__main__":
    print("🧪 Testing Weightage Marking System")
    print("=" * 50)
    
    test_question_1()
    test_question_2()
    test_question_3()
    test_question_8()
    
    print("✅ All tests completed!")
