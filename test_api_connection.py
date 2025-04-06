import requests
import json

def test_upload_endpoint():
    print("Testing /upload endpoint...")
    
    # Test with text input
    text_data = {
        "text": "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and was first released in 1991."
    }
    
    try:
        response = requests.post('http://localhost:5000/upload', json=text_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error connecting to API: {str(e)}")

def test_generate_endpoint():
    print("\nTesting /generate endpoint...")
    
    # Test with text input
    text_data = {
        "text": "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and was first released in 1991."
    }
    
    try:
        response = requests.post('http://localhost:5000/generate', json=text_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error connecting to API: {str(e)}")

if __name__ == "__main__":
    print("Starting API tests...")
    test_upload_endpoint()
    test_generate_endpoint()
    print("\nTests completed.") 