# EduGenie – Google Gemini Powered Learning Assistant

EduGenie is a lightweight AI-powered educational assistant designed to help students learn more effectively using Generative AI.

It provides multiple learning features through a simple web interface:

- Ask questions and receive AI-generated answers
- Get simplified explanations of complex concepts
- Generate multiple-choice quizzes
- Summarize educational content
- Get personalized learning recommendations

## Features

### 1. Question & Answer
Students can enter a question and receive a clear, student-friendly answer powered by Google Gemini.

### 2. Concept Explanation
EduGenie explains difficult technical concepts using simple language, structured points, examples, and a short recap.

### 3. Quiz Generation
Students can provide educational text and generate multiple-choice questions.

Each quiz contains:
- Question
- 4 options
- Correct answer
- Short explanation

### 4. Summarization
EduGenie converts long educational passages into concise revision-friendly summaries while retaining important concepts.

### 5. Learning Recommendations
Students can enter a topic, current learning level, and learning goal to receive a structured learning path.

---

## Technology Stack

### Backend
- Python
- FastAPI
- Uvicorn
- Pydantic

### AI
- Google Gemini API
- Gemini 3.8 Flash
- Google GenAI Python SDK

### Frontend
- HTML
- CSS
- JavaScript
- Jinja2 Templates

### Testing
- Pytest
- FastAPI TestClient

---

## Project Architecture

```text
EduGenie-AI/
│
├── main.py
├── ai_client.py
├── config.py
├── prompts.py
├── qna.py
├── explanation_module.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── tests/
│
├── requirements.txt
├── requirements-local.txt
├── .gitignore
└── README.md

Prerequisites

Before running EduGenie, make sure the following are installed:

Python 3.10 or later
Git
A Google Gemini API key
Installation
Step 1: Clone the Repository

Open a terminal or PowerShell and run:

git clone https://github.com/veronica-sivakumar/EduGenie-AI.git

Then move into the project folder:

cd EduGenie-AI
Step 2: Create a Virtual Environment

Create a Python virtual environment:

python -m venv .venv
Step 3: Activate the Virtual Environment
Windows PowerShell
.venv\Scripts\Activate.ps1
Windows Command Prompt
.venv\Scripts\activate

After activation, the terminal should show:

(.venv)
Step 4: Install Required Dependencies

Install all required Python packages using:

python -m pip install -r requirements.txt
Gemini API Configuration

EduGenie uses Google Gemini for AI-powered features.

Create a file named:

.env

in the project root directory.

Add the following configuration:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.8-flash

Replace YOUR_GEMINI_API_KEY with your own Gemini API key.

Never share your Gemini API key publicly or upload the .env file to GitHub.

The .env file is excluded from Git using .gitignore.

Running the Application

After completing the installation and configuration, start the FastAPI server using:

uvicorn main:app --reload

If the server starts successfully, you will see a message similar to:

Uvicorn running on http://127.0.0.1:8000

Open the following address in a web browser:

http://127.0.0.1:8000

The EduGenie web interface will then be available.