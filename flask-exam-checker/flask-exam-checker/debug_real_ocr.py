#!/usr/bin/env python3
"""
Debug real OCR with actual image processing
"""

import base64
from io import BytesIO
from PIL import Image
from api_key_manager import get_api_manager

def debug_real_ocr():
    """Test with actual OCR prompts and larger image"""
    
    # Create a more realistic test image (like your actual images)
    img = Image.new('RGB', (1280, 1004), color='white')
    
    # Add some text to simulate an answer sheet
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Try to add text (fallback if font not available)
    try:
        # Use default font
        draw.text((100, 100), "Q1. A) Option A  B) Option B  C) Option C", fill='black')
        draw.text((100, 200), "Q2. A) Option A  B) Option B  C) Option C", fill='black')
        draw.text((100, 300), "Mark: 2", fill='black')
    except:
        # If font fails, just use basic shapes
        draw.rectangle([100, 100, 200, 150], outline='black')
        draw.rectangle([100, 200, 200, 250], outline='black')
    
    # Convert to base64 like the real OCR
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=80)
    image_data = base64.b64encode(img_byte_arr.getvalue()).decode()
    
    print(f"📸 Created test image: {len(image_data)} chars base64")
    
    # Use the ACTUAL teacher OCR prompt from your system
    teacher_prompt = '''
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
    '''
    
    try:
        api_manager = get_api_manager()
        model = api_manager.get_model('gemini-2.5-flash')
        
        image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
        
        # Use the same config as real OCR
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
        
        print("🔍 Making REAL OCR request...")
        response = model.generate_content(
            [teacher_prompt] + image_parts,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        print("\n" + "="*50)
        print("📊 REAL OCR RESPONSE ANALYSIS")
        print("="*50)
        
        # Test all extraction methods
        print("Testing extraction methods:")
        
        # Method 1: response.text
        try:
            text1 = response.text
            print(f"✅ response.text: {len(text1)} chars")
            print(f"Content preview: {text1[:200]}...")
        except Exception as e:
            print(f"❌ response.text FAILED: {e}")
        
        # Method 2: parts
        try:
            text2 = response.candidates[0].content.parts[0].text
            print(f"✅ parts[0].text: {len(text2)} chars")
        except Exception as e:
            print(f"❌ parts[0].text FAILED: {e}")
        
        # Check for safety blocking
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                print(f"\\nFinish reason: {candidate.finish_reason}")
                if candidate.finish_reason != 1:  # 1 = STOP (normal completion)
                    print(f"⚠️ ABNORMAL FINISH REASON: {candidate.finish_reason}")
            
            if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                print(f"Safety ratings: {candidate.safety_ratings}")
        
        # Check if response is empty
        response_text = None
        try:
            response_text = response.text
        except:
            try:
                response_text = response.candidates[0].content.parts[0].text
            except:
                response_text = None
        
        if not response_text:
            print("❌ EMPTY RESPONSE DETECTED!")
            print("This is why your OCR is failing!")
        else:
            print(f"✅ Response extracted successfully: {len(response_text)} chars")
            
            # Try to parse as JSON
            import json
            try:
                parsed = json.loads(response_text.strip().replace('```json', '').replace('```', ''))
                print(f"✅ JSON parsing successful: {parsed}")
            except Exception as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Raw response: {response_text}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_real_ocr()
