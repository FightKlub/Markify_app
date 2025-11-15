import base64
import io
from io import BytesIO
import json
import logging
import os
import re
from PIL import Image
from api_key_manager import get_api_manager

class OCRProcessor:
    def __init__(self, api_key=None):
        # Use API Key Manager instead of single API key
        self.api_manager = get_api_manager()
        self.logger = logging.getLogger(__name__)
        # Only print on first load, not on Flask debug restart
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            print(f"🔑 OCR Processor initialized with {self.api_manager.get_status()['total_keys']} API keys")
    
    def preprocess_image(self, image_file):
        """Preprocess image for fast OCR processing with timeout prevention"""
        try:
            # Open and convert image
            image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get original dimensions
            width, height = image.size
            
            # Resize for optimal OCR processing (balance quality vs speed)
            # Reduced resolution for faster processing and timeout prevention
            max_dimension = 1400  # Reduced from 2048 for faster processing
            if width > max_dimension or height > max_dimension:
                if width > height:
                    new_width = max_dimension
                    new_height = int(height * max_dimension / width)
                else:
                    new_height = max_dimension
                    new_width = int(width * max_dimension / height)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"DEBUG - Resized image to: ({new_width}, {new_height})")
            else:
                print(f"DEBUG - Original image size maintained: ({width}, {height})")
            
            # Save to bytes with optimized compression for speed
            img_byte_arr = BytesIO()
            # Use moderate quality for balance between speed and accuracy
            image.save(img_byte_arr, format='JPEG', quality=80, optimize=True)
            img_byte_arr = img_byte_arr.getvalue()
            
            print(f"DEBUG - Final image size: {len(img_byte_arr)} bytes")
            
            return base64.b64encode(img_byte_arr).decode()
            
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return None
    
    def extract_teacher_answers(self, image_data):
        """Extract correct answers from teacher's answer key with enhanced reliability"""
        prompt = """
        🎯 ROBUST MCQ ANSWER KEY ANALYZER - ENHANCED FOR RELIABILITY
        
        You are analyzing ANY MCQ answer key from ANY exam format. Your mission: UNIVERSAL detection that works for ALL question papers.
        
        UNIVERSAL ANALYSIS PROTOCOL:
        
        STEP 1: ADAPTIVE QUESTION DISCOVERY
        - Scan the ENTIRE image for question numbers (could be 1-100+ questions)
        - Questions may be numbered: 1,2,3... OR Q1,Q2,Q3... OR (1),(2),(3)... OR any format
        - Each question may have different numbers of options (A-D, A-E, A-F, 1-4, 1-5, etc.)
        - Adapt to whatever format you see - don't assume specific patterns
        
        STEP 2: PRECISE MARK DETECTION WITH VALIDATION
        🎯 CRITICAL: Detect ONLY actual markings, avoid false positives!
        
        - PRIORITY 1: CLEAR DIAGONAL LINES (most reliable):
          * Look for DISTINCT lines crossing through options: /, \, X, ×
          * Lines must be CLEARLY visible and intentional
          * Must go ACROSS or THROUGH the option letter
          * Ignore faint shadows or image artifacts
        
        - PRIORITY 2: CLEAR ENCLOSURES:
          * Well-defined circles around options: ○, ●
          * Complete squares around options: □, ■
          * Must be intentional markings, not image noise
        
        - PRIORITY 3: CLEAR CHECKMARKS:
          * Distinct tick marks: ✓, ✔
          * Must be near the option letter
          * Must look intentional, not accidental marks
        
        - PRIORITY 4: VISUAL EMPHASIS:
          * Significantly darker or bolder option letters
          * Clear highlighting or underlining
          * Must be obviously different from unmarked options
        
        🔍 VALIDATION STRATEGY:
          * ONLY mark options that CLEARLY exist in the question
          * For each question, first identify ALL available options (a, b, c, d, e, etc.)
          * ONLY select from these available options
          * If you see a mark on option 'f' but question only has a-d, IGNORE it
          * Compare marked vs unmarked options - marked ones should be visually distinct
          * When in doubt, DON'T include questionable marks
          * Quality over quantity - better to miss a mark than create false positives
        
        STEP 3: UNIVERSAL OPTION FORMATS
        - Options can be: A,B,C,D,E,F... OR 1,2,3,4,5... OR (a),(b),(c)... OR [A],[B],[C]...
        - Always include options in UPPERCASE letters in your response (A,B,C not a,b,c)
        - Convert numbers to letters if needed: 1→A, 2→B, 3→C, etc.
        - Only include options that actually exist in each question
        
        STEP 4: UNIVERSAL MARKS EXTRACTION
        - Look for ANY text that indicates marking scheme:
          * "Mark: 2", "Marks: 3", "Points: 4"
          * "2 marks", "3 pts", "worth 4"
          * Weightage: "a=2, b=3", "A:2, B:3", "option A=2"
          * Numbers alone: "2", "3", "4.5"
          * Any pattern that shows point values
        - Extract the EXACT text you see for marks_text field
        
        UNIVERSAL PRINCIPLES:
        ✅ ADAPT to any question paper format you encounter
        ✅ DETECT any type of correct answer marking
        ✅ WORK with any number of questions (1-100+)
        ✅ HANDLE any option format (A-Z, 1-12, mixed)
        ✅ EXTRACT any marking scheme (equal, weightage, mixed)
        ✅ BE FLEXIBLE but ACCURATE
        
        ANALYSIS APPROACH:
        1. First, understand the specific format of THIS image
        2. Identify the marking style used by THIS teacher
        3. Adapt your detection to THIS particular format
        4. Don't assume anything - work with what you actually see
        
        🚨 CRITICAL REQUIREMENT: You MUST find correct options for EVERY question!
        If you can't see clear marks, look for:
        - Options that appear slightly different
        - Options with any kind of marking or emphasis
        - Options that stand out in any way
        - When in doubt, make your best guess based on visual differences
        
        🔧 FALLBACK STRATEGY: If image quality is poor or marks are unclear:
        - Still provide your best analysis
        - Use "marks": 1 and "marks_text": "unclear" for uncertain questions
        - Include at least one option per question (guess if necessary)
        - Better to provide imperfect results than fail completely
        
        CRITICAL: This system must work for ANY exam from ANY school/college/format. Be completely adaptive.
        3. Marks/points for each question - Look VERY CAREFULLY for handwritten "Mark:" or "mark:" text patterns:
           - EQUAL MARKING: "marks-2", "marks=3", "marks:3", "marks 2", "2 marks", "Mark: 4", "Mark: 2"
           - WEIGHTAGE MARKING: "Mark: a=2, b=3, d=1", "a=2, d=3, e=1", "b=2, d=3", "Mark: a=2, d=3"
           - SIMPLE NUMBERS: "[2]", "(3)", "2pts", "3 points", "worth 2", "2m"
           - Numbers written near questions (like "3" next to a question means 3 marks)
           - Handwritten text like "mar 1.5", "marks - 3", "max 4.5", "m-2", "mk 3" etc.
           - ANY number that appears to be associated with a question
        
        CRITICAL INSTRUCTIONS FOR MARKS EXTRACTION:
        - Scan the ENTIRE image for any handwritten numbers or text that could indicate marks
        - Look for text like "marks", "mar", "mk", "m", "pts", "points" followed by numbers
        - Look for standalone numbers that might indicate marks (2, 3, 4, 1.5, etc.)
        
        UNIVERSAL WEIGHTAGE DETECTION:
        - Look for ANY pattern where option letters/numbers are paired with values
        - Common patterns: "a=2", "A=3", "1=2", "option a: 2", "a:2", "a 2", "a-2", "a(2)"
        - Detect ALL possible separators: =, :, -, space, (, ), [, ]
        - Support ALL option formats: a-z, A-Z, 1-99, (a), [A], etc.
        - Examples to detect:
          * "mark: a=2, d=3, e=1" 
          * "Mark: A=1.5, B=2.5"
          * "a:2 b:3 c:1"
          * "option a=2, option d=3"
          * "1=2, 2=3, 3=1"
          * "a(2) d(3) e(1)"
          * "A-2, D-3, E-1"
        
        UNIVERSAL EQUAL MARKING DETECTION:
        - "Mark: 4", "marks: 3", "mark=2", "2 marks", "worth 3", etc.
        - ANY standalone number near a question
        
        EXTRACTION RULES:
        - PRESERVE the EXACT text format for marks_text field
        - If you see weightage patterns, extract ALL option-value pairs
        - If you see equal marking, extract the total value
        - Better to extract uncertain text than miss marking information
        - Support decimal values (1.5, 2.5, etc.)
        
        MULTIPLE CORRECT OPTIONS:
        - If a question has multiple correct options marked, list them as an array
        - For single correct option, still use array format for consistency
        - Examples: ["A"], ["A", "B"], ["A", "B", "C"]
        
        🔍 CRITICAL VALIDATION STEP - OPTION FILTERING:
        Before finalizing your response, VALIDATE each detected option:
        
        1. **Identify Available Options**: For each question, first determine what options actually exist
           - Question 1 might have: (a)(b)(c)(d) - so only A,B,C,D are valid
           - Question 2 might have: (a)(b)(c)(d)(e) - so A,B,C,D,E are valid
           - Question 3 might have: 1,2,3,4 - so only 1,2,3,4 are valid (convert to A,B,C,D)
        
        2. **Filter Invalid Detections**: 
           - If you detected option 'E' but question only has A,B,C,D → REMOVE 'E' from correct_options
           - If you detected option 'F' but question only has A,B,C,D,E → REMOVE 'F' from correct_options
           - ONLY include options that actually exist in that specific question
        
        3. **Quality Control**:
           - Better to have fewer accurate options than many inaccurate ones
           - If unsure about a marking, DON'T include it
           - Empty correct_options array is acceptable if no clear marks found
        
        For each question, if you find marks information, include it. If you find text that might contain marks but you're not 100% sure, include both the marks number AND the raw text you found.
        
        Return ONLY a valid JSON object in this exact format:
        {
            "total_questions": number,
            "answers": [
                {"question_number": 1, "correct_options": ["A"], "marks": 3, "marks_text": "marks-3", "question_type": "single"},
                {"question_number": 2, "correct_options": ["A", "B"], "marks": 2, "marks_text": "mar 2", "question_type": "multiple"},
                {"question_number": 3, "correct_options": ["C"], "marks": 4, "marks_text": "4", "question_type": "single"}
            ]
        }
        
        - Use "correct_options" as an array even for single answers
        - Set "question_type" to "single" if only one option is correct, "multiple" if more than one
        - Include "marks_text" field with the actual text you found that indicates marks, even if it's unclear.
        Do not include any other text, explanations, or markdown formatting.
        """
        
        return self._process_with_gemini(image_data, prompt)
    
    def extract_student_answers(self, image_data):
        """Extract student's selected answers along with roll number and section"""
        prompt = """
        Analyze this student answer sheet image to identify marked options for each question.
        
        🎯 REVOLUTIONARY DETECTION MISSION:
        - FIND 100% of human ticks (ZERO missed ticks)
        - ELIMINATE 100% of false positives (ZERO wrong detections)
        - ACHIEVE PERFECT ACCURACY (no errors allowed)
        - ADAPT to ANY human marking style
        
        ⚠️ REVOLUTIONARY 5-LAYER DETECTION SYSTEM:
        LAYER 1: VISUAL CONTRAST ANALYSIS - Find any mark darker than printed text
        LAYER 2: GEOMETRIC PATTERN RECOGNITION - Detect tick shapes and patterns
        LAYER 3: SPATIAL RELATIONSHIP MAPPING - Analyze mark positions relative to options
        LAYER 4: HUMAN BEHAVIOR MODELING - Understand how humans mark answer sheets
        LAYER 5: CROSS-VALIDATION VERIFICATION - Confirm detections across all layers (a), (b), (c), (d) for every question
        
        🔍 HUMAN TICK/CHECK STYLES TO DETECT:
        Students use different styles of ticks/checks to mark their answers. Look for these 7 common styles:
        
        1. CLASSIC CHECK (✓): Two-stroke mark with short lower-left arm and longer upward sweep
           - Smooth curve, starts bottom-left, lifts at 45-60°
           - Most common style
        
        2. HOOK CHECK: Like classic check but upper stroke hooks back slightly
           - Creates subtle "J" or hook at the top
           - Upper tip curls or bends inward
        
        3. SHARP-ANGLE TICK: Angular V-shaped tick with straight lines
           - Almost geometric with crisp corner
           - Little or no curve
        
        4. LONG-TAIL TICK: Bottom-left to top-right with extended second stroke
           - Dramatic flourish, extends well beyond option text
           - Sometimes crosses into neighboring choices
        
        5. LEAN-FORWARD TICK: Slanted forward like "/" with tiny return stroke
           - Very narrow V shape
           - Sometimes mistaken for single slash
        
        6. DOUBLE-STROKE/HEAVY TICK: Writer goes over same tick twice
           - Darker, bolder check with visible overlap
           - Thickened appearance
        
        7. REVERSE/LEFT-HAND TICK: Begins right and sweeps leftward
           - Mirror image forming "∧" with open side right
           - Less common but still valid
        
        🚨 CRITICAL: These ticks can appear ABOVE, ON, THROUGH, or NEAR option letters (a), (b), (c), (d)
        
        🔍 REVOLUTIONARY 5-LAYER DETECTION PROTOCOL:
        
        LAYER 1: VISUAL CONTRAST ANALYSIS
        - Analyze EVERY pixel in the image for contrast differences
        - Identify ALL marks that are darker than the background
        - Create a contrast map of potential human marks
        - Filter out printed text and form elements
        
        LAYER 2: GEOMETRIC PATTERN RECOGNITION
        - Scan for specific tick geometries: ✓ / \ X + • ○ — |
        - Detect V-shapes, diagonal lines, crosses, dots, circles
        - Identify partial marks, incomplete ticks, faint marks
        - Recognize unconventional marking patterns
        
        LAYER 3: SPATIAL RELATIONSHIP MAPPING
        - Map every detected mark to its nearest option (a), (b), (c), (d)
        - Analyze mark positioning: ABOVE, ON, THROUGH, AROUND options
        - Calculate distance and alignment with option letters
        - Determine intentional vs accidental mark placement
        
        LAYER 4: HUMAN BEHAVIOR MODELING
        - Study the student's marking pattern across all questions
        - Identify the student's preferred tick style and position
        - Detect consistency in marking behavior
        - Adapt detection sensitivity to student's style
        
        LAYER 5: CROSS-VALIDATION VERIFICATION
        - Verify each detection across all 4 previous layers
        - Confirm marks meet criteria from multiple detection methods
        - Eliminate false positives through multi-layer validation
        - Ensure no real ticks are missed through comprehensive checking
        
        🔍 ADVANCED DETECTION METHODOLOGY:
        
        PHASE 1: SCAN PREPARATION
        - Study the entire image to understand the marking pattern
        - Identify what type of ticks the student uses
        - Note the darkness/thickness of human marks vs printed text
        - Determine the option format (A,B,C,D or 1,2,3,4 or A,B,C,D,E,F etc.)
        
        PHASE 2: SYSTEMATIC DETECTION
        For each question, for each option (FLEXIBLE - could be a,b,c,d OR 1,2,3,4 OR a,b,c,d,e,f etc.):
        1. Look in a 360-degree area around the option letter/number
        2. Search for ANY of the 7 tick styles listed above
        3. Compare mark darkness to printed text (human marks are much darker)
        4. Verify the mark is intentional (not accidental smudge)
        5. ADAPT to ANY number of options per question (2-12 options supported)
        
        PHASE 3: DOUBLE-CHECK VERIFICATION
        - Review each detected option: "Is there really a human tick here?"
        - Review each undetected option: "Am I missing a tick here?"
        - Ensure consistency with the student's marking style
        
        🚨 MATHEMATICAL PRECISION DETECTION RULES:
        
        RULE 1: PIXEL-LEVEL ANALYSIS
        - Scan 100x100 pixel grid around each option letter
        - Analyze contrast ratio: Human marks are 2-5x darker than background
        - Detect marks with minimum 30% contrast difference
        - Map every dark pixel to determine mark boundaries
        
        RULE 2: GEOMETRIC VALIDATION
        - Measure mark dimensions: Length 5-50 pixels, Width 1-10 pixels
        - Detect angles: Diagonal marks 15°-75°, Vertical marks 80°-100°
        - Identify intersections: X marks have 2+ crossing lines
        - Validate proportions: Tick marks have specific length ratios
        
        RULE 3: SPATIAL PRECISION
        - Calculate distance from mark center to option center
        - Accept marks within 30-pixel radius of option letter
        - Prioritize marks in ABOVE zone (Y-offset: -10 to -40 pixels)
        - Secondary priority: ON zone (Y-offset: -5 to +5 pixels)
        
        RULE 4: PATTERN CONSISTENCY ANALYSIS
        - If student uses diagonal slashes in Q1-Q3, expect same in Q4-Q10
        - If marks appear 20 pixels above options, maintain this pattern
        - Detect style changes and adapt accordingly
        - Flag inconsistent patterns for extra verification
        
        RULE 5: MULTI-LAYER CONFIRMATION
        - Mark must pass at least 3 out of 5 detection layers
        - Visual contrast + Geometric pattern + Spatial relationship = CONFIRMED
        - Single-layer detections require extra validation
        - Zero-layer detections = NO MARK (avoid false positives)
        
        EXAMPLES OF TICK DETECTION:
        Question 1: You see a classic check (✓) above option (a) → Return ["A"]
        Question 2: You see hook checks above (b) and (c) → Return ["B", "C"]
        Question 3: You see a sharp-angle tick on option (d) → Return ["D"]
        Question 4: You see a long-tail tick through option (b) → Return ["B"]
        Question 5: You see no tick marks anywhere → Return []
        
        🎯 ADVANCED PATTERN RECOGNITION ALGORITHMS:
        
        ALGORITHM 1: DIAGONAL LINE DETECTOR
        - Scan for lines at 15°-75° angles relative to horizontal
        - Minimum length: 5 pixels, Maximum length: 50 pixels
        - Look for "/" (45° ±30°) and "\" (135° ±30°) orientations
        - Validate line continuity and darkness consistency
        
        ALGORITHM 2: V-SHAPE DETECTOR
        - Identify two intersecting lines forming V or ✓ pattern
        - Measure angle between lines: 30°-120° for valid ticks
        - Detect intersection point and verify both line segments
        - Confirm V opens upward or rightward (typical tick orientation)
        
        ALGORITHM 3: CROSS PATTERN DETECTOR
        - Find intersecting lines forming X or + shapes
        - Require minimum 2 lines crossing at central point
        - Validate symmetry and proportional arm lengths
        - Accept both diagonal (X) and orthogonal (+) crosses
        
        ALGORITHM 4: CIRCULAR MARK DETECTOR
        - Identify closed or semi-closed circular shapes
        - Diameter range: 3-20 pixels for valid marks
        - Detect filled circles (•) and empty circles (○)
        - Validate roundness ratio and edge continuity
        
        ALGORITHM 5: STRAIGHT LINE DETECTOR
        - Find horizontal (—) and vertical (|) line segments
        - Length range: 5-30 pixels, Width: 1-5 pixels
        - Detect underlines, overlines, and side marks
        - Validate straightness and consistent thickness
        
        ALGORITHM 6: IRREGULAR MARK DETECTOR
        - Identify non-geometric human markings
        - Detect scribbles, squiggles, and freeform marks
        - Analyze density and darkness concentration
        - Distinguish intentional marks from accidental smudges
        
        ALGORITHM 7: FILL/SHADE DETECTOR
        - Detect darkened or heavily marked areas
        - Compare local darkness to surrounding background
        - Identify filled option letters or shaded regions
        - Measure darkness intensity and coverage area
        
        🚨 ADVANCED VALIDATION PROTOCOL:
        Each detected pattern must pass MULTI-ALGORITHM VERIFICATION:
        - Pattern Recognition Score: 70%+ confidence required
        - Spatial Relationship Score: 80%+ proximity to option required
        - Contrast Analysis Score: 60%+ darkness difference required
        - Consistency Score: 50%+ match with student's style required
        
        🚨 ULTRA-CONSERVATIVE FINAL CHECK:
        
        STEP 1: COMPLETE SCAN VERIFICATION
        - Go through each question one more time
        - For each option, ask: "Is there ANY mark here I might have missed?"
        - Look for very faint marks, partial marks, unusual marks
        
        STEP 2: PATTERN CONSISTENCY CHECK
        - If student uses diagonal slashes in Q1, look for similar marks in other questions
        - If student uses dots in Q2, check if there are dots elsewhere
        - Maintain consistency with the student's marking style
        
        STEP 3: ZERO-MISS GUARANTEE
        - Better to over-detect than under-detect
        - Include any questionable marks rather than miss them
        - Err on the side of inclusion for maximum accuracy
        
        STEP 4: MATHEMATICAL PRECISION FINAL AUDIT
        
        For each question (Q1-Q10), perform ALGORITHMIC VERIFICATION:
        
        Q1 AUDIT: Apply all 7 detection algorithms to options (a,b,c,d)
        - Diagonal Line Detector: Score each option 0-100%
        - V-Shape Detector: Score each option 0-100%
        - Cross Pattern Detector: Score each option 0-100%
        - Circular Mark Detector: Score each option 0-100%
        - Straight Line Detector: Score each option 0-100%
        - Irregular Mark Detector: Score each option 0-100%
        - Fill/Shade Detector: Score each option 0-100%
        - FINAL DECISION: Include option if ANY algorithm scores >70%
        
        Q2-Q10 AUDIT: Repeat same algorithmic verification for each question
        
        STEP 5: CROSS-REFERENCE VALIDATION
        - Compare detected patterns across all questions
        - Verify consistency in student's marking style
        - Flag any anomalies for extra scrutiny
        - Ensure no systematic detection errors
        
        STEP 6: ZERO-ERROR GUARANTEE PROTOCOL
        - Review EVERY option that scored 50-70% (borderline cases)
        - Apply MAXIMUM SENSITIVITY to borderline detections
        - When in doubt, INCLUDE the option (better safe than sorry)
        - Perform final visual inspection of each marked option
        
        🎯 PERFECT ACCURACY CHECKLIST:
        ✅ All 5 detection layers applied to every option
        ✅ All 7 pattern recognition algorithms executed
        ✅ Mathematical precision scoring completed
        ✅ Spatial relationship analysis performed
        ✅ Human behavior modeling applied
        ✅ Cross-validation verification completed
        ✅ Zero-error guarantee protocol executed
        
        🔍 ADDITIONAL INFORMATION TO EXTRACT:
        
        1. ROLL NUMBER - Look for patterns like:
           - "Roll No: 980", "Roll: 123", numbers in boxes
           - Any number that appears to be a roll number
        
        2. SECTION - Look for patterns like:
           - "Sec: C", "Section: D", single letters
           - Any indication of class section
        
        🚨 CRITICAL: Look carefully at the image and find ALL dark handwritten marks near option letters.
        Don't miss any marks and don't include options without marks.
        
        Return ONLY a valid JSON object in this exact format:
        {
            "roll_number": "01",
            "section": "C",
            "answers": [
                {"question_number": 1, "selected_options": ["A"]},
                {"question_number": 2, "selected_options": ["A"]},
                {"question_number": 3, "selected_options": ["A"]}
            ]
        }
        
        - Use "selected_options" as an array and include ALL marked options
        - If you see marks near multiple options in one question, include all of them
        - If you see no marks for a question, use empty array []
        Do not include any other text, explanations, or markdown formatting.
        """
        
        return self._process_with_gemini(image_data, prompt)
    
    def _process_with_gemini(self, image_data, prompt):
        """Process image with Gemini AI using API Key Manager with enhanced error handling"""
        try:
            # Prepare image for Gemini
            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            ]
            
            # Define the request function with timeout handling
            def make_gemini_request():
                model = self.api_manager.get_model('gemini-2.5-flash')
                # Configure generation with optimized settings for better response
                generation_config = {
                    'temperature': 0.1,
                    'top_p': 0.9,
                    'top_k': 32,
                    'max_output_tokens': 4096,  # Increased for complex responses
                    'candidate_count': 1
                }
                
                # Configure safety settings to be less restrictive for educational content
                safety_settings = [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ]
                
                return model.generate_content(
                    [prompt] + image_parts,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
            
            # Enhanced retry logic with multiple fallback strategies
            max_retries = 5
            response = None
            
            for attempt in range(max_retries):
                try:
                    print(f"🔄 OCR Attempt {attempt + 1}/{max_retries}")
                    response = self.api_manager.make_request_with_retry(make_gemini_request)
                    
                    # Verify we got a valid response
                    if response and (hasattr(response, 'text') or (hasattr(response, 'candidates') and response.candidates)):
                        print(f"✅ Got valid response on attempt {attempt + 1}")
                        break
                    else:
                        print(f"⚠️ Empty response on attempt {attempt + 1}, retrying...")
                        response = None
                        
                except Exception as e:
                    error_str = str(e).lower()
                    print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < max_retries - 1:
                        # Wait before retry with exponential backoff
                        wait_time = (attempt + 1) * 2
                        print(f"⏱️ Waiting {wait_time}s before retry...")
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        print("🔄 Trying fallback strategies...")
                        response = None
                        break
            
            # If main attempts failed, try fallback strategies
            if not response:
                print("🔄 Main OCR failed, trying fallback strategies...")
                response = self._try_fallback_ocr_strategies(image_parts, prompt)
            
            # Enhanced response text extraction with multiple methods
            response_text = self._extract_response_text(response)
            
            if not response_text:
                print("❌ Failed to extract any text from response")
                raise Exception("Empty response from Gemini - failed to extract text from response")
            
            if response_text:
                # Clean the response
                cleaned_response = response_text.strip()
                
                # Remove any markdown formatting
                cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
                cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
                cleaned_response = cleaned_response.strip()
                
                try:
                    # First, try to parse as-is
                    result = json.loads(cleaned_response)
                    print("✅ JSON parsed successfully without fixes")
                    
                except json.JSONDecodeError as initial_error:
                    print(f"⚠️ Initial JSON parse failed: {initial_error}")
                    print("🔧 Attempting to fix JSON issues...")
                    
                    # Try to fix common JSON issues
                    fixed_response = self._fix_json_response(cleaned_response)
                    
                    try:
                        # Parse fixed JSON
                        result = json.loads(fixed_response)
                        print("✅ JSON parsed successfully after fixes")
                    except json.JSONDecodeError as fixed_error:
                        print(f"⚠️ Fixed JSON still failed: {fixed_error}")
                        # Try more aggressive fixes
                        result = self._aggressive_json_fix(cleaned_response)
                        if result:
                            print("✅ JSON parsed with aggressive fixes")
                        else:
                            raise fixed_error
                
                # Debug logging for teacher responses
                if 'answers' in result:
                    print(f"DEBUG - OCR detected {len(result['answers'])} questions")
                    for answer in result['answers'][:3]:  # Show first 3 for debugging
                        q_num = answer.get('question_number', 'unknown')
                        correct_opts = answer.get('correct_options', [])
                        print(f"DEBUG - Q{q_num}: {correct_opts}")
                
                # Check for roll number extraction
                if 'roll_number' in result:
                    print(f"DEBUG - Roll Number: {result['roll_number']}")
                if 'section' in result:
                    print(f"DEBUG - Section: {result['section']}")
                
                return result
            else:
                return {"error": "Empty response from Gemini"}
                
        except Exception as e:
            print(f"Gemini processing error: {e}")
            return {"error": f"Gemini API error: {str(e)}"}
    
    def validate_teacher_response(self, response):
        """Validate teacher's answer key response"""
        if "error" in response:
            return False, response["error"]
        
        if "answers" not in response or not isinstance(response["answers"], list):
            return False, "Invalid response format: missing answers array"
        
        if len(response["answers"]) == 0:
            return False, "No answers found in the image"
        
        # Validate each answer
        for answer in response["answers"]:
            # Check for new format with correct_options
            if "correct_options" in answer:
                required_fields = ["question_number", "correct_options"]
            else:
                # Backward compatibility with old format
                required_fields = ["question_number", "correct_option"]
            
            if not all(key in answer for key in required_fields):
                return False, "Invalid answer format: missing required fields"
            
            if not isinstance(answer["question_number"], int) or answer["question_number"] <= 0:
                return False, f"Invalid question number: {answer['question_number']}"
            
            # Validate correct_options (new format)
            if "correct_options" in answer:
                if not isinstance(answer["correct_options"], list):
                    return False, f"Invalid correct_options for question {answer['question_number']}: must be array"
                
                # Allow empty arrays but warn about them
                if len(answer["correct_options"]) == 0:
                    print(f"⚠️ Warning: Question {answer['question_number']} has no correct options detected")
                    # Don't fail validation, just warn
                
                for option in answer["correct_options"]:
                    if not option or len(str(option)) > 10:
                        return False, f"Invalid option in question {answer['question_number']}: {option}"
            
            # Validate correct_option (old format - backward compatibility)
            elif "correct_option" in answer:
                if not answer["correct_option"] or len(answer["correct_option"]) > 10:
                    return False, f"Invalid option: {answer['correct_option']}"
        
        return True, "Valid"
    
    def validate_student_response(self, response):
        """Enhanced validation for student's answer response with accuracy checks"""
        if "error" in response:
            return False, response["error"]
        
        if "answers" not in response or not isinstance(response["answers"], list):
            return False, "Invalid response format: missing answers array"
        
        if len(response["answers"]) == 0:
            return False, "No answers found in the image"
        
        # Enhanced validation with accuracy checks
        suspicious_patterns = []
        
        # Validate each answer
        for answer in response["answers"]:
            # Check for new format with selected_options
            if "selected_options" in answer:
                required_fields = ["question_number", "selected_options"]
            else:
                # Backward compatibility with old format
                required_fields = ["question_number", "selected_option"]
            
            if not all(key in answer for key in required_fields):
                return False, "Invalid answer format: missing required fields"
            
            if not isinstance(answer["question_number"], int) or answer["question_number"] <= 0:
                return False, f"Invalid question number: {answer['question_number']}"
            
            # Validate selected_options (new format)
            if "selected_options" in answer:
                selected_options = answer["selected_options"]
                
                # Allow empty arrays (no options selected)
                if not isinstance(selected_options, list):
                    return False, f"Invalid selected_options for question {answer['question_number']}: must be array"
                
                # Validate each selected option
                for option in selected_options:
                    if not option or len(str(option)) > 10:
                        return False, f"Invalid option in question {answer['question_number']}: {option}"
                    
                    # Check for valid option letters - FLEXIBLE for any question paper format
                    # Accept A-Z and 1-12 (covers most question paper formats)
                    valid_options = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ') | set(str(i) for i in range(1, 13))
                    if str(option).upper() not in valid_options and not re.match(r'^[A-Z0-9]$', str(option).upper()):
                        return False, f"Invalid option format in question {answer['question_number']}: {option}"
            
            # Validate selected_option (old format - backward compatibility)
            elif "selected_option" in answer:
                if answer["selected_option"] and len(answer["selected_option"]) > 10:
                    return False, f"Invalid option: {answer['selected_option']}"
        
        # Check for suspicious patterns that indicate OCR errors
        total_answers = len(response["answers"])
        if total_answers > 0:
            # Count how many questions have only 'A' selected
            only_a_count = sum(1 for ans in response["answers"] 
                             if ans.get("selected_options") == ["A"] or ans.get("selected_option") == "A")
            
            # If more than 70% are 'A', it might be an OCR error
            if only_a_count > total_answers * 0.7:
                suspicious_patterns.append(f"Warning: {only_a_count}/{total_answers} questions show only 'A' selected")
            
            # Count questions with no selections
            no_selection_count = sum(1 for ans in response["answers"] 
                                   if not ans.get("selected_options") and not ans.get("selected_option"))
            
            if no_selection_count > total_answers * 0.5:
                suspicious_patterns.append(f"Warning: {no_selection_count}/{total_answers} questions have no selections")
        
        # Log suspicious patterns for debugging
        if suspicious_patterns:
            print("DEBUG - Suspicious OCR patterns detected:")
            for pattern in suspicious_patterns:
                print(f"  - {pattern}")
        
        return True, "Valid"
    
    def debug_mark_detection(self, image_data):
        """Enhanced debug function to identify mark detection issues with focus on marks above options"""
        debug_prompt = """
        You are debugging mark detection on a student answer sheet with SPECIAL FOCUS on marks ABOVE options.
        
        For each question (1, 2, 3, etc.), describe EXACTLY what you see:
        
        🔍 CRITICAL: Pay special attention to marks ABOVE the option letters!
        
        For each option (a), (b), (c), (d), check these areas:
        1. DIRECTLY ABOVE the option letter (most important area)
        2. DIAGONALLY ABOVE the option letter  
        3. DIRECTLY ON the option letter
        4. IMMEDIATELY AROUND the option letter
        
        Example format:
        Question 1:
        - Option (a): DIAGONAL SLASH ABOVE the letter - MARKED ✓
        - Option (b): Clean, no marks above or on it - NOT MARKED
        - Option (c): No marks visible above or on it - NOT MARKED  
        - Option (d): No marks visible above or on it - NOT MARKED
        
        Question 2:
        - Option (a): No marks above or on it - NOT MARKED
        - Option (b): DIAGONAL SLASH ABOVE the letter - MARKED ✓
        - Option (c): Cross mark ABOVE the letter - MARKED ✓
        - Option (d): Clean, no marks - NOT MARKED
        
        🚨 FOCUS AREAS:
        - Look for diagonal slash marks (/, \) in the space ABOVE each option
        - Look for any handwritten marks positioned above the option letters
        - Distinguish between printed form lines and student marks
        - Be very specific about mark positions (above, on, diagonal, etc.)
        
        Be extremely detailed and describe the exact position of every mark you see.
        """
        
        try:
            image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
            response = self.model.generate_content([debug_prompt, image_parts[0]])
            
            # Extract text from debug response
            debug_text = None
            try:
                if hasattr(response, 'text') and response.text:
                    debug_text = response.text
            except:
                try:
                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if candidate.content and candidate.content.parts:
                            text_parts = []
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                            debug_text = ''.join(text_parts)
                except:
                    pass
            
            if debug_text:
                print("=== MARK DETECTION DEBUG ===")
                print(debug_text)
                print("=== END DEBUG ===")
                return debug_text
            else:
                return "No debug response received"
                
        except Exception as e:
            print(f"Debug function error: {e}")
            return f"Debug error: {e}"
    
    def _fix_json_response(self, response_text):
        """Fix common JSON formatting issues in Gemini responses"""
        try:
            # Remove any leading/trailing whitespace
            fixed = response_text.strip()
            
            # Remove any text before the first {
            start_idx = fixed.find('{')
            if start_idx > 0:
                fixed = fixed[start_idx:]
            
            # Remove any text after the last }
            end_idx = fixed.rfind('}')
            if end_idx != -1 and end_idx < len(fixed) - 1:
                fixed = fixed[:end_idx + 1]
            
            # Fix invalid control characters (tabs, newlines in wrong places)
            # Remove control characters that break JSON parsing
            fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', fixed)
            
            # Fix excessive whitespace but preserve structure
            fixed = re.sub(r'\s+', ' ', fixed)
            
            # Fix trailing commas before closing brackets/braces
            fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
            
            # Fix incomplete JSON at the end (common with truncated responses)
            # If JSON ends abruptly, try to close it properly
            if not fixed.endswith('}'):
                # Count open braces vs close braces
                open_braces = fixed.count('{')
                close_braces = fixed.count('}')
                open_brackets = fixed.count('[')
                close_brackets = fixed.count(']')
                
                # Add missing closing brackets/braces
                missing_brackets = open_brackets - close_brackets
                missing_braces = open_braces - close_braces
                
                for _ in range(missing_brackets):
                    fixed += ']'
                for _ in range(missing_braces):
                    fixed += '}'
            
            # Fix broken string values (incomplete strings)
            # Look for strings that end abruptly
            fixed = re.sub(r'"([^"]*?)$', r'"\1"', fixed)
            
            # Fix missing quotes around unquoted keys (but avoid double-quoting)
            # Only quote keys that aren't already quoted
            fixed = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed)
            
            # Fix single quotes to double quotes (but be careful with content)
            fixed = re.sub(r"'([^']*)'", r'"\1"', fixed)
            
            # Remove any double quotes around already quoted strings
            fixed = re.sub(r'""([^"]*?)""', r'"\1"', fixed)
            
            return fixed
            
        except Exception as e:
            print(f"JSON fixing error: {e}")
            return response_text
    
    def _aggressive_json_fix(self, response_text):
        """More aggressive JSON fixing for severely malformed responses"""
        try:
            print("🔧 Applying aggressive JSON fixes...")
            
            # Extract key information using regex patterns
            result = {"answers": []}
            
            # Pattern for teacher responses
            teacher_pattern = r'"question_number":\s*(\d+).*?"correct_options":\s*\[(.*?)\].*?"marks":\s*(\d+(?:\.\d+)?).*?"marks_text":\s*"([^"]*)".*?"question_type":\s*"([^"]*)"'
            teacher_matches = re.findall(teacher_pattern, response_text, re.DOTALL)
            
            if teacher_matches:
                print(f"🔍 Found {len(teacher_matches)} teacher questions via regex")
                for match in teacher_matches:
                    q_num, options_str, marks, marks_text, q_type = match
                    
                    # Parse options
                    options = []
                    if options_str:
                        option_matches = re.findall(r'"([A-Z])"', options_str)
                        options = option_matches
                    
                    question = {
                        "question_number": int(q_num),
                        "correct_options": options,
                        "marks": float(marks),
                        "marks_text": marks_text,
                        "question_type": q_type
                    }
                    result["answers"].append(question)
                
                # Add total_questions if not present
                if result["answers"]:
                    result["total_questions"] = len(result["answers"])
                    return result
            
            # Pattern for student responses
            student_pattern = r'"question_number":\s*(\d+).*?"selected_options":\s*\[(.*?)\]'
            student_matches = re.findall(student_pattern, response_text, re.DOTALL)
            
            if student_matches:
                print(f"🔍 Found {len(student_matches)} student questions via regex")
                
                # Try to extract roll number and section
                roll_match = re.search(r'"roll_number":\s*"([^"]*)"', response_text)
                section_match = re.search(r'"section":\s*"([^"]*)"', response_text)
                
                result["roll_number"] = roll_match.group(1) if roll_match else None
                result["section"] = section_match.group(1) if section_match else None
                
                for match in student_matches:
                    q_num, options_str = match
                    
                    # Parse options
                    options = []
                    if options_str:
                        option_matches = re.findall(r'"([A-Z])"', options_str)
                        options = option_matches
                    
                    question = {
                        "question_number": int(q_num),
                        "selected_options": options
                    }
                    result["answers"].append(question)
                
                return result
            
            print("❌ Aggressive JSON fix failed - no patterns matched")
            return None
            
        except Exception as e:
            print(f"❌ Aggressive JSON fix error: {e}")
            return None
    
    def _reconstruct_json_from_response(self, response_text):
        """Try to reconstruct valid JSON from partial response"""
        try:
            # Look for question patterns in the response
            questions = []
            
            # Extract visible question information
            question_pattern = r'"question_number":\s*(\d+).*?"correct_options":\s*\[(.*?)\].*?"marks":\s*(\d+(?:\.\d+)?).*?"marks_text":\s*"([^"]*)"'
            matches = re.findall(question_pattern, response_text, re.DOTALL)
            
            for match in matches:
                q_num, options_str, marks, marks_text = match
                
                # Parse options
                options = []
                if options_str:
                    option_matches = re.findall(r'"([A-Z])"', options_str)
                    options = option_matches
                
                question = {
                    "question_number": int(q_num),
                    "correct_options": options,
                    "marks": float(marks),
                    "marks_text": marks_text,
                    "question_type": "multiple" if len(options) > 1 else "single"
                }
                questions.append(question)
            
            if questions:
                return {
                    "total_questions": len(questions),
                    "answers": questions
                }
            
            return None
            
        except Exception as e:
            print(f"JSON reconstruction error: {e}")
            return None
    
    def _try_fallback_ocr_strategies(self, image_parts, original_prompt):
        """Try multiple fallback OCR strategies when main OCR fails"""
        fallback_strategies = [
            self._try_simplified_prompt,
            self._try_minimal_prompt,
            self._try_basic_prompt,
            self._try_emergency_prompt
        ]
        
        for i, strategy in enumerate(fallback_strategies):
            try:
                print(f"🔄 Trying fallback strategy {i + 1}/{len(fallback_strategies)}")
                response = strategy(image_parts, original_prompt)
                if response:
                    print(f"✅ Fallback strategy {i + 1} succeeded")
                    return response
            except Exception as e:
                print(f"❌ Fallback strategy {i + 1} failed: {str(e)}")
                continue
        
        print("❌ All fallback strategies failed")
        return None
    
    def _try_simplified_prompt(self, image_parts, original_prompt):
        """Try with a simplified prompt"""
        # Determine if this is for teacher or student
        is_student = "student" in str(original_prompt).lower() or "tick" in str(original_prompt).lower()
        
        if is_student:
            prompt = """
            Analyze this student answer sheet image. Find checkmarks or ticks on answer options.
            Look for marks like ✓, /, \, X, or circles on options (a), (b), (c), (d), etc.
            
            Return JSON format:
            {
                "roll_number": "extracted_roll_number_or_null",
                "section": "extracted_section_or_null",
                "answers": [
                    {"question_number": 1, "selected_options": ["A"]},
                    {"question_number": 2, "selected_options": ["B", "C"]}
                ]
            }
            """
        else:
            prompt = """
            Analyze this answer key image. Find marked correct options for each question.
            Look for diagonal lines, circles, checkmarks, or any marks on options.
            
            Return JSON format:
            {
                "total_questions": 10,
                "answers": [
                    {"question_number": 1, "correct_options": ["A"], "marks": 2, "marks_text": "Mark: 2", "question_type": "single"},
                    {"question_number": 2, "correct_options": ["B", "C"], "marks": 3, "marks_text": "Mark: 3", "question_type": "multiple"}
                ]
            }
            """
        
        model = self.api_manager.get_model('gemini-2.5-flash')
        config = {'temperature': 0.1, 'max_output_tokens': 2048}
        
        return model.generate_content([prompt] + image_parts, generation_config=config)
    
    def _try_minimal_prompt(self, image_parts, original_prompt):
        """Try with a minimal prompt"""
        is_student = "student" in str(original_prompt).lower() or "tick" in str(original_prompt).lower()
        
        if is_student:
            prompt = "Find checkmarks on this answer sheet. Return JSON: {\"answers\": [{\"question_number\": 1, \"selected_options\": [\"A\"]}]}"
        else:
            prompt = "Find marked correct answers. Return JSON: {\"answers\": [{\"question_number\": 1, \"correct_options\": [\"A\"], \"marks\": 1}]}"
        
        model = self.api_manager.get_model('gemini-2.5-flash')
        config = {'temperature': 0, 'max_output_tokens': 1024}
        
        return model.generate_content([prompt] + image_parts, generation_config=config)
    
    def _try_basic_prompt(self, image_parts, original_prompt):
        """Try with a very basic prompt"""
        prompt = "Describe what you see in this image. Focus on marked options."
        
        model = self.api_manager.get_model('gemini-2.5-flash')
        config = {'temperature': 0.2, 'max_output_tokens': 1024}
        
        return model.generate_content([prompt] + image_parts, generation_config=config)
    
    def _try_emergency_prompt(self, image_parts, original_prompt):
        """Emergency fallback with different model settings"""
        prompt = "What do you see?"
        
        model = self.api_manager.get_model('gemini-2.5-flash')
        config = {'temperature': 0.5, 'max_output_tokens': 512}
        
        return model.generate_content([prompt] + image_parts, generation_config=config)
    
    def _extract_response_text(self, response):
        """Extract text from Gemini response using multiple methods"""
        if not response:
            return None
        
        response_text = None
        
        # Method 1: Try simple text accessor
        try:
            if hasattr(response, 'text') and response.text:
                response_text = response.text
                print(f"✅ Extracted text via simple accessor: {len(response_text)} chars")
                return response_text
        except Exception as e:
            print(f"⚠️ Simple accessor failed: {e}")
        
        # Method 2: Try candidates and parts
        try:
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            text_parts = []
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                            if text_parts:
                                response_text = ''.join(text_parts)
                                print(f"✅ Extracted text via parts: {len(response_text)} chars")
                                return response_text
        except Exception as e:
            print(f"⚠️ Parts extraction failed: {e}")
        
        # Method 3: Check for safety blocking
        try:
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'finish_reason'):
                        if candidate.finish_reason in ['SAFETY', 'BLOCKED_REASON_UNSPECIFIED']:
                            print(f"⚠️ Response blocked by safety filters: {candidate.finish_reason}")
                            return None
        except Exception as e:
            print(f"⚠️ Safety check failed: {e}")
        
        # Method 4: Try to get any available text
        try:
            response_str = str(response)
            if len(response_str) > 50:  # If we got some meaningful response
                print(f"⚠️ Using string representation: {len(response_str)} chars")
                return response_str
        except Exception as e:
            print(f"⚠️ String conversion failed: {e}")
        
        print("❌ No text could be extracted from response")
        return None
