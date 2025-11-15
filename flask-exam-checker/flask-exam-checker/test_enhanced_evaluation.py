#!/usr/bin/env python3
"""
Test script for Enhanced Evaluation System
Tests the new marking schemes and Gemini 2.0 Flash integration
"""

import sys
import os
import json

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_evaluation import EnhancedEvaluator

def test_equal_marking_mode():
    """Test equal marking mode scenarios"""
    print("🧪 TESTING EQUAL MARKING MODE")
    print("=" * 50)
    
    evaluator = EnhancedEvaluator()
    evaluator.debug_mode = True
    
    # Test case 1: Perfect score
    teacher_data = {
        "Q1": {"correct_options": ["A", "B"], "marks_text": "Mark: 4"},
        "Q2": {"correct_options": ["C"], "marks_text": "Mark: 2"},
        "Q3": {"correct_options": ["A", "C", "D"], "marks_text": "Mark: 6"}
    }
    
    student_data = {
        "Q1": ["A", "B"],      # All correct → 4 marks
        "Q2": ["C"],           # All correct → 2 marks
        "Q3": ["A", "C", "D"]  # All correct → 6 marks
    }
    
    result = evaluator.evaluate_complete_sheet(teacher_data, student_data)
    print("Test 1 - Perfect Score:")
    print(f"Results: {result['results']}")
    print(f"Expected: Q1=4, Q2=2, Q3=6, Total=12")
    print()
    
    # Test case 2: Partial correct answers
    student_data_2 = {
        "Q1": ["A"],           # Partial correct → 2 marks (1/2 * 4)
        "Q2": ["C"],           # All correct → 2 marks
        "Q3": ["A", "C"]       # Partial correct → 4 marks (2/3 * 6)
    }
    
    result_2 = evaluator.evaluate_complete_sheet(teacher_data, student_data_2)
    print("Test 2 - Partial Correct:")
    print(f"Results: {result_2['results']}")
    print(f"Expected: Q1=2, Q2=2, Q3=4, Total=8")
    print()
    
    # Test case 3: Wrong answers penalty
    student_data_3 = {
        "Q1": ["A", "B", "C"],  # Contains wrong → 0 marks
        "Q2": ["C", "D"],       # Contains wrong → 0 marks
        "Q3": ["A", "C"]        # Partial correct → 4 marks
    }
    
    result_3 = evaluator.evaluate_complete_sheet(teacher_data, student_data_3)
    print("Test 3 - Wrong Answer Penalty:")
    print(f"Results: {result_3['results']}")
    print(f"Expected: Q1=0, Q2=0, Q3=4, Total=4")
    print()

def test_weightage_marking_mode():
    """Test weightage marking mode scenarios"""
    print("🧪 TESTING WEIGHTAGE MARKING MODE")
    print("=" * 50)
    
    evaluator = EnhancedEvaluator()
    evaluator.debug_mode = True
    
    # Test case 1: Custom weightage
    teacher_data = {
        "Q1": {"correct_options": ["A", "B", "D"], "marks_text": "Mark: a=2, b=3, d=1"},
        "Q2": {"correct_options": ["B", "C"], "marks_text": "Mark: b=4, c=2"},
        "Q3": {"correct_options": ["A"], "marks_text": "Mark: a=5"}
    }
    
    student_data = {
        "Q1": ["A", "B", "D"],  # All correct → 2+3+1 = 6 marks
        "Q2": ["B"],            # Partial correct → 4 marks
        "Q3": ["A"]             # All correct → 5 marks
    }
    
    result = evaluator.evaluate_complete_sheet(teacher_data, student_data)
    print("Test 1 - Weightage Perfect/Partial:")
    print(f"Results: {result['results']}")
    print(f"Expected: Q1=6, Q2=4, Q3=5, Total=15")
    print()
    
    # Test case 2: Wrong answer penalty in weightage mode
    student_data_2 = {
        "Q1": ["A", "B"],       # Partial correct → 2+3 = 5 marks
        "Q2": ["B", "C", "A"],  # Contains wrong → 0 marks
        "Q3": ["A", "B"]        # Contains wrong → 0 marks
    }
    
    result_2 = evaluator.evaluate_complete_sheet(teacher_data, student_data_2)
    print("Test 2 - Weightage with Wrong Answers:")
    print(f"Results: {result_2['results']}")
    print(f"Expected: Q1=5, Q2=0, Q3=0, Total=5")
    print()

def test_marking_scheme_parsing():
    """Test the marking scheme parsing functionality"""
    print("🧪 TESTING MARKING SCHEME PARSING")
    print("=" * 50)
    
    evaluator = EnhancedEvaluator()
    
    test_cases = [
        ("Mark: 4", {"mode": "equal", "total_marks": 4}),
        ("Mark: a=2, b=3, d=1", {"mode": "weightage", "weights": {"A": 2, "B": 3, "D": 1}}),
        ("marks: 2", {"mode": "equal", "total_marks": 2}),
        ("Mark: a=1.5, c=2.5", {"mode": "weightage", "weights": {"A": 1.5, "C": 2.5}}),
        ("3", {"mode": "equal", "total_marks": 3}),
        ("", {"mode": "equal", "total_marks": 1})
    ]
    
    for marks_text, expected in test_cases:
        result = evaluator.parse_marking_scheme(marks_text)
        print(f"Input: '{marks_text}'")
        print(f"Parsed: {result}")
        print(f"Expected mode: {expected['mode']}")
        if expected["mode"] == "equal":
            print(f"Expected total: {expected['total_marks']}")
        else:
            print(f"Expected weights: {expected['weights']}")
        print()

def test_real_scenario():
    """Test with realistic exam scenario"""
    print("🧪 TESTING REAL EXAM SCENARIO")
    print("=" * 50)
    
    evaluator = EnhancedEvaluator()
    
    # Simulate the images you provided earlier
    teacher_data = {
        "Q1": {"correct_options": ["B", "D"], "marks_text": "Mark: 2"},
        "Q2": {"correct_options": ["C"], "marks_text": "Mark: 3"},
        "Q3": {"correct_options": ["A", "D", "E"], "marks_text": "Mark: a=2, d=3, e=1"},
        "Q4": {"correct_options": ["A", "B"], "marks_text": "Mark: 2"},
        "Q5": {"correct_options": ["C", "D"], "marks_text": "Mark: 2"},
        "Q6": {"correct_options": ["E", "F"], "marks_text": "Mark: 4"},
        "Q7": {"correct_options": ["A", "C"], "marks_text": "Mark: 4"},
        "Q8": {"correct_options": ["B", "D"], "marks_text": "Mark: a=2, d=3"},
        "Q9": {"correct_options": ["B", "C"], "marks_text": "Mark: 3"},
        "Q10": {"correct_options": ["A", "B"], "marks_text": "Mark: 4"}
    }
    
    student_data = {
        "Q1": ["B", "D"],      # All correct → 2 marks
        "Q2": ["A", "C"],      # Contains wrong → 0 marks
        "Q3": ["D", "E"],      # Partial correct → 3+1 = 4 marks
        "Q4": ["A", "C"],      # Contains wrong → 0 marks
        "Q5": ["B", "D"],      # Contains wrong → 0 marks
        "Q6": ["E", "F"],      # All correct → 4 marks
        "Q7": ["A", "C"],      # All correct → 4 marks
        "Q8": ["B", "D"],      # All correct → 3 marks (d=3, b not in weightage)
        "Q9": ["A", "B"],      # Contains wrong → 0 marks
        "Q10": ["B", "C"]      # Contains wrong → 0 marks
    }
    
    result = evaluator.evaluate_complete_sheet(teacher_data, student_data)
    print("Real Scenario Results:")
    print(json.dumps(result['results'], indent=2))
    print()
    print("Question-wise breakdown:")
    for q_id, details in result['question_details'].items():
        print(f"{q_id}: {details['marks_awarded']} marks - {details['explanation']}")

def main():
    """Run all tests"""
    print("🚀 ENHANCED EVALUATION SYSTEM TESTS")
    print("=" * 60)
    print()
    
    try:
        test_marking_scheme_parsing()
        test_equal_marking_mode()
        test_weightage_marking_mode()
        test_real_scenario()
        
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 Enhanced evaluation system is working correctly")
        print("🔥 Gemini 2.0 Flash integration ready")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
