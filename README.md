# EduQuery Pro

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0.1-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-GPT--2-orange)](https://huggingface.co/gpt2)

A Flask-based web application named Edu Query Pro that generates multiple-choice questions from text or PDF documents using AI.

## 🌟 Features

- 📄 Upload PDF documents or enter text directly
- 🤖 AI-powered question generation using Hugging Face models
- ✅ Interactive MCQ interface with immediate feedback
- 🏷️ Topic extraction from generated questions
- 📱 Responsive design for all devices

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/sumanthgithub7/pdf-question-generator.git
   cd pdf-question-generator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your Hugging Face API key:
   ```
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   ```

5. Run the application:
   ```bash
   cd backend
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## 💡 Usage

1. **Upload a PDF or Enter Text**:
   - Click on the "Upload PDF" button to upload a PDF document
   - Or click on the "Enter Text" button to type or paste text directly

2. **Generate Questions**:
   - Click the "Generate Questions" button
   - Wait for the AI to process your input and generate questions

3. **Answer Questions**:
   - Select your answer for each question
   - Click "Check Answer" to see if you're correct
   - Get immediate feedback and explanations

## 🔧 API Endpoints

- `POST /upload`: Upload a PDF file or submit text for question generation
- `POST /generate`: Generate questions from a text passage (JSON format)

## 🛠️ Technologies Used

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **AI**: Hugging Face Inference API with GPT-2 model
- **Styling**: Bootstrap 5, Font Awesome

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- Hugging Face for providing the AI models
- OpenAI for the GPT-2 model

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you have any questions or run into issues, please open an issue in the GitHub repository.

## 🚀 Potential Improvements

Here are some areas where the PDF Question Generator could be enhanced:

1. **Question Generation Algorithm**:
   - Improve the quality and relevance of generated questions
   - Add support for different question types (true/false, fill-in-the-blank, etc.)
   - Implement better distractor generation for multiple-choice questions

2. **Customization Options**:
   - Allow users to specify difficulty levels
   - Add topic-based question generation
   - Enable users to set the number of questions to generate

3. **User Interface Enhancements**:
   - Improve the PDF upload and text input experience
   - Add question review and editing capabilities
   - Implement a progress tracker for question generation

4. **Technical Improvements**:
   - Add support for larger PDF files
   - Implement better error handling and user feedback
   - Optimize the question generation process for faster response times

## Project Structure

```
📂 pdf-question-generator/
│── 📂 backend/                  
│   │── 📂 static/               
│   │   ├── style.css            # Styles for UI
│   │   ├── script.js            # Frontend interactivity
│   │── 📂 templates/            
│   │   ├── index.html           # PDF Upload Page
│   │   ├── result.html          # Display AI Questions
│   │── app.py                   # Flask Backend
│   │── requirements.txt          # Dependencies
│   │── .env                      # Store API Key
│── 📂 ai/                       
│   │── process_pdf.py            # Extract text from PDF
│   │── generate_questions.py     # Generate AI-based Questions
│   │── .env                      # Store API Key
│── 📂 uploads/                   
│── README.md                     
```
