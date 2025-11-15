#!/usr/bin/env python3
"""
Test the specific Q2 case from memory requirements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import calculate_partial_marks, extract_weightage_scheme

def test_q2_case():
    """Test Q2: Student selected A,C but only C correct, so 1 wrong = 0 marks"""
    print("Testing Q2 case from memory...")
    
    student_options = ["A", "C"]  # Student selected A and C
    correct_options = ["C"]       # Only C is correct
    marks_text = "Mark: 3"        # Equal marking, 3 marks total
    
    print(f"Student selected: {student_options}")
    print(f"Correct options: {correct_options}")
    print(f"Marks text: {marks_text}")
    
    # Extract weightage scheme (should be None for equal marking)
    weightage_scheme = extract_weightage_scheme(marks_text)
    print(f"Weightage scheme: {weightage_scheme}")
    
    # Calculate total marks
    total_marks = 3  # From marks_text
    
    # Calculate marks
    result = calculate_partial_marks(
        student_options, 
        correct_options, 
        total_marks, 
        weightage_scheme
    )
    
    print(f"Result: {result}")
    print(f"Marks awarded: {result['marks_awarded']}")
    print(f"Explanation: {result['explanation']}")
    
    # Should be 0 because A is wrong (strict penalty)
    expected = 0
    actual = result['marks_awarded']
    
    if actual == expected:
        print(f"✅ Q2 Test PASSED: Got {actual} marks (expected {expected})")
        return True
    else:
        print(f"❌ Q2 Test FAILED: Got {actual} marks (expected {expected})")
        return False

if __name__ == "__main__":
    test_q2_case()
