#!/usr/bin/env python3
"""
Debug script to see exactly what Gemini is returning
"""

import base64
from io import BytesIO
from PIL import Image
from api_key_manager import get_api_manager

def debug_gemini_response():
    """Debug what Gemini is actually returning"""
    
    # Get a test image (create a simple one)
    img = Image.new('RGB', (100, 100), color='white')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_data = base64.b64encode(img_byte_arr.getvalue()).decode()
    
    # Simple test prompt
    prompt = "Look at this image and return JSON: {\"test\": \"response\"}"
    
    try:
        api_manager = get_api_manager()
        model = api_manager.get_model('gemini-2.5-flash')
        
        image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
        
        print("🔍 Making Gemini request...")
        response = model.generate_content([prompt] + image_parts)
        
        print("\n" + "="*50)
        print("📊 GEMINI RESPONSE ANALYSIS")
        print("="*50)
        
        print(f"Response type: {type(response)}")
        print(f"Response dir: {[attr for attr in dir(response) if not attr.startswith('_')]}")
        
        # Check if response has text attribute
        print(f"\nHas 'text' attribute: {hasattr(response, 'text')}")
        if hasattr(response, 'text'):
            try:
                text = response.text
                print(f"response.text works: {len(text)} chars")
                print(f"response.text content: {text[:200]}...")
            except Exception as e:
                print(f"response.text FAILS: {e}")
        
        # Check candidates
        print(f"\nHas 'candidates' attribute: {hasattr(response, 'candidates')}")
        if hasattr(response, 'candidates'):
            print(f"Number of candidates: {len(response.candidates) if response.candidates else 0}")
            
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                print(f"Candidate type: {type(candidate)}")
                print(f"Candidate dir: {[attr for attr in dir(candidate) if not attr.startswith('_')]}")
                
                # Check candidate content
                print(f"Has 'content' attribute: {hasattr(candidate, 'content')}")
                if hasattr(candidate, 'content'):
                    content = candidate.content
                    print(f"Content type: {type(content)}")
                    print(f"Content dir: {[attr for attr in dir(content) if not attr.startswith('_')]}")
                    
                    # Check content parts
                    print(f"Has 'parts' attribute: {hasattr(content, 'parts')}")
                    if hasattr(content, 'parts'):
                        parts = content.parts
                        print(f"Number of parts: {len(parts) if parts else 0}")
                        
                        if parts and len(parts) > 0:
                            part = parts[0]
                            print(f"Part type: {type(part)}")
                            print(f"Part dir: {[attr for attr in dir(part) if not attr.startswith('_')]}")
                            
                            # Check part text
                            print(f"Has 'text' attribute: {hasattr(part, 'text')}")
                            if hasattr(part, 'text'):
                                try:
                                    part_text = part.text
                                    print(f"part.text works: {len(part_text)} chars")
                                    print(f"part.text content: {part_text[:200]}...")
                                except Exception as e:
                                    print(f"part.text FAILS: {e}")
                        else:
                            print("❌ No parts found!")
                    else:
                        print("❌ No 'parts' attribute in content!")
                else:
                    print("❌ No 'content' attribute in candidate!")
            else:
                print("❌ No candidates found!")
        
        # Check finish reason
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason'):
                print(f"\nFinish reason: {candidate.finish_reason}")
            
            if hasattr(candidate, 'safety_ratings'):
                print(f"Safety ratings: {candidate.safety_ratings}")
        
        print("\n" + "="*50)
        print("🎯 CONCLUSION")
        print("="*50)
        
        # Try to extract text using different methods
        methods = []
        
        # Method 1: Direct text
        try:
            text1 = response.text
            methods.append(f"✅ response.text: {len(text1)} chars")
        except Exception as e:
            methods.append(f"❌ response.text: {e}")
        
        # Method 2: Parts
        try:
            text2 = response.candidates[0].content.parts[0].text
            methods.append(f"✅ parts[0].text: {len(text2)} chars")
        except Exception as e:
            methods.append(f"❌ parts[0].text: {e}")
        
        # Method 3: Join parts
        try:
            parts = response.candidates[0].content.parts
            text_parts = [part.text for part in parts if hasattr(part, 'text')]
            text3 = ''.join(text_parts)
            methods.append(f"✅ joined parts: {len(text3)} chars")
        except Exception as e:
            methods.append(f"❌ joined parts: {e}")
        
        for method in methods:
            print(method)
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_gemini_response()
