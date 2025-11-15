#!/usr/bin/env python3
"""
Simple OCR Fix - Clean and reliable OCR processing
"""

def create_simple_teacher_prompt():
    """Create a simple, effective teacher OCR prompt"""
    return """
    Analyze this MCQ answer key image and extract the correct answers and marks for each question.
    
    Look for:
    1. Question numbers (1, 2, 3... or Q1, Q2, Q3...)
    2. Marked correct options (diagonal lines, circles, checkmarks on options like A, B, C, D)
    3. Marks/points for each question (look for "Mark:", "marks:", numbers near questions)
    
    Return JSON format:
    {
        "total_questions": 10,
        "answers": [
            {
                "question_number": 1,
                "correct_options": ["B", "D"],
                "marks": 2,
                "marks_text": "mark: 2",
                "question_type": "multiple"
            }
        ]
    }
    
    Important:
    - Include ALL questions you can see
    - Mark correct_options as empty [] if no clear marks found
    - Use question_type "single" for one correct option, "multiple" for more than one
    """

def create_simple_student_prompt():
    """Create a simple, effective student OCR prompt"""
    return """
    Analyze this student answer sheet and find which options are marked for each question.
    
    Look for:
    1. Question numbers
    2. Student marks (checkmarks, ticks, lines) on options A, B, C, D, etc.
    3. Roll number and section if visible
    
    Return JSON format:
    {
        "roll_number": "48",
        "section": "A",
        "total_questions": 10,
        "answers": [
            {
                "question_number": 1,
                "selected_options": ["B", "D"]
            }
        ]
    }
    
    Important:
    - Include ALL questions you can see
    - Use empty array [] if no marks found for a question
    - Look carefully for all types of marks (✓, /, \, X, circles)
    """

def test_simple_prompts():
    """Test the simple prompts"""
    print("=== SIMPLE TEACHER PROMPT ===")
    print(create_simple_teacher_prompt())
    print("\n=== SIMPLE STUDENT PROMPT ===")
    print(create_simple_student_prompt())

if __name__ == "__main__":
    test_simple_prompts()
