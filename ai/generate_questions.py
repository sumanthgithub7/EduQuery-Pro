import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Get the absolute path to the backend directory
BACKEND_DIR = Path(__file__).parent.parent / 'backend'

# Load API Key from the correct .env file location
load_dotenv(BACKEND_DIR / '.env')
TOKEN = os.getenv("HUGGINGFACE_API_KEY")

# Using specialized models for question and answer generation
QUESTION_API_URL = "https://api-inference.huggingface.co/models/valhalla/t5-base-qg-hl"
ANSWER_API_URL = "https://api-inference.huggingface.co/models/valhalla/t5-base-qa-qg-hl"

def generate_questions(text, max_retries=3, retry_delay=2):
    """
    Generate questions and answers from text using Hugging Face's T5 models.
    
    Args:
        text (str): The text to generate questions from
        max_retries (int): Maximum number of retries for failed requests
        retry_delay (int): Delay in seconds between retries
        
    Returns:
        tuple: (list of questions, list of answers)
        
    Raises:
        Exception: If API key is missing, invalid, or if there are API errors
        ValueError: If input text is invalid or too short
    """
    import time

    try:
        # Verify API key is set
        if not TOKEN:
            raise Exception(f"Hugging Face API key not found. Please check your .env file at {BACKEND_DIR / '.env'}")

        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        # Validate input text
        if not text or len(text.strip()) < 10:
            raise Exception("Input text is too short or empty. Please provide more detailed text.")

        # Preprocess and format text for T5 question generation model
        # Clean and normalize the text first
        text = text.strip().replace('\n', ' ').replace('\r', ' ')
        while '  ' in text:  # Remove multiple spaces
            text = text.replace('  ', ' ')
            
        # Split text into meaningful segments using multiple delimiters
        delimiters = ['.', ';', '!', '?']
        text_parts = []
        current_text = text
        
        # First split by all delimiters to get basic segments
        import re
        pattern = '|'.join(map(re.escape, delimiters))
        parts = [p.strip() for p in re.split(pattern, current_text)]
        
        # Process each part to ensure it's suitable for question generation
        for part in parts:
            # Skip if part is too short
            if len(part) < 20:
                continue
                
            # Skip if part doesn't contain enough words
            words = part.split()
            if len(words) < 4:
                continue
                
            # Skip if part contains mostly numbers or special characters
            alpha_count = sum(c.isalpha() for c in part)
            if alpha_count / len(part) < 0.5:
                continue
                
            text_parts.append(part)
            
        # Format prompts for the model with proper highlighting
        prompts = []
        for part in text_parts:
            # Format prompts for both question and answer generation
            question_prompt = f"generate question: <hl> {part} <hl>\nGenerate a clear and specific question about the main concept in this text."
            prompts.append((question_prompt, part))
        
        all_questions = []
        all_answers = []
        for question_prompt, context in prompts:
            # Generate question first
            question_payload = {
                "inputs": question_prompt,
                "wait_for_model": True
            }

            last_error = None
            for retry in range(max_retries):
                try:
                    # Make the API request for question generation
                    response = requests.post(QUESTION_API_URL, headers=headers, json=question_payload, timeout=30)
                    
                    # Handle authentication errors
                    if response.status_code == 401:
                        raise Exception("Invalid Hugging Face API key. Please check your API key in the .env file.")
                    elif response.status_code == 403:
                        raise Exception("Access denied. You may not have access to this model. Please check your Hugging Face account permissions.")
                    elif response.status_code == 429:
                        print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    elif response.status_code == 503:
                        print(f"Service temporarily unavailable. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    
                    response.raise_for_status()
                    
                    # Process the question response
                    result = response.json()
                    question = None
                    if isinstance(result, list) and result:
                        for item in result:
                            if isinstance(item, str) and '?' in item:
                                question = item.strip()
                                break
                            elif isinstance(item, dict) and 'generated_text' in item:
                                text = item['generated_text'].strip()
                                if '?' in text:
                                    question = text
                                    break
                    elif isinstance(result, dict) and 'generated_text' in result:
                        text = result['generated_text'].strip()
                        if '?' in text:
                            question = text
                    
                    if question:
                        all_questions.append(question)
                        # Generate answer for this question
                        answer_prompt = f"answer: question: {question} context: {context}"
                        answer_payload = {
                            "inputs": answer_prompt,
                            "wait_for_model": True,
                            "options": {"wait_for_model": True}
                        }
                        
                        # Add retry logic for answer generation
                        answer = None
                        for answer_retry in range(max_retries):
                            try:
                                answer_response = requests.post(ANSWER_API_URL, headers=headers, json=answer_payload, timeout=30)
                                
                                # Handle answer generation API errors
                                if answer_response.status_code == 429:
                                    print(f"Rate limit exceeded for answer generation. Retrying in {retry_delay} seconds...")
                                    time.sleep(retry_delay)
                                    continue
                                elif answer_response.status_code == 503:
                                    print(f"Service temporarily unavailable for answer generation. Retrying in {retry_delay} seconds...")
                                    time.sleep(retry_delay)
                                    continue
                                
                                answer_response.raise_for_status()
                                answer_result = answer_response.json()
                                
                                # Process answer response
                                if isinstance(answer_result, list) and answer_result:
                                    answer = answer_result[0].get('generated_text', '').strip()
                                elif isinstance(answer_result, dict):
                                    answer = answer_result.get('generated_text', '').strip()
                                
                                # Validate answer quality
                                if answer and len(answer.split()) >= 3:  # Ensure answer has at least 3 words
                                    all_answers.append(answer)
                                    break
                                else:
                                    answer = None
                                    if answer_retry < max_retries - 1:
                                        print(f"Generated answer too short, retrying ({answer_retry + 1}/{max_retries})")
                                        time.sleep(retry_delay)
                                        continue
                            
                            except requests.exceptions.RequestException as e:
                                print(f"Answer generation request failed (attempt {answer_retry + 1}/{max_retries}): {str(e)}")
                                if answer_retry < max_retries - 1:
                                    time.sleep(retry_delay)
                                continue
                            except Exception as e:
                                print(f"Unexpected error in answer generation: {str(e)}")
                                break
                        
                        if not answer:  # If all retries failed
                            all_answers.append("No answer generated - Please try again later")

                    
                    # Break the retry loop if successful
                    break

                except requests.exceptions.RequestException as e:
                    last_error = e
                    print(f"Request failed (attempt {retry + 1}/{max_retries}): {str(e)}")
                    if retry < max_retries - 1:
                        time.sleep(retry_delay)
                    continue
                except Exception as e:
                    last_error = e
                    break

        # If we've exhausted all retries or encountered a non-retryable error
        if not all_questions:
            error_msg = str(last_error) if last_error else "Unknown error occurred"
            raise Exception(f"API request failed after {max_retries} attempts: {error_msg}")
        
        return all_questions, all_answers

    except Exception as e:
        raise Exception(f"Error generating questions: {str(e)}")

# Example Usage
if __name__ == "__main__":
    try:
        text = "Marie Curie was a Polish-born physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize and remains the only person to win Nobel Prizes in two different scientific fields—Physics and Chemistry. She discovered two radioactive elements, polonium and radium, along with her husband Pierre Curie. Her work laid the foundation for the development of X-rays in medicine. Marie Curie passed away in 1934 due to prolonged exposure to radiation."
        questions, answers = generate_questions(text)
        print("\nGenerated Questions and Answers:")
        for q, a in zip(questions, answers):
            print(f"\nQ: {q}")
            print(f"A: {a}")
    except Exception as e:
        print(f"Error: {str(e)}")
