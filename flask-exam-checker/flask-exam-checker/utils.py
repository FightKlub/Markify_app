import re
from datetime import datetime

def clean_option(option):
    """
    UNIVERSAL option cleaner - handles ANY format
    Supports: A-Z, a-z, 1-99, (a), [A], option formats, etc.
    """
    if not option:
        return None
    
    # Convert to string and strip whitespace
    option = str(option).strip()
    
    # Remove common prefixes like "option", "choice", etc.
    option = re.sub(r'^(option|choice|ans|answer)\s*', '', option, flags=re.IGNORECASE)
    
    # Remove common brackets and punctuation
    option = re.sub(r'[()[\]{}.,;:]', '', option)
    
    # Extract the core option character/number
    clean = re.sub(r'[^a-zA-Z0-9]', '', option)
    
    if not clean:
        return None
    
    # Handle single character (most common)
    if len(clean) == 1:
        if clean.isalpha():
            return clean.upper()
        elif clean.isdigit():
            num = int(clean)
            if 1 <= num <= 26:  # Convert 1-26 to A-Z
                return chr(ord('A') + num - 1)
            else:
                return clean  # Keep as number for options > 26
    
    # Handle multi-digit numbers (like 10, 11, 12)
    elif clean.isdigit():
        num = int(clean)
        if 1 <= num <= 26:
            return chr(ord('A') + num - 1)  # Convert to letter
        else:
            return clean  # Keep as number for large numbers
    
    # Handle multi-character (take first valid character)
    elif len(clean) > 1:
        for char in clean:
            if char.isalpha():
                return char.upper()
            elif char.isdigit():
                num = int(char)
                if 1 <= num <= 9:
                    return chr(ord('A') + num - 1)
    
    return clean.upper() if clean else None

def validate_roll_number(roll_number):
    """Validate and clean roll number"""
    if not roll_number:
        return None
    
    # Remove extra spaces and convert to string
    roll_number = str(roll_number).strip()
    
    # Basic validation - should contain alphanumeric characters
    if re.match(r'^[A-Za-z0-9\-_]+$', roll_number):
        return roll_number.upper()
    
    return None

def calculate_percentage(correct, total):
    """Calculate percentage with proper rounding"""
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 2)

def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def validate_image_file(file):
    """Validate uploaded image file"""
    if not file:
        return False
    
    if file.filename == '':
        return False
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return False
    
    # Check file size (max 10MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        return False
    
    return True

def extract_marks_from_text(text):
    """Extract marks from text patterns like 'marks-2', 'marks=3', '[2]', etc."""
    if not text:
        return 1
    
    text = str(text).lower().strip()
    
    # Enhanced patterns for marks extraction including handwritten variations
    patterns = [
        r'marks?[-=:\s]+(\d+(?:\.\d+)?)',  # marks-2, marks=3, marks:3, marks 2, mark 1.5
        r'(\d+(?:\.\d+)?)\s*marks?',       # 2 marks, 3marks, 1.5 mark
        r'mar\s*[-=:\s]*(\d+(?:\.\d+)?)',  # mar 2, mar-3, mar:1.5
        r'max\s*[-=:\s]*(\d+(?:\.\d+)?)',  # max 4, max-3, max:2.5
        r'\[(\d+(?:\.\d+)?)\]',            # [2], [3], [1.5]
        r'\((\d+(?:\.\d+)?)\)',            # (2), (3), (1.5)
        r'(\d+(?:\.\d+)?)\s*pts?',         # 2pts, 3pt, 1.5pts
        r'(\d+(?:\.\d+)?)\s*points?',      # 2 points, 3 point, 1.5 points
        r'worth\s+(\d+(?:\.\d+)?)',        # worth 2, worth 3, worth 1.5
        r'(\d+(?:\.\d+)?)\s*m\b',          # 2m, 3m, 1.5m
        r'^(\d+(?:\.\d+)?)$',              # Just a number by itself like "3" or "1.5"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                marks = float(match.group(1))
                return int(marks) if marks == int(marks) else marks  # Return int if whole number, float otherwise
            except (ValueError, IndexError):
                continue
    
    return 1  # Default to 1 mark if no pattern matches

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Replace unsafe characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename

def clean_multiple_options(options_str):
    """Clean and standardize multiple options format"""
    if not options_str:
        return []
    
    # Handle different input formats
    if isinstance(options_str, list):
        options = options_str
    elif isinstance(options_str, str):
        # Split by common delimiters
        options = re.split(r'[,;\s]+', options_str.strip())
    else:
        options = [str(options_str)]
    
    # Clean each option
    cleaned_options = []
    for option in options:
        cleaned = clean_option(option)
        if cleaned and cleaned not in cleaned_options:
            cleaned_options.append(cleaned)
    
    return sorted(cleaned_options)  # Sort for consistent comparison

def validate_multiple_options(student_options, correct_options):
    """
    Validate student's multiple options against correct answers using strict marking
    Returns True only if student selected ALL correct options and NO wrong options
    """
    if not isinstance(student_options, list):
        student_options = clean_multiple_options(student_options)
    if not isinstance(correct_options, list):
        correct_options = clean_multiple_options(correct_options)
    
    # Clean and sort both lists for comparison
    student_set = set(clean_multiple_options(student_options))
    correct_set = set(clean_multiple_options(correct_options))
    
    # Strict marking: must match exactly (all correct, no extra)
    return student_set == correct_set

def calculate_partial_marks(student_options, correct_options, total_marks, weightage_scheme=None):
    """
    UNIVERSAL PARTIAL CREDIT MARKING SYSTEM
    
    LOGIC: Award partial credit for correct selections, with penalty for wrong ones
    - If student selects ONLY correct options → Full/partial marks
    - If student selects correct + wrong → Partial credit with penalty
    - Works for ANY question paper format universally
    
    Args:
        student_options: List of student's selected options (any format)
        correct_options: List of correct options (any format)  
        total_marks: Total marks for the question
        weightage_scheme: Dict with option weights e.g., {'A': 2, 'D': 3, 'E': 1}
    
    Returns:
        dict: Complete evaluation result
    """
    # Convert inputs to proper format
    if not isinstance(student_options, list):
        student_options = clean_multiple_options(student_options)
    if not isinstance(correct_options, list):
        correct_options = clean_multiple_options(correct_options)
    
    # Clean and convert to sets for comparison
    student_set = set(clean_multiple_options(student_options))
    correct_set = set(clean_multiple_options(correct_options))
    
    # Handle empty cases
    if not student_set:
        return {
            'marks_awarded': 0,
            'is_fully_correct': False,
            'is_partially_correct': False,
            'has_wrong_options': False,
            'explanation': 'No options selected',
            'marking_mode': 'partial_credit'
        }
    
    if not correct_set:
        return {
            'marks_awarded': 0,
            'is_fully_correct': False,
            'is_partially_correct': False,
            'has_wrong_options': True,
            'explanation': 'No correct options defined',
            'marking_mode': 'partial_credit'
        }
    
    # Calculate intersections
    correct_selected = student_set & correct_set  # Correct options selected
    wrong_selected = student_set - correct_set    # Wrong options selected
    
    # CASE 1: Perfect match (selected exactly the correct options)
    if student_set == correct_set:
        if weightage_scheme:
            awarded_marks = sum(weightage_scheme.get(opt, 0) for opt in correct_selected)
            return {
                'marks_awarded': awarded_marks,
                'is_fully_correct': True,
                'is_partially_correct': False,
                'has_wrong_options': False,
                'explanation': f'All correct options selected. Weightage total: {awarded_marks} marks',
                'marking_mode': 'weightage'
            }
        else:
            return {
                'marks_awarded': total_marks,
                'is_fully_correct': True,
                'is_partially_correct': False,
                'has_wrong_options': False,
                'explanation': f'All correct options selected. Full marks: {total_marks}',
                'marking_mode': 'equal'
            }
    
    # CASE 2: Only correct options selected (subset of correct answers)
    if student_set.issubset(correct_set):
        if weightage_scheme:
            awarded_marks = sum(weightage_scheme.get(opt, 0) for opt in correct_selected)
            missing_options = correct_set - student_set
            missing_weights = [f"{opt}={weightage_scheme.get(opt, 0)}" for opt in missing_options]
            return {
                'marks_awarded': awarded_marks,
                'is_fully_correct': False,
                'is_partially_correct': True,
                'has_wrong_options': False,
                'explanation': f'Partial weightage: {awarded_marks} marks ({", ".join([f"{opt}={weightage_scheme.get(opt, 0)}" for opt in correct_selected])}). Missing: {", ".join(missing_weights)}',
                'marking_mode': 'weightage'
            }
        else:
            # Proportional marks for partial selection
            proportion = len(correct_selected) / len(correct_set)
            partial_marks = round(total_marks * proportion, 2)
            missing_options = correct_set - student_set
            return {
                'marks_awarded': partial_marks,
                'is_fully_correct': False,
                'is_partially_correct': True,
                'has_wrong_options': False,
                'explanation': f'Partial marks: {len(correct_selected)}/{len(correct_set)} correct = {partial_marks} marks. Missing: {", ".join(sorted(missing_options))}',
                'marking_mode': 'equal'
            }
    
    # CASE 3: Mixed selection (some correct + some wrong) - CONDITIONAL LOGIC
    if correct_selected and wrong_selected:
        # LOGIC FROM USER'S EXAMPLES:
        # - Single correct answer questions (like Q2): Give partial credit
        # - Multiple correct answer questions (like Q4, Q5): Strict penalty (zero marks)
        
        if len(correct_set) == 1:
            # SINGLE CORRECT ANSWER QUESTION (like Q2: only C is correct)
            # Give partial credit even with wrong selections
            if weightage_scheme:
                base_marks = sum(weightage_scheme.get(opt, 0) for opt in correct_selected)
                # For single answer, give 50% credit when mixed with wrong options
                awarded_marks = round(base_marks * 0.5, 2)
            else:
                # For single answer, give 50% credit when mixed with wrong options
                awarded_marks = round(total_marks * 0.5, 2)
            
            return {
                'marks_awarded': awarded_marks,
                'is_fully_correct': False,
                'is_partially_correct': True,
                'has_wrong_options': True,
                'explanation': f'Partial credit for single-answer question: {awarded_marks} marks. Correct: {", ".join(correct_selected)}, Wrong: {", ".join(wrong_selected)}',
                'marking_mode': 'partial_credit'
            }
        
        else:
            # MULTIPLE CORRECT ANSWER QUESTION (like Q4, Q5: A,D or C,D are correct)
            # Apply strict penalty - zero marks for any wrong selection
            return {
                'marks_awarded': 0,
                'is_fully_correct': False,
                'is_partially_correct': False,
                'has_wrong_options': True,
                'explanation': f'Strict penalty for multiple-answer question: Zero marks. Selected wrong option(s): {", ".join(wrong_selected)}',
                'marking_mode': 'strict_penalty'
            }
    
    # CASE 4: Only wrong options selected
    return {
        'marks_awarded': 0,
        'is_fully_correct': False,
        'is_partially_correct': False,
        'has_wrong_options': True,
        'explanation': f'All selected options are wrong: {", ".join(sorted(wrong_selected))}',
        'marking_mode': 'partial_credit'
    }

def parse_options_string(options_str):
    """Parse options string from various formats like 'A,B', 'A B C', 'A;B;C' etc."""
    if not options_str:
        return []
    
    # Handle array-like strings from database
    if options_str.startswith('{') and options_str.endswith('}'):
        # PostgreSQL array format: {A,B,C}
        options_str = options_str[1:-1]  # Remove braces
    
    # Split by various delimiters
    options = re.split(r'[,;\s]+', str(options_str).strip())
    
    # Clean and filter empty options
    return [clean_option(opt) for opt in options if opt.strip()]

def extract_weightage_scheme(marks_text):
    """
    UNIVERSAL weightage scheme extraction - works for ANY format
    Dynamically detects and extracts weightage patterns from ANY text
    
    Args:
        marks_text: String containing weightage information (any format)
        
    Returns:
        dict: Weightage scheme e.g., {'A': 2, 'D': 3, 'E': 1} or None if no weightage found
    """
    if not marks_text:
        return None
    
    # Use the universal evaluator for parsing
    from universal_dynamic_evaluator import UniversalDynamicEvaluator
    
    evaluator = UniversalDynamicEvaluator()
    marking_scheme = evaluator.parse_marking_scheme_universal(marks_text)
    
    if marking_scheme["mode"] == "weightage" and marking_scheme["scheme"]:
        return marking_scheme["scheme"]
    
    return None
