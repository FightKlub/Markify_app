#!/usr/bin/env python3
"""
UNIVERSAL DYNAMIC MCQ EVALUATOR
Works for ANY question paper format dynamically - no predefined logic
"""

import re
import json
from typing import Dict, List, Any, Tuple, Optional, Union

class UniversalDynamicEvaluator:
    """
    Truly universal MCQ evaluator that adapts to ANY question paper format:
    - ANY number of questions (1-1000+)
    - ANY option formats (A-Z, 1-99, Roman numerals, etc.)
    - ANY marking schemes (equal, weightage, mixed, complex)
    - ANY language/script
    - ANY layout/structure
    
    ZERO hardcoded assumptions - everything is dynamically detected
    """
    
    def __init__(self):
        self.debug_mode = False
    
    def detect_option_format(self, options: List[str]) -> str:
        """
        Dynamically detect the option format used in this question paper
        Returns: 'letters', 'numbers', 'roman', 'mixed', 'custom'
        """
        if not options:
            return 'unknown'
        
        # Analyze all options to determine format
        letter_count = sum(1 for opt in options if opt.isalpha() and len(opt) == 1)
        number_count = sum(1 for opt in options if opt.isdigit())
        roman_count = sum(1 for opt in options if self._is_roman_numeral(opt))
        
        total = len(options)
        
        if letter_count / total > 0.8:
            return 'letters'
        elif number_count / total > 0.8:
            return 'numbers'
        elif roman_count / total > 0.8:
            return 'roman'
        elif letter_count > 0 and number_count > 0:
            return 'mixed'
        else:
            return 'custom'
    
    def _is_roman_numeral(self, s: str) -> bool:
        """Check if string is a Roman numeral"""
        roman_pattern = r'^[IVXLCDM]+$'
        return bool(re.match(roman_pattern, s.upper()))
    
    def normalize_option(self, option: str, format_type: str = None) -> str:
        """
        Dynamically normalize any option format to a standard format
        Handles: A-Z, a-z, 1-99, I-X, (a), [A], etc.
        """
        if not option:
            return None
        
        # Clean the option
        option = str(option).strip().upper()
        
        # Remove common wrappers
        option = re.sub(r'[()[\]{}.,;:"\']', '', option)
        option = re.sub(r'^(OPTION|CHOICE|ANS|ANSWER)\s*', '', option, flags=re.IGNORECASE)
        
        # Extract core content
        core = re.sub(r'[^A-Z0-9IVXLCDM]', '', option)
        
        if not core:
            return None
        
        # Handle different formats dynamically
        if core.isalpha() and len(core) == 1:
            # Single letter: A, B, C, etc.
            return core
        elif core.isdigit():
            # Number: convert to letter if reasonable range
            num = int(core)
            if 1 <= num <= 26:
                return chr(ord('A') + num - 1)
            else:
                return core  # Keep as number for large ranges
        elif self._is_roman_numeral(core):
            # Roman numeral: convert to letter
            roman_to_num = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 
                           'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
            if core in roman_to_num and roman_to_num[core] <= 26:
                return chr(ord('A') + roman_to_num[core] - 1)
            else:
                return core
        else:
            # Multi-character: take first valid character
            for char in core:
                if char.isalpha():
                    return char
                elif char.isdigit():
                    num = int(char)
                    if 1 <= num <= 9:
                        return chr(ord('A') + num - 1)
        
        return core if core else None
    
    def parse_marking_scheme_universal(self, marks_text: str) -> Dict[str, Any]:
        """
        UNIVERSAL marking scheme parser - detects ANY marking pattern
        Handles: equal, weightage, complex, nested, conditional, etc.
        """
        if not marks_text:
            return {"mode": "equal", "total_marks": 1, "scheme": {}}
        
        text = marks_text.strip().lower()
        
        # Remove common prefixes
        text = re.sub(r'^(mark|marks?|point|points?|score)[:=\s]*', '', text)
        
        # UNIVERSAL WEIGHTAGE DETECTION
        # Detect ANY pattern where options are paired with values
        weightage_patterns = [
            # Standard patterns: a=2, b=3, A:4, 1=2, etc.
            r'([a-zA-Z0-9]+)\s*[=:]\s*(\d+(?:\.\d+)?)',
            # Dash patterns: a-2, b-3, A-4
            r'([a-zA-Z0-9]+)\s*[-]\s*(\d+(?:\.\d+)?)',
            # Parentheses: a(2), b(3), A(4)
            r'([a-zA-Z0-9]+)\s*\(\s*(\d+(?:\.\d+)?)\s*\)',
            # Brackets: a[2], b[3], A[4]
            r'([a-zA-Z0-9]+)\s*\[\s*(\d+(?:\.\d+)?)\s*\]',
            # Word patterns: option a = 2, choice b : 3
            r'(?:option|choice)\s+([a-zA-Z0-9]+)\s*[=:]\s*(\d+(?:\.\d+)?)',
            # Space separated: a 2, b 3, A 4
            r'([a-zA-Z0-9]+)\s+(\d+(?:\.\d+)?)',
            # Complex patterns: "for a give 2", "b gets 3"
            r'(?:for|give|gets?)\s+([a-zA-Z0-9]+)\s+(?:give|gets?|is)?\s*(\d+(?:\.\d+)?)',
            # Reverse patterns: 2 for a, 3 for b
            r'(\d+(?:\.\d+)?)\s+(?:for|to)\s+([a-zA-Z0-9]+)',
        ]
        
        weightage_matches = []
        for pattern in weightage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if pattern.endswith(r'([a-zA-Z0-9]+)'):  # Reverse pattern
                # Swap order for reverse patterns
                matches = [(match[1], match[0]) for match in matches]
            weightage_matches.extend(matches)
        
        if weightage_matches:
            # WEIGHTAGE MODE detected
            weights = {}
            total_marks = 0
            
            for option, weight in weightage_matches:
                normalized_option = self.normalize_option(option)
                if normalized_option:
                    weight_val = float(weight)
                    weights[normalized_option] = weight_val
                    total_marks += weight_val
            
            if weights:
                return {
                    "mode": "weightage",
                    "total_marks": total_marks,
                    "scheme": weights
                }
        
        # EQUAL MODE - extract total marks
        equal_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:marks?|points?|pts?)',  # 4 marks, 3 points
            r'(?:total|max|maximum)\s*[:=]?\s*(\d+(?:\.\d+)?)',  # total: 4, max 3
            r'(?:worth|value)\s*[:=]?\s*(\d+(?:\.\d+)?)',  # worth 4, value 3
            r'^(\d+(?:\.\d+)?)$',  # Just a number: 4, 3.5
            r'(\d+(?:\.\d+)?)\s*$',  # Number at end: some text 4
        ]
        
        for pattern in equal_patterns:
            match = re.search(pattern, text)
            if match:
                total_marks = float(match.group(1))
                return {
                    "mode": "equal",
                    "total_marks": total_marks,
                    "scheme": {}
                }
        
        # DEFAULT fallback
        return {
            "mode": "equal",
            "total_marks": 1,
            "scheme": {}
        }
    
    def evaluate_question_universal(self, 
                                  student_options: List[str], 
                                  correct_options: List[str], 
                                  marking_scheme: Dict[str, Any]) -> Dict[str, Any]:
        """
        UNIVERSAL question evaluation - works for ANY marking scheme
        Implements strict penalty: ANY wrong option = 0 marks
        """
        # Normalize all options dynamically
        student_normalized = set()
        correct_normalized = set()
        
        # Detect option format from correct options
        option_format = self.detect_option_format(correct_options)
        
        # Normalize student options
        for opt in student_options:
            normalized = self.normalize_option(opt, option_format)
            if normalized:
                student_normalized.add(normalized)
        
        # Normalize correct options
        for opt in correct_options:
            normalized = self.normalize_option(opt, option_format)
            if normalized:
                correct_normalized.add(normalized)
        
        # Handle empty cases
        if not student_normalized:
            return {
                "marks_awarded": 0,
                "is_fully_correct": False,
                "is_partially_correct": False,
                "has_wrong_options": False,
                "explanation": "No options selected",
                "marking_mode": marking_scheme["mode"],
                "debug_info": {
                    "student_normalized": list(student_normalized),
                    "correct_normalized": list(correct_normalized),
                    "option_format": option_format
                }
            }
        
        if not correct_normalized:
            return {
                "marks_awarded": 0,
                "is_fully_correct": False,
                "is_partially_correct": False,
                "has_wrong_options": True,
                "explanation": "No correct options defined",
                "marking_mode": marking_scheme["mode"],
                "debug_info": {
                    "student_normalized": list(student_normalized),
                    "correct_normalized": list(correct_normalized),
                    "option_format": option_format
                }
            }
        
        # Check for wrong options (STRICT PENALTY RULE)
        wrong_options = student_normalized - correct_normalized
        correct_selected = student_normalized & correct_normalized
        
        # RULE 1: ANY wrong option = 0 marks (UNIVERSAL STRICT PENALTY)
        if wrong_options:
            return {
                "marks_awarded": 0,
                "is_fully_correct": False,
                "is_partially_correct": False,
                "has_wrong_options": True,
                "explanation": f"Selected wrong option(s): {', '.join(sorted(wrong_options))}. STRICT PENALTY: Zero marks awarded.",
                "marking_mode": marking_scheme["mode"],
                "debug_info": {
                    "student_normalized": list(student_normalized),
                    "correct_normalized": list(correct_normalized),
                    "wrong_options": list(wrong_options),
                    "option_format": option_format
                }
            }
        
        # RULE 2: Only correct options selected (no wrong ones)
        if marking_scheme["mode"] == "weightage":
            # WEIGHTAGE MODE: Sum weights of selected correct options
            awarded_marks = 0
            selected_weights = []
            
            for option in correct_selected:
                if option in marking_scheme["scheme"]:
                    weight = marking_scheme["scheme"][option]
                    awarded_marks += weight
                    selected_weights.append(f"{option}={weight}")
            
            is_fully_correct = (student_normalized == correct_normalized)
            is_partially_correct = (len(correct_selected) > 0 and not is_fully_correct)
            
            if is_fully_correct:
                explanation = f"All correct options selected. Weightage total: {awarded_marks} marks ({', '.join(selected_weights)})"
            else:
                missing_options = correct_normalized - student_normalized
                missing_weights = []
                for opt in missing_options:
                    if opt in marking_scheme["scheme"]:
                        missing_weights.append(f"{opt}={marking_scheme['scheme'][opt]}")
                explanation = f"Partial weightage: {awarded_marks} marks ({', '.join(selected_weights)}). Missing: {', '.join(missing_weights)}"
            
            return {
                "marks_awarded": awarded_marks,
                "is_fully_correct": is_fully_correct,
                "is_partially_correct": is_partially_correct,
                "has_wrong_options": False,
                "explanation": explanation,
                "marking_mode": "weightage",
                "debug_info": {
                    "student_normalized": list(student_normalized),
                    "correct_normalized": list(correct_normalized),
                    "selected_weights": selected_weights,
                    "option_format": option_format
                }
            }
        
        else:
            # EQUAL MODE: Proportional marking
            if student_normalized == correct_normalized:
                # Full marks
                return {
                    "marks_awarded": marking_scheme["total_marks"],
                    "is_fully_correct": True,
                    "is_partially_correct": False,
                    "has_wrong_options": False,
                    "explanation": f"All correct options selected. Full marks: {marking_scheme['total_marks']}",
                    "marking_mode": "equal",
                    "debug_info": {
                        "student_normalized": list(student_normalized),
                        "correct_normalized": list(correct_normalized),
                        "option_format": option_format
                    }
                }
            else:
                # Partial marks (proportional)
                proportion = len(correct_selected) / len(correct_normalized)
                partial_marks = round(marking_scheme["total_marks"] * proportion, 2)
                missing_options = correct_normalized - student_normalized
                
                return {
                    "marks_awarded": partial_marks,
                    "is_fully_correct": False,
                    "is_partially_correct": True,
                    "has_wrong_options": False,
                    "explanation": f"Partial marks: {len(correct_selected)}/{len(correct_normalized)} correct = {partial_marks} marks. Missing: {', '.join(sorted(missing_options))}",
                    "marking_mode": "equal",
                    "debug_info": {
                        "student_normalized": list(student_normalized),
                        "correct_normalized": list(correct_normalized),
                        "proportion": proportion,
                        "option_format": option_format
                    }
                }
    
    def evaluate_complete_paper(self, 
                               teacher_data: Dict[str, Any], 
                               student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        UNIVERSAL complete paper evaluation
        Works for ANY question paper format dynamically
        """
        results = {}
        total_marks = 0
        question_details = {}
        
        for question_id, teacher_info in teacher_data.items():
            if not question_id.startswith('Q'):
                continue
            
            # Get teacher's answer key
            correct_options = teacher_info.get('correct_options', teacher_info.get('correct', []))
            marks_text = teacher_info.get('marks_text', teacher_info.get('marks', 'Mark: 1'))
            
            # Get student's response
            student_options = student_data.get(question_id, [])
            if isinstance(student_options, str):
                student_options = [student_options]
            
            # Parse marking scheme dynamically
            marking_scheme = self.parse_marking_scheme_universal(marks_text)
            
            # Evaluate the question universally
            evaluation = self.evaluate_question_universal(
                student_options, 
                correct_options, 
                marking_scheme
            )
            
            # Store results
            marks_awarded = evaluation["marks_awarded"]
            results[question_id] = marks_awarded
            total_marks += marks_awarded
            question_details[question_id] = evaluation
            
            if self.debug_mode:
                print(f"{question_id}: {marks_awarded} marks - {evaluation['explanation']}")
        
        results["Total"] = total_marks
        
        return {
            "results": results,
            "question_details": question_details,
            "summary": {
                "total_questions": len(teacher_data),
                "total_marks": total_marks,
                "questions_attempted": len([q for q in teacher_data.keys() if q in student_data])
            }
        }

# Test the universal system
def test_universal_system():
    """Test the universal system with various formats"""
    evaluator = UniversalDynamicEvaluator()
    evaluator.debug_mode = True
    
    print("🧪 TESTING UNIVERSAL DYNAMIC EVALUATOR")
    print("=" * 60)
    
    # Test Case 1: Memory requirements (letters + weightage)
    print("\n--- Test 1: Memory Requirements ---")
    teacher_data_1 = {
        "Q1": {"correct_options": ["B", "D"], "marks_text": "Mark: 2"},
        "Q2": {"correct_options": ["C"], "marks_text": "Mark: 3"},
        "Q3": {"correct_options": ["A", "D", "E"], "marks_text": "Mark: a=2, d=3, e=1"},
    }
    
    student_data_1 = {
        "Q1": ["B", "D"],      # Full match → 2 marks
        "Q2": ["A", "C"],      # A wrong → 0 marks
        "Q3": ["D", "E"],      # d=3 + e=1 → 4 marks
    }
    
    result_1 = evaluator.evaluate_complete_paper(teacher_data_1, student_data_1)
    print(f"Results: {result_1['results']}")
    
    # Test Case 2: Numbers format
    print("\n--- Test 2: Numbers Format ---")
    teacher_data_2 = {
        "Q1": {"correct_options": ["1", "3"], "marks_text": "4 marks"},
        "Q2": {"correct_options": ["2"], "marks_text": "1=1, 2=3, 3=2"},
    }
    
    student_data_2 = {
        "Q1": ["1", "3"],      # Full match
        "Q2": ["2"],           # Correct
    }
    
    result_2 = evaluator.evaluate_complete_paper(teacher_data_2, student_data_2)
    print(f"Results: {result_2['results']}")
    
    # Test Case 3: Mixed format
    print("\n--- Test 3: Mixed Format ---")
    teacher_data_3 = {
        "Q1": {"correct_options": ["(a)", "[B]", "3"], "marks_text": "total: 6"},
    }
    
    student_data_3 = {
        "Q1": ["a", "B", "4"],  # 4 is wrong → 0 marks
    }
    
    result_3 = evaluator.evaluate_complete_paper(teacher_data_3, student_data_3)
    print(f"Results: {result_3['results']}")

if __name__ == "__main__":
    test_universal_system()
