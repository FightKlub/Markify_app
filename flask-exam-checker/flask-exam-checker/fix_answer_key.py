#!/usr/bin/env python3
"""
Fix Answer Key - Update database with correct teacher answers
This script will update the database with the exact expected answers
"""

import os
import psycopg2
from urllib.parse import urlparse

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL', "postgresql://neondb_owner:npg_Q0NxwyzY5rBt@ep-cold-wildflower-a8n97rw3-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require")

def fix_answer_key():
    """Update the database with correct teacher answers"""
    
    # Expected correct answers based on your teacher answer key
    correct_answers = {
        1: {"correct_options": ["B", "D"], "marks": 2, "marks_text": "Mark: 2"},
        2: {"correct_options": ["C"], "marks": 3, "marks_text": "Mark: 3"},
        3: {"correct_options": ["A", "D", "E"], "marks": 6, "marks_text": "Mark: a=2, d=3, e=1"},
        4: {"correct_options": ["A", "D"], "marks": 2, "marks_text": "Mark: 2"},
        5: {"correct_options": ["C", "D"], "marks": 2, "marks_text": "Mark: 2"},
        6: {"correct_options": ["E", "F"], "marks": 4, "marks_text": "Mark: 4"},
        7: {"correct_options": ["A", "C"], "marks": 4, "marks_text": "Mark: 4"},
        8: {"correct_options": ["B", "D"], "marks": 5, "marks_text": "Mark: b=2, d=3"},
        9: {"correct_options": ["B", "C"], "marks": 3, "marks_text": "Mark: 3"},
        10: {"correct_options": ["A", "B"], "marks": 4, "marks_text": "Mark: 4"}
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔧 FIXING ANSWER KEY IN DATABASE")
        print("=" * 50)
        
        # Get the paper_id (assuming it's the latest paper)
        cursor.execute("SELECT id FROM question_papers ORDER BY created_at DESC LIMIT 1")
        paper_result = cursor.fetchone()
        
        if not paper_result:
            print("❌ No question papers found in database")
            return
        
        paper_id = paper_result[0]
        print(f"📋 Updating paper ID: {paper_id}")
        
        # Update each question
        for question_num, data in correct_answers.items():
            correct_options = data["correct_options"]
            marks = data["marks"]
            marks_text = data["marks_text"]
            question_type = "single" if len(correct_options) == 1 else "multiple"
            correct_option = correct_options[0]  # For backward compatibility
            
            print(f"\n📝 Q{question_num}: {correct_options} - {marks} marks - {marks_text}")
            
            # Check if question exists
            cursor.execute("""
                SELECT id FROM correct_answers 
                WHERE paper_id = %s AND question_number = %s
            """, (paper_id, question_num))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing question
                cursor.execute("""
                    UPDATE correct_answers 
                    SET correct_option = %s, correct_options = %s, marks = %s, 
                        question_type = %s, marks_text = %s
                    WHERE paper_id = %s AND question_number = %s
                """, (
                    correct_option, correct_options, marks, 
                    question_type, marks_text, paper_id, question_num
                ))
                print(f"   ✅ Updated Q{question_num}")
            else:
                # Insert new question
                cursor.execute("""
                    INSERT INTO correct_answers 
                    (paper_id, question_number, correct_option, correct_options, marks, question_type, marks_text)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    paper_id, question_num, correct_option, correct_options, 
                    marks, question_type, marks_text
                ))
                print(f"   ✅ Inserted Q{question_num}")
        
        # Commit changes
        conn.commit()
        
        print("\n🎉 ANSWER KEY SUCCESSFULLY UPDATED!")
        print("\nExpected Results:")
        print("Q1: 2 marks (B,D full match)")
        print("Q2: 0 marks (A,C but only C correct - A wrong)")
        print("Q3: 4 marks (D,E from A,D,E = d=3 + e=1)")
        print("Q4: 0 marks (A,C but A,D correct - C wrong)")
        print("Q5: 0 marks (B,D but C,D correct - B wrong)")
        print("Q6: 4 marks (E,F full match)")
        print("Q7: 4 marks (A,C full match)")
        print("Q8: 5 marks (B,D full match = b=2 + d=3)")
        print("Q9: 0 marks (A,B but B,C correct - A wrong)")
        print("Q10: 0 marks (B,C but A,B correct - C wrong)")
        print("TOTAL: 19 marks")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_answer_key()
