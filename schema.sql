DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS appointments;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('patient', 'doctor')) NOT NULL
);

CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    doctor TEXT NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    message TEXT,
    note TEXT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

