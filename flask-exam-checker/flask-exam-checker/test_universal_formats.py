#!/usr/bin/env python3
"""
Test the universal system with EVERY possible question paper format
Proves the system is NOT predefined but truly universal
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from universal_dynamic_evaluator import UniversalDynamicEvaluator

def test_all_formats():
    """Test EVERY possible question paper format"""
    evaluator = UniversalDynamicEvaluator()
    
    print("🌍 TESTING UNIVERSAL FORMAT SUPPORT")
    print("=" * 80)
    print("Proving the system works for ANY format, not just predefined cases!")
    print("=" * 80)
    
    # Test cases covering EVERY possible format
    test_cases = [
        {
            "name": "Standard Letters (A-Z)",
            "teacher": {"Q1": {"correct_options": ["A", "C"], "marks_text": "Mark: 4"}},
            "student": {"Q1": ["A", "C"]},
            "expected": 4,
            "description": "Most common format"
        },
        {
            "name": "Numbers (1-10)",
            "teacher": {"Q1": {"correct_options": ["1", "3", "5"], "marks_text": "6 marks"}},
            "student": {"Q1": ["1", "3"]},
            "expected": 4,  # 2/3 * 6 = 4
            "description": "Numeric options"
        },
        {
            "name": "Roman Numerals",
            "teacher": {"Q1": {"correct_options": ["I", "III"], "marks_text": "total: 8"}},
            "student": {"Q1": ["I", "III"]},
            "expected": 8,
            "description": "Roman numeral options"
        },
        {
            "name": "Parentheses Format",
            "teacher": {"Q1": {"correct_options": ["(a)", "(d)"], "marks_text": "Mark: 5"}},
            "student": {"Q1": ["(a)", "(d)"]},
            "expected": 5,
            "description": "Options in parentheses"
        },
        {
            "name": "Brackets Format",
            "teacher": {"Q1": {"correct_options": ["[A]", "[C]"], "marks_text": "4 points"}},
            "student": {"Q1": ["[A]", "[C]"]},
            "expected": 4,
            "description": "Options in brackets"
        },
        {
            "name": "Mixed Format",
            "teacher": {"Q1": {"correct_options": ["A", "2", "III"], "marks_text": "Mark: 9"}},
            "student": {"Q1": ["A", "2", "III"]},
            "expected": 9,
            "description": "Mixed letters, numbers, romans"
        },
        {
            "name": "Complex Weightage - Letters",
            "teacher": {"Q1": {"correct_options": ["A", "B", "D"], "marks_text": "Mark: a=3, b=2, d=4"}},
            "student": {"Q1": ["A", "B"]},
            "expected": 5,  # a=3 + b=2 = 5
            "description": "Weightage with letters"
        },
        {
            "name": "Complex Weightage - Numbers",
            "teacher": {"Q1": {"correct_options": ["1", "3", "4"], "marks_text": "1=2, 3=3, 4=1"}},
            "student": {"Q1": ["1", "3"]},
            "expected": 5,  # 1=2 + 3=3 = 5
            "description": "Weightage with numbers"
        },
        {
            "name": "Strict Penalty Test - Letters",
            "teacher": {"Q1": {"correct_options": ["B", "D"], "marks_text": "Mark: 6"}},
            "student": {"Q1": ["B", "D", "F"]},  # F is wrong
            "expected": 0,
            "description": "Wrong option penalty"
        },
        {
            "name": "Strict Penalty Test - Numbers",
            "teacher": {"Q1": {"correct_options": ["2", "4"], "marks_text": "Mark: 8"}},
            "student": {"Q1": ["2", "4", "7"]},  # 7 is wrong
            "expected": 0,
            "description": "Wrong option penalty with numbers"
        },
        {
            "name": "Partial Weightage Selection",
            "teacher": {"Q1": {"correct_options": ["A", "C", "E"], "marks_text": "a=1.5, c=2.5, e=3"}},
            "student": {"Q1": ["C", "E"]},
            "expected": 5.5,  # c=2.5 + e=3 = 5.5
            "description": "Partial weightage with decimals"
        },
        {
            "name": "Large Number Options",
            "teacher": {"Q1": {"correct_options": ["12", "15", "18"], "marks_text": "Mark: 12"}},
            "student": {"Q1": ["12", "15"]},
            "expected": 8,  # 2/3 * 12 = 8
            "description": "Large number options"
        },
        {
            "name": "Single Character vs Multi-Character",
            "teacher": {"Q1": {"correct_options": ["A", "BB", "C3"], "marks_text": "Mark: 6"}},
            "student": {"Q1": ["A", "BB"]},
            "expected": 4,  # 2/3 * 6 = 4
            "description": "Mixed single and multi-character"
        },
        {
            "name": "Case Insensitive",
            "teacher": {"Q1": {"correct_options": ["a", "C"], "marks_text": "Mark: 4"}},
            "student": {"Q1": ["A", "c"]},
            "expected": 4,
            "description": "Case insensitive matching"
        },
        {
            "name": "Complex Marking Text",
            "teacher": {"Q1": {"correct_options": ["A", "B"], "marks_text": "For option A give 3 marks, for B give 2 marks"}},
            "student": {"Q1": ["A"]},
            "expected": 3,  # Only A selected
            "description": "Natural language marking"
        },
        {
            "name": "Reverse Weightage Pattern",
            "teacher": {"Q1": {"correct_options": ["X", "Y"], "marks_text": "3 points for X, 4 points for Y"}},
            "student": {"Q1": ["Y"]},
            "expected": 4,  # Only Y selected
            "description": "Reverse pattern detection"
        },
        {
            "name": "No Selection",
            "teacher": {"Q1": {"correct_options": ["A", "B"], "marks_text": "Mark: 5"}},
            "student": {"Q1": []},
            "expected": 0,
            "description": "Empty selection"
        },
        {
            "name": "All Wrong Options",
            "teacher": {"Q1": {"correct_options": ["A", "B"], "marks_text": "Mark: 5"}},
            "student": {"Q1": ["X", "Y", "Z"]},
            "expected": 0,
            "description": "All selections wrong"
        },
        {
            "name": "Unicode Options",
            "teacher": {"Q1": {"correct_options": ["α", "β"], "marks_text": "Mark: 6"}},
            "student": {"Q1": ["α", "β"]},
            "expected": 6,
            "description": "Unicode characters"
        },
        {
            "name": "Very Large Weightage",
            "teacher": {"Q1": {"correct_options": ["A", "B"], "marks_text": "A=100, B=200"}},
            "student": {"Q1": ["B"]},
            "expected": 200,
            "description": "Large weightage values"
        }
    ]
    
    all_passed = True
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test {i}/{total_tests}: {test['name']} ---")
        print(f"Description: {test['description']}")
        
        try:
            result = evaluator.evaluate_complete_paper(test['teacher'], test['student'])
            actual = result['results']['Q1']
            expected = test['expected']
            
            if abs(actual - expected) < 0.01:  # Allow for floating point precision
                print(f"✅ PASSED: {actual} marks (expected {expected})")
                passed_tests += 1
            else:
                print(f"❌ FAILED: Got {actual} marks, expected {expected}")
                print(f"   Details: {result['question_details']['Q1']['explanation']}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 80)
    print(f"📊 UNIVERSAL FORMAT TEST RESULTS:")
    print(f"Passed: {passed_tests}/{total_tests} tests")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if all_passed:
        print("🎉 SYSTEM IS TRULY UNIVERSAL!")
        print("✅ Works for ANY question paper format")
        print("✅ No hardcoded assumptions")
        print("✅ Fully dynamic and adaptive")
    else:
        print("❌ Some formats not supported")
    
    return all_passed

def test_memory_requirements_universal():
    """Test that memory requirements work with universal system"""
    evaluator = UniversalDynamicEvaluator()
    
    print("\n🧠 TESTING MEMORY REQUIREMENTS WITH UNIVERSAL SYSTEM")
    print("=" * 60)
    
    # Original memory test cases
    memory_cases = [
        {"Q": "Q1", "student": ["B", "D"], "correct": ["B", "D"], "marks": "Mark: 2", "expected": 2},
        {"Q": "Q2", "student": ["A", "C"], "correct": ["C"], "marks": "Mark: 3", "expected": 0},  # A wrong
        {"Q": "Q3", "student": ["D", "E"], "correct": ["A", "D", "E"], "marks": "Mark: a=2, d=3, e=1", "expected": 4},
        {"Q": "Q4", "student": ["A", "C"], "correct": ["A", "D"], "marks": "Mark: 2", "expected": 0},  # C wrong
        {"Q": "Q5", "student": ["B", "D"], "correct": ["C", "D"], "marks": "Mark: 2", "expected": 0},  # B wrong
        {"Q": "Q6", "student": ["E", "F"], "correct": ["E", "F"], "marks": "Mark: 4", "expected": 4},
        {"Q": "Q7", "student": ["A", "C"], "correct": ["A", "C"], "marks": "Mark: 4", "expected": 4},
        {"Q": "Q8", "student": ["B", "D"], "correct": ["B", "D"], "marks": "Mark: b=2, d=3", "expected": 5},
        {"Q": "Q9", "student": ["A", "B"], "correct": ["B", "C"], "marks": "Mark: 3", "expected": 0},  # A wrong
        {"Q": "Q10", "student": ["B", "C"], "correct": ["A", "B"], "marks": "Mark: 4", "expected": 0},  # C wrong
    ]
    
    all_passed = True
    total_expected = sum(case["expected"] for case in memory_cases)
    total_actual = 0
    
    for case in memory_cases:
        teacher_data = {case["Q"]: {"correct_options": case["correct"], "marks_text": case["marks"]}}
        student_data = {case["Q"]: case["student"]}
        
        result = evaluator.evaluate_complete_paper(teacher_data, student_data)
        actual = result['results'][case["Q"]]
        expected = case["expected"]
        
        total_actual += actual
        
        if actual == expected:
            print(f"✅ {case['Q']}: {actual} marks")
        else:
            print(f"❌ {case['Q']}: Got {actual}, expected {expected}")
            all_passed = False
    
    print(f"\nTotal Expected: {total_expected} marks")
    print(f"Total Actual: {total_actual} marks")
    print(f"Match: {'✅ YES' if total_expected == total_actual else '❌ NO'}")
    
    return all_passed

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE UNIVERSAL FORMAT TESTING")
    print("Testing that the system works for ANY format, not predefined cases!")
    print("=" * 80)
    
    format_test = test_all_formats()
    memory_test = test_memory_requirements_universal()
    
    print("\n" + "=" * 80)
    print("🏆 FINAL RESULTS:")
    print(f"Universal Format Support: {'✅ PASSED' if format_test else '❌ FAILED'}")
    print(f"Memory Requirements: {'✅ PASSED' if memory_test else '❌ FAILED'}")
    
    if format_test and memory_test:
        print("\n🎉 SYSTEM IS PERFECTLY UNIVERSAL!")
        print("✅ Works for ANY question paper format")
        print("✅ No hardcoded logic")
        print("✅ Fully dynamic and adaptive")
        print("✅ Ready for real-world use")
    else:
        print("\n❌ System needs improvements")
