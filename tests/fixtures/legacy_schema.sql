-- Schema exported from the unmodified uploaded models.py; no personal data.
BEGIN TRANSACTION;
CREATE TABLE attendance (
	id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	status VARCHAR(7), 
	score_1 FLOAT, 
	score_2 FLOAT, 
	lesson_topic TEXT, 
	homework TEXT, 
	recorded_by INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES groups (id), 
	FOREIGN KEY(student_id) REFERENCES students (id), 
	FOREIGN KEY(recorded_by) REFERENCES users (id)
);
CREATE TABLE audit_logs (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	user_name VARCHAR(200), 
	action VARCHAR(20) NOT NULL, 
	entity VARCHAR(50) NOT NULL, 
	entity_id INTEGER, 
	summary VARCHAR(400), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE cancelled_lessons (
	id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	reason TEXT, 
	cancelled_by INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES groups (id), 
	FOREIGN KEY(cancelled_by) REFERENCES users (id)
);
CREATE TABLE characteristics (
	id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	author_id INTEGER, 
	author_name VARCHAR(200), 
	period VARCHAR(7) NOT NULL, 
	text TEXT NOT NULL, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id), 
	FOREIGN KEY(author_id) REFERENCES users (id)
);
CREATE TABLE classrooms (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	capacity INTEGER, 
	branch VARCHAR(100), 
	floor INTEGER, 
	is_active BOOLEAN, 
	PRIMARY KEY (id)
);
CREATE TABLE enrollment_forms (
	id INTEGER NOT NULL, 
	manager_id INTEGER, 
	student_name VARCHAR(200) NOT NULL, 
	grade INTEGER, 
	language VARCHAR(3), 
	student_phone VARCHAR(20), 
	parent_name VARCHAR(200), 
	parent_phone VARCHAR(20), 
	branch VARCHAR(100), 
	start_date DATE, 
	payment VARCHAR(100), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(manager_id) REFERENCES users (id)
);
CREATE TABLE ent_student_results (
	id INTEGER NOT NULL, 
	test_id INTEGER, 
	student_name VARCHAR, 
	student_phone VARCHAR, 
	grade INTEGER, 
	language VARCHAR, 
	subject1 VARCHAR, 
	subject2 VARCHAR, 
	answers TEXT, 
	scores TEXT, 
	total_score INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(test_id) REFERENCES ent_tests (id)
);
CREATE TABLE ent_tests (
	id INTEGER NOT NULL, 
	name VARCHAR(300) NOT NULL, 
	status VARCHAR(8), 
	progress INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	correct_answers TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE fines (
	id INTEGER NOT NULL, 
	teacher_id INTEGER NOT NULL, 
	amount INTEGER NOT NULL, 
	reason TEXT, 
	issued_by INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(teacher_id) REFERENCES users (id), 
	FOREIGN KEY(issued_by) REFERENCES users (id)
);
CREATE TABLE forbidden_dates (
	id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	added_by INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	UNIQUE (date), 
	FOREIGN KEY(added_by) REFERENCES users (id)
);
CREATE TABLE freezes (
	id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	start_date DATE NOT NULL, 
	end_date DATE NOT NULL, 
	reason TEXT, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id)
);
CREATE TABLE group_students (
	id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES groups (id), 
	FOREIGN KEY(student_id) REFERENCES students (id)
);
CREATE TABLE groups (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	subject VARCHAR(150), 
	grade INTEGER, 
	language VARCHAR(3), 
	teacher_id INTEGER, 
	classroom_id INTEGER, 
	capacity INTEGER, 
	status VARCHAR(8), 
	branch VARCHAR(100), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(teacher_id) REFERENCES users (id), 
	FOREIGN KEY(classroom_id) REFERENCES classrooms (id)
);
CREATE TABLE mentor_assignments (
	id INTEGER NOT NULL, 
	mentor_id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(mentor_id) REFERENCES users (id), 
	UNIQUE (student_id), 
	FOREIGN KEY(student_id) REFERENCES students (id)
);
CREATE TABLE payments (
	id INTEGER NOT NULL, 
	student_id INTEGER NOT NULL, 
	start_date DATE NOT NULL, 
	months INTEGER NOT NULL, 
	gift_months INTEGER NOT NULL, 
	amount INTEGER, 
	paid_until DATE NOT NULL, 
	note TEXT, 
	created_by INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);
CREATE TABLE returns (
	id INTEGER NOT NULL, 
	student_id INTEGER, 
	student_name VARCHAR(200) NOT NULL, 
	parent_name VARCHAR(200), 
	parent_phone VARCHAR(20), 
	language VARCHAR(3), 
	reason TEXT, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(student_id) REFERENCES students (id)
);
CREATE TABLE schedule_slots (
	id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	day_of_week VARCHAR(3) NOT NULL, 
	start_time TIME NOT NULL, 
	end_time TIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES groups (id)
);
CREATE TABLE students (
	id INTEGER NOT NULL, 
	full_name VARCHAR(200) NOT NULL, 
	grade INTEGER NOT NULL, 
	language VARCHAR(3) NOT NULL, 
	phone VARCHAR(20), 
	parent_name VARCHAR(200), 
	parent_phone VARCHAR(20), 
	branch VARCHAR(100), 
	status VARCHAR(8), 
	paid_until DATE, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
);
CREATE TABLE tasks (
	id INTEGER NOT NULL, 
	title VARCHAR(300) NOT NULL, 
	description TEXT, 
	assigned_to INTEGER, 
	created_by INTEGER NOT NULL, 
	status VARCHAR(11), 
	due_date DATE, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(assigned_to) REFERENCES users (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);
CREATE TABLE teacher_substitutions (
	id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	substitute_teacher_id INTEGER NOT NULL, 
	reason TEXT, 
	created_by INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES groups (id), 
	FOREIGN KEY(substitute_teacher_id) REFERENCES users (id), 
	FOREIGN KEY(created_by) REFERENCES users (id)
);
CREATE TABLE transferred_lessons (
	id INTEGER NOT NULL, 
	group_id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	new_date DATE NOT NULL, 
	reason TEXT, 
	transferred_by INTEGER, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id), 
	FOREIGN KEY(group_id) REFERENCES groups (id), 
	FOREIGN KEY(transferred_by) REFERENCES users (id)
);
CREATE TABLE users (
	id INTEGER NOT NULL, 
	iin VARCHAR(12) NOT NULL, 
	hashed_password VARCHAR NOT NULL, 
	full_name VARCHAR(200) NOT NULL, 
	initials VARCHAR(10), 
	role VARCHAR(8) NOT NULL, 
	phone VARCHAR(20), 
	subject VARCHAR(100), 
	hourly_rate INTEGER, 
	branch VARCHAR(100), 
	is_active BOOLEAN, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_users_id ON users (id);
CREATE UNIQUE INDEX ix_users_iin ON users (iin);
CREATE INDEX ix_students_id ON students (id);
CREATE INDEX ix_classrooms_id ON classrooms (id);
CREATE INDEX ix_ent_tests_id ON ent_tests (id);
CREATE INDEX ix_groups_id ON groups (id);
CREATE INDEX ix_mentor_assignments_id ON mentor_assignments (id);
CREATE INDEX ix_tasks_id ON tasks (id);
CREATE INDEX ix_ent_student_results_id ON ent_student_results (id);
CREATE INDEX ix_returns_id ON returns (id);
CREATE INDEX ix_enrollment_forms_id ON enrollment_forms (id);
CREATE INDEX ix_forbidden_dates_id ON forbidden_dates (id);
CREATE INDEX ix_payments_student_id ON payments (student_id);
CREATE INDEX ix_payments_id ON payments (id);
CREATE INDEX ix_freezes_id ON freezes (id);
CREATE INDEX ix_freezes_student_id ON freezes (student_id);
CREATE INDEX ix_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX ix_audit_logs_created_at ON audit_logs (created_at);
CREATE INDEX ix_audit_logs_id ON audit_logs (id);
CREATE INDEX ix_characteristics_period ON characteristics (period);
CREATE INDEX ix_characteristics_id ON characteristics (id);
CREATE INDEX ix_characteristics_student_id ON characteristics (student_id);
CREATE INDEX ix_fines_teacher_id ON fines (teacher_id);
CREATE INDEX ix_fines_id ON fines (id);
CREATE INDEX ix_group_students_id ON group_students (id);
CREATE INDEX ix_schedule_slots_id ON schedule_slots (id);
CREATE INDEX ix_attendance_id ON attendance (id);
CREATE INDEX ix_cancelled_lessons_id ON cancelled_lessons (id);
CREATE INDEX ix_cancelled_lessons_group_id ON cancelled_lessons (group_id);
CREATE INDEX ix_cancelled_lessons_date ON cancelled_lessons (date);
CREATE INDEX ix_teacher_substitutions_date ON teacher_substitutions (date);
CREATE INDEX ix_teacher_substitutions_id ON teacher_substitutions (id);
CREATE INDEX ix_teacher_substitutions_group_id ON teacher_substitutions (group_id);
CREATE INDEX ix_transferred_lessons_date ON transferred_lessons (date);
CREATE INDEX ix_transferred_lessons_new_date ON transferred_lessons (new_date);
CREATE INDEX ix_transferred_lessons_id ON transferred_lessons (id);
CREATE INDEX ix_transferred_lessons_group_id ON transferred_lessons (group_id);
COMMIT;
