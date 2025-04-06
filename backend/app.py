from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app with correct template and static folders
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Hugging Face API configuration
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
if not HUGGINGFACE_API_KEY:
    print("Warning: HUGGINGFACE_API_KEY not found in environment variables. Using demo mode with mock data.")
    DEMO_MODE = True
else:
    DEMO_MODE = False

# Update model URL to use gpt2
QUESTION_MODEL_URL = "https://api-inference.huggingface.co/models/gpt2"

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}" if HUGGINGFACE_API_KEY else ""}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def build_prompt(passage):
    """Build a prompt for the Hugging Face model to generate MCQs"""
    return f"""Generate multiple choice questions based on the following passage:

{passage}

For every 150-200 words, generate 1 question. Each question must:
- Be based strictly on the passage
- Contain 1 question and 4 answer choices labeled A, B, C, and D
- Have only 1 correct answer
- Have distractor options that are relevant and logically close to the correct answer

Format the output as a JSON object with the following structure:
{{
    "questions": [
        {{
            "question": "...",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "answer": "B"
        }},
        ...
    ]
}}"""

def generate_questions_from_text(text):
    """Generate MCQs from text using the Hugging Face API"""
    try:
        # Calculate number of questions based on word count
        word_count = len(text.split())
        num_questions = max(1, word_count // 175)
        
        if DEMO_MODE:
            # Return mock data for demo mode
            return [
                {
                    'question': 'Who created the Python programming language?',
                    'options': [
                        'Guido van Rossum',
                        'James Gosling',
                        'Brendan Eich',
                        'Larry Wall'
                    ],
                    'correct_answer': 'Guido van Rossum'
                },
                {
                    'question': 'When was Python first released?',
                    'options': [
                        '1991',
                        '1995',
                        '1989',
                        '1993'
                    ],
                    'correct_answer': '1991'
                },
                {
                    'question': 'What is Python known for?',
                    'options': [
                        'Simplicity and readability',
                        'Complex syntax',
                        'Limited library support',
                        'Mobile development only'
                    ],
                    'correct_answer': 'Simplicity and readability'
                }
            ]
        
        # Build the prompt
        prompt = build_prompt(text)
        
        # Prepare the payload for the API
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 1024,
                "temperature": 0.7,
                "top_p": 0.9,
                "num_return_sequences": 1
            }
        }
        
        # Make the API request
        response = requests.post(QUESTION_MODEL_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Extract the generated text
        generated_text = result[0]['generated_text']
        
        # Try to extract the JSON part from the generated text
        try:
            # Find the JSON part in the generated text
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = generated_text[json_start:json_end]
                json_data = json.loads(json_str)
                
                # Convert the format to match what the frontend expects
                mcqs = []
                for q in json_data.get('questions', []):
                    mcqs.append({
                        'question': q['question'],
                        'options': q['options'],
                        'correct_answer': q['options'][ord(q['answer']) - ord('A')] if 'answer' in q else q['options'][0]
                    })
                
                return mcqs
            else:
                # If no JSON found, return an error
                return []
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")
            return []
            
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def handle_upload():
    """Handle file upload or text input"""
    try:
        # Check if a file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file and allowed_file(file.filename):
                # TODO: Process PDF file and extract text
                # For now, return an error
                return jsonify({'error': 'PDF processing not implemented yet'}), 400
            else:
                return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400
        
        # Check if text was provided
        elif 'text' in request.form:
            text = request.form['text']
            if not text.strip():
                return jsonify({'error': 'No text provided'}), 400
            
            # Generate MCQs from the text
            mcqs = generate_questions_from_text(text)
            
            if not mcqs:
                return jsonify({'error': 'Failed to generate questions. Please try again with different text.'}), 400
            
            return jsonify({'mcqs': mcqs})
        
        else:
            return jsonify({'error': 'No file or text provided'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    """Generate MCQs from text"""
    try:
        data = request.get_json()
        if not data or 'passage' not in data:
            return jsonify({'error': 'No passage provided'}), 400
        
        passage = data['passage']
        mcqs = generate_questions_from_text(passage)
        
        if not mcqs:
            return jsonify({'error': 'Failed to generate questions. Please try again with different text.'}), 400
        
        return jsonify({'mcqs': mcqs})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0')