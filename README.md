# SciWalker Educational Application

An educational web application that integrates with Google Classroom API and uses LLM technology to generate quizzes based on lesson plans.

## Features

- **Lesson Plan Management**: Create and edit lesson plans with customizable fields
- **AI-Powered Quiz Generation**: Generate quizzes automatically using Google's Gemini API
- **Quiz Editing**: View and edit generated quizzes with a user-friendly interface
- **Google Classroom Integration**: List and view your Google Classroom classes

## Project Structure

```
edu-app/
├── backend_server.py     # Flask backend server with API endpoints
├── classroom_handler.py  # Google Classroom API integration
├── generate_quiz.py      # LLM-based quiz generation script
├── gemini_handler.py     # Google Gemini API integration
├── config.yml           # Configuration file for API keys
├── data/                # Data storage
│   ├── lesson_plan.json # Lesson plan data
│   └── quiz.json        # Generated quiz data
└── frontend/            # React frontend
    ├── public/          # Static assets
    └── src/             # React components
        ├── App.js       # Main application with tab navigation
        ├── LessonPlanTab.js    # Lesson plan management
        ├── QuizTab.js          # Quiz display and editing
        └── GoogleClassroomTab.js # Google Classroom integration
```

## Setup and Installation

### Prerequisites

- Python 3.7+
- Node.js and npm
- Google Classroom API credentials
- Google Gemini API key

### Backend Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure API keys:
   - Copy `config.yml.example` to `config.yml`
   - Add your Google Gemini API key and Google Classroom credentials

3. Start the backend server:
   ```bash
   python backend_server.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open your browser to [http://localhost:3000](http://localhost:3000)

## Usage

### Lesson Plan Tab

1. Edit the lesson plan fields (topic, number of questions, etc.)
2. Click "Save" to save changes
3. Click "Generate Quiz" to create a quiz based on the lesson plan

### Quiz Tab

1. View the generated quiz with questions and answer options
2. Edit questions, options, and correct answers as needed
3. Click "Save" to save changes

### Google Classroom Tab

1. Click "List Classes" to fetch your Google Classroom classes
2. View class details and click "Open in Classroom" to navigate to Google Classroom

## API Endpoints

- `GET /api/lesson-plan`: Retrieve the current lesson plan
- `POST /api/lesson-plan`: Update the lesson plan
- `GET /api/quiz`: Retrieve the current quiz
- `POST /api/quiz`: Update the quiz
- `POST /api/generate-quiz`: Generate a new quiz using LLM
- `GET /api/google-classroom-classes`: List Google Classroom classes

## Technologies Used

- **Backend**: Python, Flask, Google API Client
- **Frontend**: React, JavaScript
- **AI/ML**: Google Gemini API
- **Authentication**: Google OAuth 2.0
- **Data Storage**: JSON files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Classroom API
- Google Gemini API
- React and Flask communities
