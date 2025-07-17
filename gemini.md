 # edu-app Project Documentation

## Project Overview

The `edu-app` is a full-stack educational application designed to help teachers manage their classes, students, and subjects. It provides a web-based interface for viewing and managing educational data, as well as tools for generating educational content like quizzes using AI. The backend is built with Flask and PostgreSQL, and the frontend is a React application.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.x
- Node.js and npm
- PostgreSQL

### Backend Setup

1.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory of the project and add the necessary environment variables. You can use `config.yml.example` as a reference for the required variables, but the application uses a `.env` file for sensitive information like `DATABASE_URL`. A typical `.env` file would look like this:

    ```
    DATABASE_URL="postgresql://user:password@host:port/dbname"
    GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-credentials.json"
    # Optional:
    CLASSROOM_TEACHER_EMAIL="teacher@example.com"
    GOOGLE_AI_STUDIO_API_KEY="your-gemini-key"
    ```

3.  **Initialize the database:**
    Run the following script to create the necessary tables in your PostgreSQL database.
    ```bash
    python database/init_db.py
    ```

4.  **Run the backend server:**
    ```bash
    python backend_server.py
    ```
    The Flask server will start, typically on `http://127.0.0.1:5000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Start the frontend development server:**
    ```bash
    npm start
    ```
    The React app will open in your browser, usually at `http://localhost:3000`.

## Project Structure

The project is organized into several key directories:

-   `backend_server.py`: The main entry point for the Flask backend API.
-   `main.py`: A command-line interface for interacting with Google Classroom and Gemini.
-   `frontend/`: Contains the React frontend application.
-   `database/`: Includes scripts for database initialization (`init_db.py`), schema definition (`schema.sql`), and other database-related tasks.
-   `src/`: Contains Python source code. *Note: There seems to be a duplication of files in the root directory and the `src` directory. This might need to be cleaned up.*
-   `data/`: Stores data files like `lesson_plan.json` and `quiz.json`.
-   `config/`: Contains configuration files, such as Supabase client setup.
-   `requirements.txt`: Lists the Python dependencies for the backend.
-   `frontend/package.json`: Lists the Node.js dependencies for the frontend.

## Configuration

Application configuration is primarily handled through environment variables. The backend server (`backend_server.py`) and other scripts load these variables using `python-dotenv`.

-   `DATABASE_URL`: The connection string for the PostgreSQL database.
-   `GOOGLE_APPLICATION_CREDENTIALS`: Path to the Google Cloud service account JSON file for authentication.
-   `CLASSROOM_TEACHER_EMAIL`: (Optional) The teacher's email for domain-wide delegation with Google Classroom.
-   `GOOGLE_AI_STUDIO_API_KEY`: (Optional) Your API key for Google's Generative AI services (Gemini).

Refer to `config.yml.example` for a sample structure, but use a `.env` file for actual configuration.

## Database Schema
 
 The `edu-app` project utilizes a PostgreSQL database to manage information about teachers, students, classes, subjects, and their relationships. The schema is defined in `database/schema.sql` and includes the following tables:
 
 ### `teachers`
 Stores information about teachers.
 
 *   `teacher_id` (SERIAL PRIMARY KEY): Unique identifier for each teacher.
 *   `first_name` (VARCHAR(100) NOT NULL): First name of the teacher.
 *   `last_name` (VARCHAR(100) NOT NULL): Last name of the teacher.
 *   `email` (VARCHAR(255) UNIQUE NOT NULL): Email address of the teacher (must be unique).
 *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the teacher record was created.
 *   `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the teacher record was last updated.
 
 ### `students`
 Stores information about students.
 
 *   `student_id` (SERIAL PRIMARY KEY): Unique identifier for each student.
 *   `first_name` (VARCHAR(100) NOT NULL): First name of the student.
 *   `last_name` (VARCHAR(100) NOT NULL): Last name of the student.
 *   `email` (VARCHAR(255) UNIQUE NOT NULL): Email address of the student (must be unique).
 *   `date_of_birth` (DATE): Date of birth of the student.
 *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the student record was created.
 *   `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the student record was last updated.
 
 ### `classes`
 Stores information about classes.
 
 *   `class_id` (SERIAL PRIMARY KEY): Unique identifier for each class.
 *   `class_name` (VARCHAR(100) NOT NULL): Name of the class.
 *   `academic_year` (VARCHAR(20) NOT NULL): Academic year the class belongs to.
 *   `semester` (VARCHAR(20) NOT NULL): Semester the class is offered in.
 *   `description` (TEXT): Description of the class.
 *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the class record was created.
 *   `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the class record was last updated.
 
 ### `subjects`
 Stores information about subjects.
 
 *   `subject_id` (SERIAL PRIMARY KEY): Unique identifier for each subject.
 *   `subject_name` (VARCHAR(100) NOT NULL): Name of the subject.
 *   `subject_code` (VARCHAR(20)): Code for the subject.
 *   `description` (TEXT): Description of the subject.
 *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the subject record was created.
 *   `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the subject record was last updated.
 
 ### `student_class`
 Represents the relationship between students and classes (enrollment).
 
 *   `student_id` (INTEGER NOT NULL): Foreign key referencing `students(student_id)`.
 *   `class_id` (INTEGER NOT NULL): Foreign key referencing `classes(class_id)`.
 *   `enrollment_date` (DATE NOT NULL): Date when the student enrolled in the class.
 *   `status` (VARCHAR(20) DEFAULT 'active'): Enrollment status (e.g., 'active', 'inactive').
 *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the enrollment record was created.
 *   `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the enrollment record was last updated.
 *   PRIMARY KEY (`student_id`, `class_id`): Composite primary key.
 *   FOREIGN KEY (`student_id`) REFERENCES `students(student_id)` ON DELETE CASCADE: Ensures referential integrity.
 *   FOREIGN KEY (`class_id`) REFERENCES `classes(class_id)` ON DELETE CASCADE: Ensures referential integrity.
 
 ### `teacher_subject_class`
 Represents the relationship between teachers, subjects, and classes (teaching assignments).
 
 *   `teacher_id` (INTEGER NOT NULL): Foreign key referencing `teachers(teacher_id)`.
 *   `subject_id` (INTEGER NOT NULL): Foreign key referencing `subjects(subject_id)`.
 *   `class_id` (INTEGER NOT NULL): Foreign key referencing `classes(class_id)`.
 *   `academic_year` (VARCHAR(20) NOT NULL): Academic year of the teaching assignment.
 *   `semester` (VARCHAR(20) NOT NULL): Semester of the teaching assignment.
 *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the assignment record was created.
 *   `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the assignment record was last updated.
 *   PRIMARY KEY (`teacher_id`, `subject_id`, `class_id`, `academic_year`, `semester`): Composite primary key.
 *   FOREIGN KEY (`teacher_id`) REFERENCES `teachers(teacher_id)` ON DELETE CASCADE: Ensures referential integrity.
 *   FOREIGN KEY (`subject_id`) REFERENCES `subjects(subject_id)` ON DELETE CASCADE: Ensures referential integrity.
 *   FOREIGN KEY (`class_id`) REFERENCES `classes(class_id)` ON DELETE CASCADE: Ensures referential integrity.
 
 ### `student_subject_performance`
 Stores student performance data in subjects.
 
 *   `student_id` (INTEGER NOT NULL): Foreign key referencing `students(student_id)`.
 *   `subject_id` (INTEGER NOT NULL): Foreign key referencing `subjects(subject_id)`.
 *   `class_id` (INTEGER NOT NULL): Foreign key referencing `classes(class_id)`.
 *   `academic_year` (VARCHAR(20) NOT NULL): Academic year of the performance record.
 *   `semester` (VARCHAR(20) NOT NULL): Semester of the performance record.
 *   `score` (NUMERIC(5,2)): Student's score in the subject.
 *   `grade` (VARCHAR(5)): Student's grade in the subject.
 *   `attendance` (INTEGER): Student's attendance in the subject.
 *   `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the performance record was created.
 *   `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp of when the performance record was last updated.
 *   PRIMARY KEY (`student_id`, `subject_id`, `class_id`, `academic_year`, `semester`): Composite primary key.
 *   FOREIGN KEY (`student_id`) REFERENCES `students(student_id)` ON DELETE CASCADE: Ensures referential integrity.
 *   FOREIGN KEY (`subject_id`) REFERENCES `subjects(subject_id)` ON DELETE CASCADE: Ensures referential integrity.
 *   FOREIGN KEY (`class_id`) REFERENCES `classes(class_id)` ON DELETE CASCADE: Ensures referential integrity.
 
 ### Triggers
 
 The schema includes triggers to automatically update the `updated_at` column in each table whenever a row is modified. This is achieved using a function `update_modified_column()` that sets the `updated_at` column to the current timestamp.