CREATE TYPE user_role As ENUM('USER', 'ADMIN');
CREATE TYPE authentication_method As ENUM('EMAIL', 'PHONE_NUMBER');

CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(100) NOT NULL,
    user_role user_role NOT NULL DEFAULT 'USER',
    name VARCHAR(100),
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(15) UNIQUE,
    city VARCHAR(20),
    date_of_sign_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_picture BYTEA,
    authentication_method authentication_method NOT NULL DEFAULT 'EMAIL'
);

CREATE TYPE vehicle_type As ENUM('BUS', 'TRAIN', 'FLIGHT');

CREATE TABLE vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    facility JSONB,
    vehicle_type vehicle_type NOT NULL
);

CREATE TABLE flights (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    airline_name VARCHAR(100) NOT NULL,
    flight_class VARCHAR(50) NOT NULL,
    number_of_stop INTEGER CHECK (number_of_stop >= 0),
    flight_code VARCHAR(50) NOT NULL,
    origin_airport VARCHAR(100) NOT NULL,
    destination_airport VARCHAR(100) NOT NULL
);

CREATE TABLE trains (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    train_stars INTEGER CHECK (train_stars > 0 AND train_stars < 6) NOT NULL,
    choosing_a_closed_coupe BOOLEAN
);

CREATE TABLE buses (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    company_name VARCHAR(100)  NOT NULL,
    bus_type VARCHAR(50)  NOT NULL,
    number_of_chairs INTEGER CHECK (number_of_chairs > 0)
);

CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id) ON UPDATE CASCADE,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    date_and_time_of_departure TIMESTAMP NOT NULL,
    date_and_time_of_arrival TIMESTAMP NOT NULL,
    price INTEGER CHECK (price > 0),
    remaining_capacity INTEGER CHECK (remaining_capacity >= 0)
);

CREATE TYPE reservation_status As ENUM('RESERVED', 'NOT_RESERVED');

CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    username VARCHAR(50) REFERENCES users(username) ON UPDATE CASCADE ON DELETE CASCADE,
    ticket_id INTEGER REFERENCES tickets(ticket_id) ON UPDATE CASCADE ON DELETE CASCADE,
    reservation_status reservation_status NOT NULL DEFAULT 'NOT_RESERVED',
    date_and_time_of_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reservation_seat INTEGER CHECK (reservation_seat > 0) NOT NULL
);

CREATE TYPE payment_status As ENUM('PAID', 'NOT_PAID');
CREATE TYPE payment_method As ENUM('CRYPTOCURRENCY', 'WALLET', 'CREDIT_CARD');

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    username VARCHAR(50) REFERENCES users(username) ON UPDATE CASCADE ON DELETE CASCADE,
    reservation_id INTEGER REFERENCES reservations(reservation_id) ON UPDATE CASCADE,
    amount_paid INTEGER CHECK (amount_paid > 0),
    payment_status payment_status NOT NULL DEFAULT 'NOT_PAID',
    date_and_time_of_payment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method payment_method NOT NULL DEFAULT 'CREDIT_CARD'
);

CREATE TYPE report_type As ENUM('PAYMENT', 'TRAVEL_DELAY', 'CANCEL', 'OTHER');
CREATE TYPE report_status As ENUM('CHECKED', 'UNCHECKED');

CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    username VARCHAR(50) REFERENCES users(username) ON UPDATE CASCADE ON DELETE CASCADE,
    reservation_id INTEGER REFERENCES reservations(reservation_id) ON UPDATE CASCADE,
    report_type report_type NOT NULL,
    report_text TEXT,
    report_status report_status NOT NULL DEFAULT 'UNCHECKED'
);

CREATE TYPE operation_type As ENUM('BUY', 'CANCEL');

CREATE TABLE reservations_history (
    username VARCHAR(50) REFERENCES users(username) ON UPDATE CASCADE,
    reservation_id INTEGER REFERENCES reservations(reservation_id) ON UPDATE CASCADE,
    date_and_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation_type operation_type NOT NULL,
    PRIMARY KEY (reservation_id, username, date_and_time)
);

CREATE INDEX idx_tickets_vehicle_id ON tickets(vehicle_id);
CREATE INDEX idx_reservations_ticket_id ON reservations(ticket_id);
CREATE INDEX idx_payments_reservation_id ON payments(reservation_id);
