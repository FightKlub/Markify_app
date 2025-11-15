#!/usr/bin/env python3
"""
Universal MCQ Evaluation Agent
Handles ANY teacher sheet and student sheet combination with proper weightage logic
"""

import re
import json
from typing import Dict, List, Any, Tuple, Optional

class UniversalMCQEvaluator:
    """
    Universal MCQ evaluation agent that follows strict marking rules:
    1. Any wrong option = 0 marks (strict penalty)
    2. Equal marking: proportional marks for correct subset
    3. Weightage marking: sum of weights for correct subset
    """
    
    def __init__(self):
        pass
    
    def clean_option(self, option: str) -> Optional[str]:
        """Clean and standardize option format"""
        if not option:
            return None
        
        option = str(option).strip().upper()
        
        # Remove common brackets and punctuation
        option = re.sub(r'[()[\]{}.,;:]', '', option)
        
        # Extract the core option character/number
        clean = re.sub(r'[^A-Z0-9]', '', option)
        
        if not clean:
            return None
        
        # Handle single character (most common)
        if len(clean) == 1:
            if clean.isalpha():
                return clean
            elif clean.isdigit():
                num = int(clean)
                if 1 <= num <= 26:  # Convert 1-26 to A-Z
                    return chr(ord('A') + num - 1)
                else:
                    return clean  # Keep as number for options > 26
        
        # Handle multi-digit numbers
        elif clean.isdigit():
            num = int(clean)
            if 1 <= num <= 26:
                return chr(ord('A') + num - 1)
            else:
                return clean
        
        # Take first valid character
        elif len(clean) > 1:
            for char in clean:
                if char.isalpha():
                    return char
                elif char.isdigit():
                    num = int(char)
                    if 1 <= num <= 9:
                        return chr(ord('A') + num - 1)
        
        return clean if clean else None
    
    def parse_marking_scheme(self, marks_text: str) -> Tuple[float, Optional[Dict[str, float]]]:
        """
        Parse marking scheme from marks text
        Returns: (total_marks, weightage_scheme)
        """
        if not marks_text:
            return 1.0, None
        
        marks_text = marks_text.strip().lower()
        
        # Remove common prefixes
        marks_text = re.sub(r'^(mark|marks?)[:=\s]*', '', marks_text)
        
        # Check for weightage patterns first
        # Patterns: a=2, b=3, d=1 OR a:2, b:3 OR A=1.5, B=2.5 etc.
        weightage_patterns = [
            r'([a-z0-9]+)\s*[=:]\s*(\d+(?:\.\d+)?)',  # a=2, a:3, 1=2
            r'([a-z0-9]+)\s*[-]\s*(\d+(?:\.\d+)?)',   # a-2, b-3
            r'([a-z0-9]+)\s*\(\s*(\d+(?:\.\d+)?)\s*\)', # a(2), b(3)
            r'([a-z0-9]+)\s+(\d+(?:\.\d+)?)', # a 2, b 3 (space separated)
        ]
        
        weightage_matches = []
        for pattern in weightage_patterns:
            matches = re.findall(pattern, marks_text, re.IGNORECASE)
            weightage_matches.extend(matches)
        
        if weightage_matches:
            # Weightage mode
            weights = {}
            total = 0
            for option, weight in weightage_matches:
                option_clean = self.clean_option(option)
                if option_clean:
                    weight_val = float(weight)
                    weights[option_clean] = weight_val
                    total += weight_val
            
            return total, weights if weights else None
        
        # Equal marking mode - extract total marks
        # Look for standalone numbers
        number_match = re.search(r'(\d+(?:\.\d+)?)', marks_text)
        if number_match:
            total_marks = float(number_match.group(1))
            return total_marks, None
        
        # Default to 1 mark if nothing found
        return 1.0, None
    
    def parse_options(self, options_text: str) -> List[str]:
        """Parse and clean options from text"""
        if not options_text:
            return []
        
        # Split by common delimiters
        options = re.split(r'[,;\s]+', str(options_text).strip())
        
        # Clean each option
        cleaned_options = []
        for option in options:
            cleaned = self.clean_option(option)
            if cleaned and cleaned not in cleaned_options:
                cleaned_options.append(cleaned)
        
        return cleaned_options
    
    def evaluate_question(self, student_options: List[str], correct_options: List[str], 
                         total_marks: float, weightage_scheme: Optional[Dict[str, float]] = None) -> float:
        """
        Evaluate a single question based on the rules:
        1. Any wrong option = 0 marks
        2. Equal marking: proportional marks for correct subset
        3. Weightage marking: sum of weights for correct subset
        """
        if not student_options:
            return 0.0
        
        if not correct_options:
            return 0.0
        
        student_set = set(student_options)
        correct_set = set(correct_options)
        
        # Check for wrong options (strict penalty)
        wrong_options = student_set - correct_set
        if wrong_options:
            return 0.0  # Any wrong option = 0 marks
        
        # Student selected only correct options (subset or full)
        correct_selected = student_set & correct_set
        
        if not correct_selected:
            return 0.0
        
        if weightage_scheme:
            # Weightage mode: sum of weights of selected correct options
            awarded_marks = 0.0
            for option in correct_selected:
                if option in weightage_scheme:
                    awarded_marks += weightage_scheme[option]
            return awarded_marks
        else:
            # Equal marking mode: proportional marks
            if student_set == correct_set:
                # All correct options selected
                return total_marks
            else:
                # Subset of correct options selected
                proportion = len(correct_selected) / len(correct_set)
                return round(total_marks * proportion, 2)
    
    def evaluate_mcq_sheets(self, teacher_data: Dict[str, Any], student_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate MCQ sheets based on teacher's answer key and student's responses
        
        Args:
            teacher_data: {
                "Q1": {"correct": ["A", "B"], "marks_text": "Mark: 4"},
                "Q2": {"correct": ["C"], "marks_text": "Mark: a=2, b=3, c=1"},
                ...
            }
            student_data: {
                "Q1": ["A", "C"],
                "Q2": ["C"],
                ...
            }
        
        Returns:
            {"Q1": 0, "Q2": 1, ..., "Total": 5}
        """
        results = {}
        total_marks = 0.0
        
        # Get all questions from teacher data
        for question_id, teacher_info in teacher_data.items():
            if not question_id.startswith('Q'):
                continue
            
            # Parse teacher's answer key
            correct_options = teacher_info.get('correct', [])
            marks_text = teacher_info.get('marks_text', '')
            
            # Parse marking scheme
            question_total, weightage_scheme = self.parse_marking_scheme(marks_text)
            
            # Get student's response
            student_options = student_data.get(question_id, [])
            if isinstance(student_options, str):
                student_options = self.parse_options(student_options)
            
            # Evaluate the question
            marks_awarded = self.evaluate_question(
                student_options=student_options,
                correct_options=correct_options,
                total_marks=question_total,
                weightage_scheme=weightage_scheme
            )
            
            results[question_id] = marks_awarded
            total_marks += marks_awarded
        
        results["Total"] = total_marks
        return results

# Example usage and test function
def test_evaluator():
    """Test the evaluator with sample data"""
    evaluator = UniversalMCQEvaluator()
    
    # Test case 1: Mixed marking schemes
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
    
    student_data = {
        "Q1": ["B"],
        "Q2": ["A", "C"],  # A is wrong
        "Q3": ["D", "E"],  # Correct subset
        "Q4": ["A", "C"],  # C is wrong
        "Q5": ["B", "D", "F"],  # B, F are wrong
        "Q6": ["E"],  # Missing F
        "Q7": ["A", "C"],  # All correct
        "Q8": ["B", "D"],  # All correct
        "Q9": ["A", "B"],  # A is wrong
        "Q10": ["B", "C"]  # C is wrong
    }
    
    results = evaluator.evaluate_mcq_sheets(teacher_data, student_data)
    
    print("🧪 MCQ Evaluation Results:")
    print("=" * 40)
    for question_id, marks in results.items():
        if question_id != "Total":
            print(f"{question_id}: {marks} marks")
    print("=" * 40)
    print(f"Total: {results['Total']} marks")
    
    return results

if __name__ == "__main__":
    test_evaluator()
