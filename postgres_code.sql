CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role VARCHAR(20) NOT NULL
);

CREATE TABLE authentication_methods (
    authentication_method_id SERIAL PRIMARY KEY,
    authentication_method VARCHAR(20) NOT NULL
);

CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(100) NOT NULL,
    role INTEGER REFERENCES roles(role_id),
    name VARCHAR(100),
    email VARCHAR(100),
    phone_number VARCHAR(15),
    city VARCHAR(20),
    date_of_sign_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_picture BYTEA,
    authentication_method INTEGER REFERENCES authentication_methods(authentication_method_id)
);

CREATE TABLE payment_methods (
    payment_method_id SERIAL PRIMARY KEY,
    payment_method VARCHAR(50) NOT NULL
);

CREATE TABLE payment_statuses (
    payment_status_id SERIAL PRIMARY KEY,
    payment_status VARCHAR(50) NOT NULL
);

CREATE TABLE reservation_statuses (
    reservation_status_id SERIAL PRIMARY KEY,
    reservation_status VARCHAR(50) NOT NULL
);

CREATE TABLE report_types (
    report_type_id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL
);

CREATE TABLE report_statuses (
    report_status_id SERIAL PRIMARY KEY,
    report_status VARCHAR(50) NOT NULL
);

CREATE TABLE operation_types (
    operation_type_id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL
);

CREATE TABLE facilities_of_vehicles (
    facility_id SERIAL PRIMARY KEY,
    facility JSONB NOT NULL
);

CREATE TABLE vehicle_types (
    vehicle_type_id SERIAL PRIMARY KEY,
    vehicle_type VARCHAR(50) NOT NULL
);

CREATE TABLE vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    facility_id INTEGER REFERENCES facilities_of_vehicles(facility_id),
    vehicle_type INTEGER REFERENCES vehicle_types(vehicle_type_id)
);

CREATE TABLE flights (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    airline_name VARCHAR(100),
    flight_class VARCHAR(50),
    number_of_stop INTEGER CHECK (number_of_stop >= 0),
    flight_code VARCHAR(50),
    origin_airport VARCHAR(100),
    destination_airport VARCHAR(100)
);

CREATE TABLE trains (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    train_stars INTEGER CHECK (train_stars > 0 AND train_stars < 6),
    choosing_a_closed_coupe BOOLEAN
);

CREATE TABLE buses (
    vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    company_name VARCHAR(100),
    bus_type VARCHAR(50),
    number_of_chairs INTEGER CHECK (number_of_chairs > 0)
);

CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id) ON UPDATE CASCADE,
    origin VARCHAR(100),
    destination VARCHAR(100),
    date_and_time_of_departure TIMESTAMP,
    date_and_time_of_arrival TIMESTAMP,
    price INTEGER CHECK (price > 0),
    remaining_capacity INTEGER CHECK (remaining_capacity >= 0)
);

CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    username VARCHAR(50) REFERENCES users(username) ON UPDATE CASCADE,
    ticket_id INTEGER REFERENCES tickets(ticket_id) ON UPDATE CASCADE,
    status INTEGER REFERENCES reservation_statuses(reservation_status_id),
    date_and_time_of_reservation TIMESTAMP,
    reservation_seat INTEGER CHECK (reservation_seat > 0)
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    username VARCHAR(50) REFERENCES users(username) ON UPDATE CASCADE,
    reservation_id INTEGER REFERENCES reservations(reservation_id) ON UPDATE CASCADE,
    amount_paid INTEGER CHECK (amount_paid > 0),
    payment_status INTEGER REFERENCES payment_statuses(payment_status_id),
    date_and_time_of_payment TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method INTEGER REFERENCES payment_methods(payment_method_id)
);


CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    username VARCHAR(50) REFERENCES users(username) ON UPDATE CASCADE,
    reservation_id INTEGER REFERENCES reservations(reservation_id) ON UPDATE CASCADE,
    report_type INTEGER REFERENCES report_types(report_type_id),
    report_text TEXT,
    report_status INTEGER REFERENCES report_statuses(report_status_id)
);

CREATE TABLE reservations_history (
    username VARCHAR(50) REFERENCES users(username) ON UPDATE CASCADE,
    reservation_id INTEGER REFERENCES reservations(reservation_id) ON UPDATE CASCADE,
    date_and_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation_type INTEGER REFERENCES operation_types(operation_type_id),
    PRIMARY KEY (reservation_id, username, date_and_time)
);

CREATE INDEX idx_tickets_vehicle_id ON tickets(vehicle_id);
CREATE INDEX idx_reservations_ticket_id ON reservations(ticket_id);
CREATE INDEX idx_payments_reservation_id ON payments(reservation_id);

INSERT INTO roles (role) VALUES ('user');
INSERT INTO roles (role) VALUES ('admin');

INSERT INTO authentication_methods (authentication_method) VALUES ('email');
INSERT INTO authentication_methods (authentication_method) VALUES ('phone_number');

INSERT INTO operation_types (operation_type) VALUES ('buy');
INSERT INTO operation_types (operation_type) VALUES ('cancel');

INSERT INTO report_types (report_type) VALUES ('payment');
INSERT INTO report_types (report_type) VALUES ('travel_delay');
INSERT INTO report_types (report_type) VALUES ('cancel');
INSERT INTO report_types (report_type) VALUES ('other');

INSERT INTO report_statuses (report_status) VALUES ('checked');
INSERT INTO report_statuses (report_status) VALUES ('unchecked');

INSERT INTO payment_statuses (payment_status) VALUES ('paid');
INSERT INTO payment_statuses (payment_status) VALUES ('not_paid');

INSERT INTO payment_methods (payment_method) VALUES ('cryptocurrency');
INSERT INTO payment_methods (payment_method) VALUES ('wallet');
INSERT INTO payment_methods (payment_method) VALUES ('credit_card');

INSERT INTO reservation_statuses (reservation_status) VALUES ('reserved');
INSERT INTO reservation_statuses (reservation_status) VALUES ('not_reserved');