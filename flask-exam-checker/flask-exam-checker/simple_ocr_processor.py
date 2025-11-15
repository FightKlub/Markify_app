import base64
import io
from io import BytesIO
import json
import logging
import os
import re
from PIL import Image
from api_key_manager import get_api_manager

class SimpleOCRProcessor:
    def __init__(self, api_key=None):
        self.api_manager = get_api_manager()
        self.logger = logging.getLogger(__name__)
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            print(f"🔑 Simple OCR Processor initialized with {self.api_manager.get_status()['total_keys']} API keys")
    
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
        Look at this answer key image and find marked correct answers.
        
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
        """
        return self._process_with_gemini(image_data, prompt)
    
    def extract_student_answers(self, image_data):
        """Extract student's selected answers"""
        prompt = """
        Look at this student answer sheet and find marked options.
        
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
        """
        return self._process_with_gemini(image_data, prompt)
    
    def _process_with_gemini(self, image_data, prompt):
        """Process image with Gemini AI - SIMPLE AND WORKING"""
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
            
            # SIMPLE response extraction - NO COMPLEX FALLBACKS
            response_text = None
            try:
                response_text = response.text
            except:
                try:
                    response_text = response.candidates[0].content.parts[0].text
                except:
                    response_text = None
            
            if not response_text:
                return {"error": "Empty response from Gemini"}
            
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
