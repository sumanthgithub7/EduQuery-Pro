import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('HUGGINGFACE_API_KEY')
print(f"API Key: {api_key[:5]}...{api_key[-5:] if api_key and len(api_key) > 10 else ''}")

# Check if API key is set
if not api_key or api_key == "your_api_key_here":
    print("Error: Hugging Face API key is not set or is using the default value")
    print("Please update the .env file with your actual API key")
    exit(1)

# Set up headers
headers = {"Authorization": f"Bearer {api_key}"}

# Test question generation model
question_model_url = "https://api-inference.huggingface.co/models/t5-small"  # Alternative model
test_text = "The Python programming language was created by Guido van Rossum and was first released in 1991. Python is known for its simplicity and readability."

print("\nTesting question generation model...")
try:
    response = requests.post(
        question_model_url,
        headers=headers,
        json={"inputs": f"Generate a question about: {test_text}"}
    )
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {str(e)}")

# Test answer extraction model
answer_model_url = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
test_question = "Who created Python?"

print("\nTesting answer extraction model...")
try:
    response = requests.post(
        answer_model_url,
        headers=headers,
        json={
            "inputs": {
                "question": test_question,
                "context": test_text
            }
        }
    )
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {str(e)}")

print("\nTest completed.")