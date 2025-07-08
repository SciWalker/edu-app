-- Sample data for edu-app database
-- Created on 2025-06-04

-- Insert 2 Teachers
INSERT INTO teachers (first_name, last_name, email) VALUES
('John', 'Smith', 'john.smith@school.edu'),
('Sarah', 'Johnson', 'sarah.johnson@school.edu');

-- Insert 5 Students
INSERT INTO students (first_name, last_name, email, date_of_birth) VALUES
('Emma', 'Davis', 'emma.davis@student.edu', '2007-05-15'),
('Michael', 'Wilson', 'michael.wilson@student.edu', '2006-11-23'),
('Sophia', 'Brown', 'sophia.brown@student.edu', '2007-03-08'),
('James', 'Taylor', 'james.taylor@student.edu', '2006-09-17'),
('Olivia', 'Anderson', 'olivia.anderson@student.edu', '2007-07-30');

-- Insert 2 Classes
INSERT INTO classes (class_name, academic_year, semester, description) VALUES
('Class 10A', '2025-2026', 'Fall', 'Advanced science track for 10th grade students'),
('Class 11B', '2025-2026', 'Fall', 'Standard science track for 11th grade students');

-- Insert 3 Subjects
INSERT INTO subjects (subject_name, subject_code, description) VALUES
('Biology', 'BIO101', 'Introduction to biological concepts and systems'),
('Physics', 'PHY101', 'Fundamentals of physics and mechanics'),
('Chemistry', 'CHEM101', 'Basic principles of chemistry and molecular structures');

-- Enroll Students in Classes (student_class relationship)
INSERT INTO student_class (student_id, class_id, enrollment_date, status)
SELECT s.student_id, c.class_id, e.enrollment_date::date, e.status
FROM (VALUES
    ('emma.davis@student.edu', 'Class 10A', '2025-08-15'::date, 'active'),
    ('michael.wilson@student.edu', 'Class 10A', '2025-08-15'::date, 'active'),
    ('sophia.brown@student.edu', 'Class 10A', '2025-08-16'::date, 'active'),
    ('james.taylor@student.edu', 'Class 11B', '2025-08-14'::date, 'active'),
    ('olivia.anderson@student.edu', 'Class 11B', '2025-08-17'::date, 'active')
) AS e(email, class_name, enrollment_date, status)
JOIN students s ON s.email = e.email
JOIN classes c ON c.class_name = e.class_name;

-- Assign Teachers to Subjects and Classes (teacher_subject_class relationship)
INSERT INTO teacher_subject_class (teacher_id, subject_id, class_id, academic_year, semester)
SELECT t.teacher_id, s.subject_id, c.class_id, a.academic_year, a.semester
FROM (VALUES
    ('john.smith@school.edu', 'Biology', 'Class 10A', '2025-2026', 'Fall'),
    ('john.smith@school.edu', 'Chemistry', 'Class 10A', '2025-2026', 'Fall'),
    ('sarah.johnson@school.edu', 'Physics', 'Class 10A', '2025-2026', 'Fall'),
    ('sarah.johnson@school.edu', 'Biology', 'Class 11B', '2025-2026', 'Fall'),
    ('sarah.johnson@school.edu', 'Physics', 'Class 11B', '2025-2026', 'Fall'),
    ('sarah.johnson@school.edu', 'Chemistry', 'Class 11B', '2025-2026', 'Fall')
) AS a(teacher_email, subject_name, class_name, academic_year, semester)
JOIN teachers t ON t.email = a.teacher_email
JOIN subjects s ON s.subject_name = a.subject_name
JOIN classes c ON c.class_name = a.class_name;

-- Record some initial student performance data
INSERT INTO student_subject_performance (student_id, subject_id, class_id, academic_year, semester, score, grade, attendance)
SELECT s.student_id, subj.subject_id, c.class_id, p.academic_year, p.semester, p.score, p.grade, p.attendance
FROM (VALUES
    -- Emma's performance
    ('emma.davis@student.edu', 'Biology', 'Class 10A', '2025-2026', 'Fall', 92.5, 'A', 100),
    ('emma.davis@student.edu', 'Physics', 'Class 10A', '2025-2026', 'Fall', 85.0, 'B', 95),
    ('emma.davis@student.edu', 'Chemistry', 'Class 10A', '2025-2026', 'Fall', 88.5, 'B+', 98),
    
    -- Michael's performance
    ('michael.wilson@student.edu', 'Biology', 'Class 10A', '2025-2026', 'Fall', 78.0, 'C+', 90),
    ('michael.wilson@student.edu', 'Physics', 'Class 10A', '2025-2026', 'Fall', 95.0, 'A', 100),
    ('michael.wilson@student.edu', 'Chemistry', 'Class 10A', '2025-2026', 'Fall', 82.5, 'B', 93),
    
    -- James's performance
    ('james.taylor@student.edu', 'Biology', 'Class 11B', '2025-2026', 'Fall', 91.0, 'A-', 97),
    ('james.taylor@student.edu', 'Physics', 'Class 11B', '2025-2026', 'Fall', 89.5, 'B+', 96),
    ('james.taylor@student.edu', 'Chemistry', 'Class 11B', '2025-2026', 'Fall', 94.0, 'A', 100)
) AS p(student_email, subject_name, class_name, academic_year, semester, score, grade, attendance)
JOIN students s ON s.email = p.student_email
JOIN subjects subj ON subj.subject_name = p.subject_name
JOIN classes c ON c.class_name = p.class_name;
