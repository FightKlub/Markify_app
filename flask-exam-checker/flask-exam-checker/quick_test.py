#!/usr/bin/env python3
"""Quick test to verify weightage marking system"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import calculate_partial_marks, extract_weightage_scheme

print("🧪 QUICK WEIGHTAGE TEST")
print("=" * 40)

# Test Q3: Student selected D,E from correct A,D,E with weightage a=2, d=3, e=1
print("Q3 Test:")
weightage = extract_weightage_scheme('Mark: a=2, d=3, e=1')
print(f"  Weightage extracted: {weightage}")

result = calculate_partial_marks(['D', 'E'], ['A', 'D', 'E'], 6, weightage)
print(f"  Result: {result['marks_awarded']} marks (expected: 4)")
print(f"  Explanation: {result['explanation']}")

# Test Q8: Student selected B,D from correct B,D with weightage b=2, d=3  
print("\nQ8 Test:")
weightage8 = extract_weightage_scheme('Mark: b=2, d=3')
print(f"  Weightage extracted: {weightage8}")

result8 = calculate_partial_marks(['B', 'D'], ['B', 'D'], 5, weightage8)
print(f"  Result: {result8['marks_awarded']} marks (expected: 5)")
print(f"  Explanation: {result8['explanation']}")

# Test Q2: Student selected A,C from correct C (A is wrong, should be 0)
print("\nQ2 Test:")
result2 = calculate_partial_marks(['A', 'C'], ['C'], 3, None)
print(f"  Result: {result2['marks_awarded']} marks (expected: 0)")
print(f"  Explanation: {result2['explanation']}")

print("\n🎯 Summary:")
print(f"  Q3: {'✅ PASS' if result['marks_awarded'] == 4 else '❌ FAIL'}")
print(f"  Q8: {'✅ PASS' if result8['marks_awarded'] == 5 else '❌ FAIL'}")
print(f"  Q2: {'✅ PASS' if result2['marks_awarded'] == 0 else '❌ FAIL'}")
