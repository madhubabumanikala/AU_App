-- AU Event Information System Database Setup
-- MySQL Database Schema

-- Create database
CREATE DATABASE IF NOT EXISTS au_event_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE au_event_system;

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    phone_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_student_id (student_id),
    INDEX idx_email (email),
    INDEX idx_department (department)
);

-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    max_participants INT,
    poster_image VARCHAR(255),
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES admins(id) ON DELETE CASCADE,
    INDEX idx_date (date),
    INDEX idx_department (department),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active)
);

-- Event registrations table
CREATE TABLE IF NOT EXISTS event_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    event_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attendance_status BOOLEAN DEFAULT FALSE,
    qr_code_path VARCHAR(255),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_event_registration (student_id, event_id),
    INDEX idx_student_id (student_id),
    INDEX idx_event_id (event_id)
);

-- Event feedbacks table
CREATE TABLE IF NOT EXISTS event_feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    event_id INT NOT NULL,
    rating INT,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_event_feedback (student_id, event_id),
    INDEX idx_student_id (student_id),
    INDEX idx_event_id (event_id)
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_student_id (student_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);

-- Insert default admin user (password: admin123)
INSERT INTO admins (username, first_name, last_name, email, password_hash, role, department) 
VALUES ('admin', 'System', 'Administrator', 'admin@au-events.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflHQrxG', 'super_admin', 'Administration')
ON DUPLICATE KEY UPDATE id=id;

-- Insert sample departments for testing
INSERT IGNORE INTO events (title, description, date, time, location, department, category, max_participants, created_by) VALUES
('Python Workshop', 'Learn Python programming basics and advanced concepts', '2024-03-15', '10:00:00', 'Computer Lab 1', 'Computer Science', 'workshop', 50, 1),
('Cultural Fest', 'Annual cultural festival with music, dance, and drama', '2024-03-20', '18:00:00', 'Auditorium', 'All Departments', 'cultural', 500, 1),
('Placement Drive', 'Campus recruitment drive by top companies', '2024-03-25', '09:00:00', 'Placement Cell', 'All Departments', 'placement', 200, 1),
('Technical Seminar', 'Latest trends in Artificial Intelligence', '2024-03-18', '14:00:00', 'Seminar Hall', 'Computer Science', 'seminar', 100, 1),
('Sports Meet', 'Annual sports competition', '2024-03-22', '08:00:00', 'Sports Ground', 'All Departments', 'sports', 300, 1);

-- Insert sample students for testing
INSERT IGNORE INTO students (student_id, first_name, last_name, email, password_hash, department, year, phone_number) VALUES
('AU20240001CS001', 'Rahul', 'Kumar', 'rahul.cs001@andhrauniversity.edu.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflHQrxG', 'Computer Science', 3, '+919876543210'),
('AU20240002EC001', 'Priya', 'Sharma', 'priya.ec001@andhrauniversity.edu.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflHQrxG', 'Electronics & Communication', 2, '+919876543211'),
('AU20240003ME001', 'Amit', 'Singh', 'amit.me001@andhrauniversity.edu.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflHQrxG', 'Mechanical Engineering', 4, '+919876543212'),
('AU20240004CE001', 'Sneha', 'Reddy', 'sneha.ce001@andhrauniversity.edu.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflHQrxG', 'Civil Engineering', 1, '+919876543213'),
('AU20240005EE001', 'Karthik', 'Rao', 'karthik.ee001@andhrauniversity.edu.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflHQrxG', 'Electrical Engineering', 3, '+919876543214');

-- Create views for common queries
CREATE OR REPLACE VIEW event_statistics AS
SELECT 
    e.id,
    e.title,
    e.date,
    e.department,
    e.category,
    COUNT(er.id) as registered_count,
    e.max_participants,
    ROUND(AVG(ef.rating), 2) as average_rating,
    COUNT(CASE WHEN ef.rating IS NOT NULL THEN 1 END) as feedback_count
FROM events e
LEFT JOIN event_registrations er ON e.id = er.event_id
LEFT JOIN event_feedbacks ef ON e.id = ef.event_id
WHERE e.is_active = TRUE
GROUP BY e.id, e.title, e.date, e.department, e.category, e.max_participants;

CREATE OR REPLACE VIEW student_activity AS
SELECT 
    s.id,
    s.student_id,
    s.first_name,
    s.last_name,
    s.department,
    s.year,
    COUNT(er.id) as events_registered,
    COUNT(CASE WHEN er.attendance_status = TRUE THEN 1 END) as events_attended,
    COUNT(ef.id) as feedbacks_given
FROM students s
LEFT JOIN event_registrations er ON s.id = er.student_id
LEFT JOIN event_feedbacks ef ON s.id = ef.student_id
GROUP BY s.id, s.student_id, s.first_name, s.last_name, s.department, s.year;

-- Create stored procedures for common operations
DELIMITER //

CREATE PROCEDURE GetUpcomingEvents(IN department_filter VARCHAR(100))
BEGIN
    SELECT e.*, 
           COUNT(er.id) as registered_count,
           a.first_name as creator_name
    FROM events e
    LEFT JOIN event_registrations er ON e.id = er.event_id
    LEFT JOIN admins a ON e.created_by = a.id
    WHERE e.date >= CURDATE() 
    AND e.is_active = TRUE
    AND (department_filter IS NULL OR e.department = department_filter)
    GROUP BY e.id
    ORDER BY e.date, e.time;
END //

CREATE PROCEDURE GetStudentNotifications(IN student_id_param INT)
BEGIN
    SELECT n.*, s.first_name, s.last_name
    FROM notifications n
    JOIN students s ON n.student_id = s.id
    WHERE n.student_id = student_id_param
    ORDER BY n.created_at DESC;
END //

CREATE PROCEDURE MarkEventAttendance(IN registration_id_param INT, IN attendance_status_param BOOLEAN)
BEGIN
    UPDATE event_registrations 
    SET attendance_status = attendance_status_param 
    WHERE id = registration_id_param;
    
    SELECT ROW_COUNT() as rows_affected;
END //

DELIMITER ;

-- Create triggers for data integrity
DELIMITER //

CREATE TRIGGER before_event_update 
BEFORE UPDATE ON events
FOR EACH ROW
BEGIN
    IF NEW.date < CURDATE() THEN
        SET NEW.is_active = FALSE;
    END IF;
END //

CREATE TRIGGER after_event_registration
AFTER INSERT ON event_registrations
FOR EACH ROW
BEGIN
    -- Create notification for student
    INSERT INTO notifications (student_id, title, message, type)
    VALUES (
        NEW.student_id,
        'Event Registration Confirmed',
        CONCAT('You have successfully registered for ', (SELECT title FROM events WHERE id = NEW.event_id)),
        'success'
    );
END //

DELIMITER ;

-- Create indexes for performance optimization
CREATE INDEX idx_events_date_category ON events(date, category);
CREATE INDEX idx_registrations_student_event ON event_registrations(student_id, event_id);
CREATE INDEX idx_notifications_student_unread ON notifications(student_id, is_read);

-- Set up foreign key constraints
ALTER TABLE event_registrations 
ADD CONSTRAINT fk_registrations_student 
FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

ALTER TABLE event_registrations 
ADD CONSTRAINT fk_registrations_event 
FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE;

ALTER TABLE event_feedbacks 
ADD CONSTRAINT fk_feedbacks_student 
FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

ALTER TABLE event_feedbacks 
ADD CONSTRAINT fk_feedbacks_event 
FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE;

ALTER TABLE notifications 
ADD CONSTRAINT fk_notifications_student 
FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

ALTER TABLE events 
ADD CONSTRAINT fk_events_creator 
FOREIGN KEY (created_by) REFERENCES admins(id) ON DELETE CASCADE;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON au_event_system.* TO 'au_events_user'@'localhost' IDENTIFIED BY 'your_password';
-- FLUSH PRIVILEGES;
