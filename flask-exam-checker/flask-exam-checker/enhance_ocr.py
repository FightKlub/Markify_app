#!/usr/bin/env python3
"""
Script to enhance OCR detection accuracy
"""

def enhance_student_detection():
    """Replace student detection with enhanced logic"""
    
    # Read the current file
    with open('ocr_utils.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the student function start
    start_marker = 'def extract_student_answers(self, image_data):'
    start_pos = content.find(start_marker)
    
    if start_pos == -1:
        print("❌ Could not find student function")
        return False
    
    # Find the next function start (end of student function)
    next_func_start = content.find('def _process_with_gemini', start_pos)
    
    if next_func_start == -1:
        print("❌ Could not find end of student function")
        return False
    
    # Extract parts
    before_student = content[:start_pos]
    after_student = content[next_func_start:]
    
    # Enhanced student function
    enhanced_student = '''def extract_student_answers(self, image_data):
        """Extract student's selected answers with ULTRA-PRECISE detection"""
        prompt = """
        ULTRA-PRECISE STUDENT ANSWER DETECTION - ZERO MISSED MARKS, ZERO FALSE POSITIVES
        
        You are analyzing a student answer sheet with MAXIMUM ACCURACY requirements.
        
        CRITICAL MISSION: 
        1. FIND EVERY SINGLE marked option (0% missed marks allowed)
        2. EXCLUDE every unmarked option (0% false positives allowed)
        
        ENHANCED DETECTION STRATEGY:
        
        STEP 1: COMPREHENSIVE MARK SCANNING
        Look for ALL possible marking styles:
        - Checkmarks: ✓ ✔ ☑ (any size, any angle)
        - Diagonal lines: / \\ X × (thin or thick)
        - Circles: ○ ● ⭕ (around or near options)
        - Underlines: _____ (under option letters)
        - Highlighting: darker/bolder option letters
        - Crosses: + × ✗ (on or near options)
        - Dots: • ● (on option letters)
        - Arrows: → ↗ (pointing to options)
        - Any pen/pencil mark that indicates selection
        
        STEP 2: MULTI-ZONE DETECTION
        For each option letter, scan these zones:
        - ON the letter (overlapping)
        - ABOVE the letter (within 5mm)
        - BELOW the letter (within 5mm) 
        - LEFT of the letter (within 5mm)
        - RIGHT of the letter (within 5mm)
        - DIAGONAL from letter (within 5mm radius)
        
        STEP 3: CONTRAST ANALYSIS
        Compare each option to others in the same question:
        - Is this option visually DIFFERENT from others?
        - Is it darker, bolder, or modified in any way?
        - Does it have ANY additional marks not present on other options?
        
        STEP 4: VALIDATION FILTER
        Before including an option, verify:
        - The mark is clearly intentional (not a shadow or artifact)
        - The mark is associated with this specific option
        - The option actually exists in this question
        - The mark looks like a human-made selection
        
        STEP 5: EXHAUSTIVE VERIFICATION
        - Scan the image multiple times with different focus
        - Look for very faint marks that might be missed
        - Check for marks that might blend with printed text
        - Verify no marked options are accidentally excluded
        
        CRITICAL RULES:
        - If you see ANY mark near an option, investigate thoroughly
        - Better to include a questionable mark than miss a real one
        - But still exclude obvious false positives (shadows, artifacts)
        - Scan every pixel around each option letter
        - Look for marks in unexpected positions
        
        Return JSON:
        {
            "roll_number": "extracted_or_null",
            "section": "extracted_or_null",
            "total_questions": N,
            "answers": [
                {
                    "question_number": 1,
                    "selected_options": ["all_marked_options"]
                }
            ]
        }
        """
        
        return self._process_with_gemini(image_data, prompt)
    
    '''
    
    # Combine the parts
    new_content = before_student + enhanced_student + after_student
    
    # Write the enhanced file
    with open('ocr_utils.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Enhanced student detection logic successfully!")
    return True

if __name__ == "__main__":
    enhance_student_detection()
