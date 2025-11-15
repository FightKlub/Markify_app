#!/usr/bin/env python3
"""
Enhanced Evaluation System for MCQ Answer Sheets
Implements advanced marking schemes with equal and weightage modes
"""

import re
import json
from typing import Dict, List, Union, Tuple
from utils import clean_multiple_options, clean_option

class EnhancedEvaluator:
    """
    Advanced MCQ evaluation system with support for:
    1. Equal marking mode (Mark: 2, Mark: 4)
    2. Weightage marking mode (Mark: a=2, b=3, d=1)
    3. Strict wrong answer penalty (any wrong = 0 marks)
    4. Proportional partial marking for correct subsets
    """
    
    def __init__(self):
        self.debug_mode = False
    
    def parse_marking_scheme(self, marks_text: str) -> Dict:
        """
        Parse marking scheme from text patterns
        
        Args:
            marks_text: Text like "Mark: 2", "Mark: 4", "Mark: a=2, b=3, d=1", "Mark: b=2, d=3"
            
        Returns:
            Dict with 'mode', 'total_marks', and 'weights' (if applicable)
        """
        if not marks_text:
            return {"mode": "equal", "total_marks": 1, "weights": {}}
        
        marks_text = marks_text.strip().lower()
        
        # Remove common prefixes
        marks_text = re.sub(r'^(mark|marks?)[:=\s]*', '', marks_text)
        
        # Enhanced weightage pattern to catch ALL possible variations
        # Patterns: a=2, b=3, d=1 OR a:2, b:3 OR a 2, b 3 OR A=1.5, B=2.5 etc.
        # Support options A-Z (not just a-f) for maximum flexibility
        weightage_pattern = r'([a-zA-Z])\s*[=:\s]\s*(\d+(?:\.\d+)?)'
        weightage_matches = re.findall(weightage_pattern, marks_text)
        
        if weightage_matches:
            # Weightage mode: Mark: a=2, b=3, d=1
            weights = {}
            total_marks = 0
            
            for option, weight in weightage_matches:
                option_clean = clean_option(option)
                weight_val = float(weight)
                weights[option_clean] = weight_val
                total_marks += weight_val
            
            if self.debug_mode:
                print(f"DEBUG - Parsed weightage: {weights}, total: {total_marks}")
            
            return {
                "mode": "weightage",
                "total_marks": total_marks,
                "weights": weights
            }
        
        else:
            # Equal mode: Mark: 2, Mark: 4
            total_pattern = r'(\d+(?:\.\d+)?)'
            total_match = re.search(total_pattern, marks_text)
            
            if total_match:
                total_marks = float(total_match.group(1))
                return {
                    "mode": "equal",
                    "total_marks": total_marks,
                    "weights": {}
                }
            else:
                # Default fallback
                return {
                    "mode": "equal",
                    "total_marks": 1,
                    "weights": {}
                }
    
    def evaluate_question(self, 
                         correct_options: List[str], 
                         student_options: List[str], 
                         marking_scheme: Dict) -> Dict:
        """
        Evaluate a single question based on the marking scheme
        
        Args:
            correct_options: List of correct options ['A', 'B']
            student_options: List of student's selected options ['A', 'C']
            marking_scheme: Parsed marking scheme from parse_marking_scheme()
            
        Returns:
            Dict with evaluation results
        """
        # Clean and normalize options
        correct_set = set(clean_multiple_options(correct_options))
        student_set = set(clean_multiple_options(student_options))
        
        # Handle empty selections
        if not student_set:
            return {
                "marks_awarded": 0,
                "is_fully_correct": False,
                "is_partially_correct": False,
                "has_wrong_options": False,
                "explanation": "No options selected",
                "marking_mode": marking_scheme["mode"]
            }
        
        if not correct_set:
            return {
                "marks_awarded": 0,
                "is_fully_correct": False,
                "is_partially_correct": False,
                "has_wrong_options": True,
                "explanation": "No correct options defined",
                "marking_mode": marking_scheme["mode"]
            }
        
        # Check for wrong options
        wrong_options = student_set - correct_set
        correct_selected = student_set & correct_set
        
        # RULE 1: If student selected ANY wrong option → 0 marks
        if wrong_options:
            return {
                "marks_awarded": 0,
                "is_fully_correct": False,
                "is_partially_correct": False,
                "has_wrong_options": True,
                "explanation": f"Selected wrong option(s): {', '.join(sorted(wrong_options))}. Zero marks awarded.",
                "marking_mode": marking_scheme["mode"]
            }
        
        # RULE 2: Student selected ONLY correct options (no wrong ones)
        if student_set.issubset(correct_set):
            
            if marking_scheme["mode"] == "weightage":
                # Weightage mode: Sum the weights of selected correct options
                awarded_marks = 0
                selected_weights = []
                
                for option in correct_selected:
                    if option in marking_scheme["weights"]:
                        weight = marking_scheme["weights"][option]
                        awarded_marks += weight
                        selected_weights.append(f"{option}={weight}")
                
                is_fully_correct = (student_set == correct_set)
                is_partially_correct = (len(correct_selected) > 0 and not is_fully_correct)
                
                if is_fully_correct:
                    explanation = f"All correct options selected. Weightage total: {awarded_marks} marks ({', '.join(selected_weights)})"
                else:
                    missing_options = correct_set - student_set
                    missing_weights = []
                    for opt in missing_options:
                        if opt in marking_scheme["weights"]:
                            missing_weights.append(f"{opt}={marking_scheme['weights'][opt]}")
                    
                    explanation = f"Partial correct options. Selected: {awarded_marks} marks ({', '.join(selected_weights)}). Missing: {', '.join(missing_weights)}"
                
                return {
                    "marks_awarded": awarded_marks,
                    "is_fully_correct": is_fully_correct,
                    "is_partially_correct": is_partially_correct,
                    "has_wrong_options": False,
                    "explanation": explanation,
                    "marking_mode": "weightage",
                    "selected_weights": selected_weights,
                    "total_possible": marking_scheme["total_marks"]
                }
            
            else:
                # Equal mode: Proportional marking
                if student_set == correct_set:
                    # Full marks for all correct options
                    return {
                        "marks_awarded": marking_scheme["total_marks"],
                        "is_fully_correct": True,
                        "is_partially_correct": False,
                        "has_wrong_options": False,
                        "explanation": f"All correct options selected. Full marks: {marking_scheme['total_marks']}",
                        "marking_mode": "equal",
                        "total_possible": marking_scheme["total_marks"]
                    }
                else:
                    # Partial marks for subset of correct options
                    proportion = len(correct_selected) / len(correct_set)
                    partial_marks = round(marking_scheme["total_marks"] * proportion, 2)
                    missing_options = correct_set - student_set
                    
                    return {
                        "marks_awarded": partial_marks,
                        "is_fully_correct": False,
                        "is_partially_correct": True,
                        "has_wrong_options": False,
                        "explanation": f"Partial marks: {len(correct_selected)}/{len(correct_set)} correct options = {partial_marks} marks. Missing: {', '.join(sorted(missing_options))}",
                        "marking_mode": "equal",
                        "total_possible": marking_scheme["total_marks"]
                    }
        
        # This shouldn't happen given the logic above, but just in case
        return {
            "marks_awarded": 0,
            "is_fully_correct": False,
            "is_partially_correct": False,
            "has_wrong_options": True,
            "explanation": "Unexpected error in marking calculation",
            "marking_mode": marking_scheme["mode"]
        }
    
    def evaluate_complete_sheet(self, 
                               teacher_data: Dict, 
                               student_data: Dict) -> Dict:
        """
        Evaluate complete answer sheet
        
        Args:
            teacher_data: {
                "Q1": {"correct_options": ["A", "B"], "marks_text": "Mark: 4"},
                "Q2": {"correct_options": ["C"], "marks_text": "Mark: a=2, b=3"},
                ...
            }
            student_data: {
                "Q1": ["A", "B"],
                "Q2": ["C", "D"],
                ...
            }
            
        Returns:
            Dict with complete evaluation results
        """
        results = {}
        total_marks = 0
        question_details = {}
        
        # Process each question
        for question_id in teacher_data.keys():
            if question_id not in student_data:
                # Student didn't answer this question
                results[question_id] = 0
                question_details[question_id] = {
                    "marks_awarded": 0,
                    "explanation": "Question not answered",
                    "marking_mode": "equal"
                }
                continue
            
            # Get teacher's answer key
            teacher_info = teacher_data[question_id]
            correct_options = teacher_info.get("correct_options", [])
            marks_text = teacher_info.get("marks_text", "Mark: 1")
            
            # Get student's answers
            student_options = student_data[question_id]
            
            # Parse marking scheme
            marking_scheme = self.parse_marking_scheme(marks_text)
            
            # Evaluate the question
            evaluation = self.evaluate_question(correct_options, student_options, marking_scheme)
            
            # Store results
            marks_awarded = evaluation["marks_awarded"]
            results[question_id] = marks_awarded
            total_marks += marks_awarded
            question_details[question_id] = evaluation
            
            if self.debug_mode:
                print(f"{question_id}: {marks_awarded} marks - {evaluation['explanation']}")
        
        # Add total
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
    
    def evaluate_from_images_data(self, 
                                 teacher_ocr_result: Dict, 
                                 student_ocr_result: Dict) -> Dict:
        """
        Evaluate from OCR extracted data
        
        Args:
            teacher_ocr_result: OCR result from teacher's answer key
            student_ocr_result: OCR result from student's answer sheet
            
        Returns:
            Evaluation results in JSON format
        """
        # Convert OCR results to evaluation format
        teacher_data = {}
        student_data = {}
        
        # Process teacher's data
        if "answers" in teacher_ocr_result:
            for answer in teacher_ocr_result["answers"]:
                q_num = f"Q{answer['question_number']}"
                teacher_data[q_num] = {
                    "correct_options": answer.get("correct_options", [answer.get("correct_option", "")]),
                    "marks_text": answer.get("marks_text", f"Mark: {answer.get('marks', 1)}")
                }
        
        # Process student's data
        if "answers" in student_ocr_result:
            for answer in student_ocr_result["answers"]:
                q_num = f"Q{answer['question_number']}"
                student_data[q_num] = answer.get("selected_options", [answer.get("selected_option", "")])
        
        # Evaluate
        evaluation_result = self.evaluate_complete_sheet(teacher_data, student_data)
        
        return evaluation_result["results"]

def create_evaluation_endpoint():
    """
    Create a sample evaluation function that can be used as an API endpoint
    """
    def evaluate_mcq_sheets(teacher_image_data, student_image_data):
        """
        Evaluate MCQ sheets from image data
        
        Args:
            teacher_image_data: Base64 encoded teacher's answer key image
            student_image_data: Base64 encoded student's answer sheet image
            
        Returns:
            JSON evaluation results
        """
        try:
            from ocr_utils import OCRProcessor
            
            # Initialize OCR processor and evaluator
            ocr_processor = OCRProcessor()
            evaluator = EnhancedEvaluator()
            
            # Extract data from teacher's image
            teacher_ocr_result = ocr_processor.extract_teacher_answers(teacher_image_data)
            
            # Extract data from student's image
            student_ocr_result = ocr_processor.extract_student_answers(student_image_data)
            
            # Evaluate
            results = evaluator.evaluate_from_images_data(teacher_ocr_result, student_ocr_result)
            
            return {
                "success": True,
                "results": results,
                "teacher_data": teacher_ocr_result,
                "student_data": student_ocr_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    return evaluate_mcq_sheets

# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced evaluator
    evaluator = EnhancedEvaluator()
    evaluator.debug_mode = True
    
    # Test case 1: Equal marking mode
    print("=== TEST CASE 1: Equal Marking Mode ===")
    teacher_data_1 = {
        "Q1": {"correct_options": ["A", "B"], "marks_text": "Mark: 4"},
        "Q2": {"correct_options": ["C"], "marks_text": "Mark: 2"},
        "Q3": {"correct_options": ["A", "C", "D"], "marks_text": "Mark: 6"}
    }
    
    student_data_1 = {
        "Q1": ["A", "B"],      # All correct → 4 marks
        "Q2": ["C", "D"],      # One wrong → 0 marks
        "Q3": ["A", "C"]       # Partial correct → 4 marks (2/3 * 6)
    }
    
    result_1 = evaluator.evaluate_complete_sheet(teacher_data_1, student_data_1)
    print("Results:", result_1["results"])
    print()
    
    # Test case 2: Weightage marking mode
    print("=== TEST CASE 2: Weightage Marking Mode ===")
    teacher_data_2 = {
        "Q1": {"correct_options": ["A", "B", "D"], "marks_text": "Mark: a=2, b=3, d=1"},
        "Q2": {"correct_options": ["B", "C"], "marks_text": "Mark: b=4, c=2"}
    }
    
    student_data_2 = {
        "Q1": ["A", "B"],      # Selected a=2, b=3 → 5 marks
        "Q2": ["B", "C", "A"]  # One wrong → 0 marks
    }
    
    result_2 = evaluator.evaluate_complete_sheet(teacher_data_2, student_data_2)
    print("Results:", result_2["results"])
