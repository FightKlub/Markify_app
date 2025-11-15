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
        self.api_manager = get_api_manager()
        self.logger = logging.getLogger(__name__)
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            print(f"🔑 OCR Processor initialized with {self.api_manager.get_status()['total_keys']} API keys")
    
    def preprocess_image(self, image_file):
        """Preprocess image for OCR processing"""
        try:
            image = Image.open(image_file)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            max_dimension = 1400
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
            
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=80, optimize=True)
            img_byte_arr = img_byte_arr.getvalue()
            
            print(f"DEBUG - Final image size: {len(img_byte_arr)} bytes")
            return base64.b64encode(img_byte_arr).decode()
            
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return None
    
    def extract_teacher_answers(self, image_data):
        """Extract correct answers from teacher's answer key"""
        prompt = """
        Analyze this answer key image and find the marked correct answers.
        
        Look for any marks that indicate correct answers: lines, circles, checkmarks, bold text.
        Find the marking scheme and marks for each question.
        Adapt to whatever format you see.
        
        Return JSON:
        {
            "total_questions": N,
            "answers": [
                {
                    "question_number": 1,
                    "correct_options": ["marked_options"],
                    "marks": total_marks,
                    "marks_text": "exact_text_found",
                    "question_type": "single_or_multiple"
                }
            ]
        }
        """
        return self._process_with_gemini(image_data, prompt)
    
    def extract_student_answers(self, image_data):
        """Extract student's selected answers"""
        prompt = """
        Look at this student answer sheet and find marked options.
        
        CRITICAL: Compare each option to others in the same question.
        Only include options that look DIFFERENT (marked vs unmarked).
        If an option looks identical to others, do NOT include it.
        
        Look for any clear marks: checkmarks, lines, circles, bold marks.
        Adapt to any question format you see.
        
        Return JSON:
        {
            "roll_number": "found_or_null",
            "section": "found_or_null",
            "total_questions": N,
            "answers": [
                {
                    "question_number": 1,
                    "selected_options": ["marked_options"]
                }
            ]
        }
        """
        return self._process_with_gemini(image_data, prompt)
    
    def _process_with_gemini(self, image_data, prompt):
        """Process image with Gemini AI"""
        try:
            image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
            
            def make_gemini_request():
                model = self.api_manager.get_model('gemini-2.5-flash')
                generation_config = {
                    'temperature': 0.1,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
                
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
                ]
                
                return model.generate_content(
                    [prompt] + image_parts,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
            
            response = self.api_manager.make_request_with_retry(make_gemini_request)
            
            # Extract text from response
            response_text = None
            try:
                if hasattr(response, 'text') and response.text:
                    response_text = response.text
            except:
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        text_parts = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        response_text = ''.join(text_parts)
            
            if response_text:
                # Clean the response
                cleaned_response = response_text.strip()
                cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
                cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
                cleaned_response = cleaned_response.strip()
                
                # Fix common JSON issues
                cleaned_response = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', cleaned_response)
                cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
                cleaned_response = re.sub(r',(\s*[}\]])', r'\1', cleaned_response)
                
                try:
                    result = json.loads(cleaned_response)
                    return result
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"📄 Raw response: {cleaned_response[:500]}")
                    return {"error": f"Invalid JSON response: {str(e)}"}
            else:
                return {"error": "Empty response from Gemini"}
                
        except Exception as e:
            print(f"Gemini processing error: {e}")
            return {"error": f"Gemini API error: {str(e)}"}
    
    def validate_teacher_response(self, response):
        """Validate teacher OCR response"""
        if isinstance(response, dict) and 'error' in response:
            return False, response['error']
        
        if not isinstance(response, dict) or 'answers' not in response:
            return False, "Invalid response format"
        
        if not response['answers']:
            return False, "No answers found in response"
        
        return True, "Valid response"
    
    def validate_student_response(self, response):
        """Validate student OCR response"""
        if isinstance(response, dict) and 'error' in response:
            return False, response['error']
        
        if not isinstance(response, dict) or 'answers' not in response:
            return False, "Invalid response format"
        
        return True, "Valid response"
