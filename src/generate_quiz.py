#!/usr/bin/env python3
"""
Generate a quiz based on the lesson plan using Google's Gemini API.
This script reads lesson_plan.json and generates a quiz.json file.
"""

import os
import json
import yaml
import google.generativeai as genai

# Paths
LESSON_PLAN_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lesson_plan.json')
QUIZ_PATH = os.path.join(os.path.dirname(__file__), 'data', 'quiz.json')

def load_config():
    """Load configuration from config.yml."""
    try:
        with open("config.yml", "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config.yml: {e}")
        return None

def get_gemini_api_key():
    """Get Gemini API key from config or environment."""
    config = load_config()
    api_key = None
    
    if config and 'google_ai_studio_api_key' in config:
        api_key = config['google_ai_studio_api_key']
    else:
        api_key = os.getenv('GOOGLE_AI_STUDIO_API_KEY')
    
    return api_key

def load_lesson_plan():
    """Load the lesson plan from JSON file."""
    try:
        with open(LESSON_PLAN_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading lesson plan: {e}")
        return {
            "topic": "Quantum Physics",
            "work_type": "ASSIGNMENT",
            "response_type": "multiple_choice_question",
            "number_of_questions": 1
        }

def generate_quiz_with_gemini(lesson_plan):
    """Generate a quiz using Gemini API based on the lesson plan or content."""
    api_key = get_gemini_api_key()
    if not api_key:
        print("No Gemini API key found. Using fallback quiz generation.")
        return generate_fallback_quiz(lesson_plan)
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    topic = lesson_plan.get('topic', 'General Knowledge')
    num_questions = int(lesson_plan.get('number_of_questions', 1))
    response_type = lesson_plan.get('response_type', 'multiple_choice_question')
    content = lesson_plan.get('content', '')
    
    # Create prompt for Gemini with content if available
    if content:
        prompt = f"""
        Based on the following educational content, generate a quiz with {num_questions} questions.
        The response type should be {response_type}.
        
        Educational Content:
        {content}
        
        For each question, provide:
        1. The question text based on the content above
        2. Four possible answers (if multiple choice)
        3. The correct answer
        
        Format your response as a JSON object with this structure:
        {{
          "title": "Quiz: {topic}",
          "questions": [
            {{
              "question": "Question text",
              "type": "{response_type}",
              "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
              "answer": "Correct option"
            }}
            // more questions...
          ]
        }}
        
        IMPORTANT: Make sure your response is valid JSON that can be parsed.
        """
    else:
        # Fallback to topic-based generation
        prompt = f"""
        Generate a quiz about {topic} with {num_questions} questions.
        The response type should be {response_type}.
        
        For each question, provide:
        1. The question text
        2. Four possible answers (if multiple choice)
        3. The correct answer
        
        Format your response as a JSON object with this structure:
        {{
          "title": "Quiz: {topic}",
          "questions": [
            {{
              "question": "Question text",
              "type": "{response_type}",
              "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
              "answer": "Correct option"
            }}
            // more questions...
          ]
        }}
        
        IMPORTANT: Make sure your response is valid JSON that can be parsed.
        """
    
    try:
        response = model.generate_content(prompt)
        # Extract JSON from the response
        response_text = response.text
        
        # Find JSON content (between curly braces)
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            quiz_data = json.loads(json_str)
            return quiz_data
        else:
            print("Could not extract JSON from Gemini response")
            return generate_fallback_quiz(lesson_plan)
    
    except Exception as e:
        print(f"Error generating quiz with Gemini: {e}")
        return generate_fallback_quiz(lesson_plan)

def generate_fallback_quiz(lesson_plan):
    """Generate a fallback quiz if Gemini API fails."""
    topic = lesson_plan.get('topic', 'General Knowledge')
    num_questions = int(lesson_plan.get('number_of_questions', 5))
    
    # Generate multiple fallback questions
    questions = []
    question_templates = [
        f"What is the main concept of {topic}?",
        f"Which of the following best describes {topic}?",
        f"What are the key principles of {topic}?",
        f"How is {topic} commonly applied?",
        f"What is an important characteristic of {topic}?"
    ]
    
    for i in range(min(num_questions, len(question_templates))):
        questions.append({
            "question": question_templates[i],
            "type": lesson_plan.get('response_type', 'multiple_choice_question'),
            "options": [
                f"The fundamental principles of {topic}",
                f"The history of {topic}",
                f"The applications of {topic}",
                f"The limitations of {topic}"
            ],
            "answer": f"The fundamental principles of {topic}"
        })
    
    return {
        "title": f"Quiz: {topic}",
        "questions": questions
    }

def save_quiz(quiz_data):
    """Save the generated quiz to quiz.json."""
    try:
        with open(QUIZ_PATH, 'w') as f:
            json.dump(quiz_data, f, indent=2)
        print(f"Quiz saved to {QUIZ_PATH}")
        return True
    except Exception as e:
        print(f"Error saving quiz: {e}")
        return False

def main():
    """Main function to generate and save a quiz."""
    print("Loading lesson plan...")
    lesson_plan = load_lesson_plan()
    
    print(f"Generating quiz for topic: {lesson_plan.get('topic', 'Unknown')}")
    quiz_data = generate_quiz_with_gemini(lesson_plan)
    
    print("Saving quiz...")
    success = save_quiz(quiz_data)
    
    if success:
        print("Quiz generation completed successfully!")
    else:
        print("Quiz generation failed.")

if __name__ == "__main__":
    main()