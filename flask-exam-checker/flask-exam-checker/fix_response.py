#!/usr/bin/env python3
"""
Fix the response extraction in OCR
"""

def fix_response_extraction():
    # Read the current file
    with open('ocr_utils.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple fix - replace the complex response extraction with basic one
    old_complex = '''            try:
                # Try the simple accessor first
                if hasattr(response, 'text') and response.text:
                    response_text = response.text
                    print(f"✅ Got response text via simple accessor: {len(response_text)} chars")
            except Exception as simple_error:
                print(f"⚠️ Simple accessor failed: {simple_error}")
                # Use the proper parts accessor for complex responses
                try:
                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if candidate.content and candidate.content.parts:
                            # Combine all text parts
                            text_parts = []
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                            response_text = ''.join(text_parts)
                            print(f"✅ Got response text via parts accessor: {len(response_text)} chars")
                        else:
                            print("⚠️ No content parts found in candidate")
                    else:
                        print("⚠️ No candidates found in response")
                except Exception as e:
                    print(f"❌ Failed to extract response text: {str(e)}")'''
    
    new_simple = '''            try:
                if hasattr(response, 'text') and response.text:
                    response_text = response.text
                else:
                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if candidate.content and candidate.content.parts:
                            text_parts = []
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                            response_text = ''.join(text_parts)
            except Exception as e:
                print(f"Response extraction error: {e}")'''
    
    # Apply the fix
    if old_complex in content:
        content = content.replace(old_complex, new_simple)
        
        with open('ocr_utils.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('✅ Fixed response extraction')
        return True
    else:
        print('❌ Complex extraction code not found')
        return False

if __name__ == "__main__":
    fix_response_extraction()
