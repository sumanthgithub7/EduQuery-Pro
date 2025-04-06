document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadForm = document.getElementById('uploadForm');
    const loadingElement = document.getElementById('loading');
    const errorElement = document.getElementById('error');
    const questionsElement = document.getElementById('questions');
    const topicTagsElement = document.getElementById('topic-tags');
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('pdfFile');
    const textInput = document.getElementById('textInput');
    const browseBtn = document.getElementById('browse-btn');
    const fileInfo = document.getElementById('fileInfo');
    const dropZoneContent = document.getElementById('dropZoneContent');
    const filename = document.getElementById('filename');
    const removeFile = document.getElementById('removeFile');
    const uploadBtn = document.getElementById('uploadBtn');
    const pdfButton = document.getElementById('pdfButton');
    const textButton = document.getElementById('textButton');
    const pdfSection = document.getElementById('pdfSection');
    const textSection = document.getElementById('textSection');
    
    let mcqs = [];  // Store MCQs globally
    let fileSelected = false;
    let currentTopics = []; // Store current topics

    // Initialize UI
    errorElement.style.display = 'none';
    loadingElement.style.display = 'none';
    updateUploadButton();

    // Input type toggle functionality
    pdfButton.addEventListener('click', function() {
        pdfButton.classList.add('active');
        textButton.classList.remove('active');
        pdfSection.style.display = 'block';
        textSection.style.display = 'none';
        textInput.value = '';
        updateUploadButton();
    });

    textButton.addEventListener('click', function() {
        textButton.classList.add('active');
        pdfButton.classList.remove('active');
        textSection.style.display = 'block';
        pdfSection.style.display = 'none';
        resetFileInput();
        updateUploadButton();
    });

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('dragover');
    }

    function unhighlight() {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0 && files[0].type === 'application/pdf') {
            handleFiles(files);
        } else {
            showError('Please upload a PDF file');
        }
    }

    // Browse button functionality
    browseBtn.addEventListener('click', function() {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            handleFiles(fileInput.files);
        }
    });

    // Remove file button functionality
    removeFile.addEventListener('click', function() {
        resetFileInput();
    });

    function handleFiles(files) {
        if (files[0].type === 'application/pdf') {
            fileSelected = true;
            dropZoneContent.style.display = 'none';
            fileInfo.style.display = 'block';
            filename.textContent = files[0].name;
            updateUploadButton();
        } else {
            showError('Please upload a PDF file');
            resetFileInput();
        }
    }

    function resetFileInput() {
        fileInput.value = '';
        fileSelected = false;
        dropZoneContent.style.display = 'block';
        fileInfo.style.display = 'none';
        updateUploadButton();
    }

    function updateUploadButton() {
        if (fileSelected || textInput.value.trim()) {
            uploadBtn.disabled = false;
        } else {
            uploadBtn.disabled = true;
        }
    }

    // Monitor text input for enabling/disabling upload button
    textInput.addEventListener('input', function() {
        updateUploadButton();
    });

    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading, hide error and questions
        loadingElement.style.display = 'block';
        errorElement.style.display = 'none';
        questionsElement.innerHTML = '';
        topicTagsElement.innerHTML = '';
        
        const formData = new FormData();
        
        // Check if file is uploaded
        if (fileInput.files.length > 0) {
            formData.append('file', fileInput.files[0]);
        }
        // Check if text is entered
        else if (textInput.value.trim()) {
            formData.append('text', textInput.value.trim());
        }
        // Show error if neither file nor text is provided
        else {
            showError('Please upload a PDF file or enter some text');
            loadingElement.style.display = 'none';
            return;
        }
        
        // Disable form elements during submission
        uploadBtn.disabled = true;
        fileInput.disabled = true;
        textInput.disabled = true;
        
        // Send request to server with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        fetch('/upload', {
            method: 'POST',
            body: formData,
            signal: controller.signal
        })
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Server error occurred');
                });
            }
            return response.json();
        })
        .then(data => {
            loadingElement.style.display = 'none';
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (!data.mcqs || data.mcqs.length === 0) {
                throw new Error('No questions could be generated. Please try with different text.');
            }
            
            // Store MCQs globally
            mcqs = data.mcqs;
            
            // Extract topics from questions
            extractTopicsFromQuestions(mcqs);
            
            // Display questions
            displayQuestions(mcqs);
            
            // Scroll to questions
            document.getElementById('questions-container').scrollIntoView({ behavior: 'smooth' });
            
            // Reset form
            if (pdfButton.classList.contains('active')) {
                resetFileInput();
            } else {
                textInput.value = '';
            }
        })
        .catch(error => {
            loadingElement.style.display = 'none';
            if (error.name === 'AbortError') {
                showError('Request timed out. Please try again.');
            } else {
                showError(error.message || 'An error occurred. Please try again.');
            }
        })
        .finally(() => {
            // Re-enable form elements
            uploadBtn.disabled = false;
            fileInput.disabled = false;
            textInput.disabled = false;
            updateUploadButton();
        });
    });

    // Extract topics from questions
    function extractTopicsFromQuestions(mcqs) {
        currentTopics = [];
        
        // Extract keywords from questions
        const keywords = new Set();
        
        // First, look for specific topic indicators in questions
        const topicIndicators = [
            'about', 'regarding', 'concerning', 'related to', 'topic of', 
            'subject of', 'field of', 'study of', 'discipline of'
        ];
        
        mcqs.forEach(mcq => {
            // Extract words from question
            const question = mcq.question.toLowerCase();
            
            // Check for topic indicators
            let foundTopic = false;
            topicIndicators.forEach(indicator => {
                if (question.includes(indicator)) {
                    const parts = question.split(indicator);
                    if (parts.length > 1) {
                        // Extract the topic after the indicator
                        const potentialTopic = parts[1].trim().split(/[.,?!]/)[0].trim();
                        if (potentialTopic && potentialTopic.length > 3) {
                            keywords.add(potentialTopic);
                            foundTopic = true;
                        }
                    }
                }
            });
            
            // If no topic indicator found, extract important words
            if (!foundTopic) {
                const words = question.split(/\s+/);
                
                // Filter out common words and short words
                words.forEach(word => {
                    if (word.length > 3 && !isCommonWord(word)) {
                        keywords.add(word);
                    }
                });
            }
            
            // Also extract from options
            mcq.options.forEach(option => {
                const optionWords = option.toLowerCase().split(/\s+/);
                optionWords.forEach(word => {
                    if (word.length > 3 && !isCommonWord(word)) {
                        keywords.add(word);
                    }
                });
            });
        });
        
        // Convert to array and limit to top 5
        currentTopics = Array.from(keywords).slice(0, 5);
        
        // If we still don't have enough topics, add some generic ones based on question content
        if (currentTopics.length < 3) {
            const genericTopics = ['General Knowledge', 'Comprehension', 'Analysis', 'Critical Thinking'];
            currentTopics = [...currentTopics, ...genericTopics.slice(0, 3 - currentTopics.length)];
        }
        
        // Display topic tags
        displayTopicTags(currentTopics);
    }
    
    // Check if word is a common word
    function isCommonWord(word) {
        const commonWords = ['what', 'when', 'where', 'who', 'why', 'how', 'which', 'that', 'this', 'with', 'from', 'have', 'they', 'their', 'there', 'about', 'would', 'could', 'should', 'will', 'your', 'some', 'such', 'than', 'then', 'them', 'these', 'those', 'into', 'over', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'];
        return commonWords.includes(word);
    }
    
    // Display topic tags
    function displayTopicTags(topics) {
        topicTagsElement.innerHTML = '';
        
        topics.forEach(topic => {
            const tag = document.createElement('span');
            tag.className = 'topic-tag';
            tag.innerHTML = `<i class="fas fa-tag"></i> ${topic}`;
            topicTagsElement.appendChild(tag);
        });
    }

    function displayQuestions(mcqs) {
        questionsElement.innerHTML = '';
        
        mcqs.forEach((mcq, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'mcq-container';
            questionDiv.id = `question-${index}`;
            
            questionDiv.innerHTML = `
                <div class="question">${mcq.question}</div>
                <div class="options">
                    ${mcq.options.map((option, i) => `
                        <div class="option" data-index="${i}">
                            <input type="radio" name="q${index}" value="${i}" id="q${index}o${i}">
                            <label for="q${index}o${i}">${option}</label>
                        </div>
                    `).join('')}
                </div>
                <button class="btn btn-primary check-answer" data-question="${index}">Check Answer</button>
                <div class="result-message" style="display: none;"></div>
            `;
            
            questionsElement.appendChild(questionDiv);
            
            // Add click handler for the entire option row with visual feedback
            const optionDivs = questionDiv.querySelectorAll('.option');
            optionDivs.forEach(optionDiv => {
                optionDiv.addEventListener('click', function(e) {
                    // Clear previous selections in this question
                    optionDivs.forEach(div => div.classList.remove('selected'));
                    // Select this option
                    const radio = this.querySelector('input[type="radio"]');
                    radio.checked = true;
                    this.classList.add('selected');
                });
            });
            
            // Add click handler for the check answer button
            const checkButton = questionDiv.querySelector('.check-answer');
            checkButton.addEventListener('click', function() {
                const selectedOption = questionDiv.querySelector('input[type="radio"]:checked');
                if (!selectedOption) {
                    showError('Please select an answer');
                    return;
                }
                checkAnswer(index, parseInt(selectedOption.value));
            });
        });
    }

    function showError(message) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    function checkAnswer(questionIndex, selectedOption) {
        const mcq = mcqs[questionIndex];
        const options = mcq.options;
        const correctAnswer = mcq.correct_answer;
        const correctIndex = options.indexOf(correctAnswer);
        
        const questionDiv = document.getElementById(`question-${questionIndex}`);
        const optionDivs = questionDiv.querySelectorAll('.option');
        const resultMessage = questionDiv.querySelector('.result-message');
        const checkButton = questionDiv.querySelector('.check-answer');
        
        // Reset previous results
        optionDivs.forEach(div => {
            div.classList.remove('correct', 'incorrect');
        });
        
        // Mark correct and incorrect answers
        optionDivs[correctIndex].classList.add('correct');
        if (selectedOption !== correctIndex) {
            optionDivs[selectedOption].classList.add('incorrect');
        }
        
        // Show result message
        resultMessage.style.display = 'block';
        if (selectedOption === correctIndex) {
            resultMessage.textContent = 'Correct! Well done!';
            resultMessage.className = 'result-message correct';
        } else {
            resultMessage.textContent = `Incorrect. The correct answer is: ${correctAnswer}`;
            resultMessage.className = 'result-message incorrect';
        }
        
        // Disable the check button
        checkButton.disabled = true;
        checkButton.textContent = 'Answered';
        
        // Scroll to the next question if available
        if (questionIndex < mcqs.length - 1) {
            setTimeout(() => {
                document.getElementById(`question-${questionIndex + 1}`).scrollIntoView({ behavior: 'smooth' });
            }, 1000);
        }
    }
});