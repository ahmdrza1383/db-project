CREATE TABLE locations
(
    location_id SERIAL PRIMARY KEY,
    city        VARCHAR(100) NOT NULL,
    province    VARCHAR(100) NOT NULL,
    UNIQUE (city, province)
);

CREATE TYPE user_role As ENUM ('USER', 'ADMIN');
CREATE TYPE authentication_method As ENUM ('EMAIL', 'PHONE_NUMBER');

CREATE TABLE users
(
    username              VARCHAR(50) PRIMARY KEY,
    password              VARCHAR(100)          NOT NULL,
    user_role             user_role             NOT NULL DEFAULT 'USER',
    name                  VARCHAR(100),
    email                 VARCHAR(100)          NOT NULL UNIQUE,
    phone_number          VARCHAR(15) UNIQUE,
    city                  INTEGER REFERENCES locations (location_id) ON UPDATE CASCADE,
    date_of_sign_in       TIMESTAMP                      DEFAULT CURRENT_TIMESTAMP,
    profile_picture       BYTEA,
    authentication_method authentication_method NOT NULL DEFAULT 'EMAIL',
    profile_status        BOOLEAN                        DEFAULT TRUE,
    date_of_birth         DATE,
    wallet_balance        INTEGER               not null default 0
);

CREATE TYPE vehicle_type As ENUM ('BUS', 'TRAIN', 'FLIGHT');

CREATE TABLE vehicles
(
    vehicle_id   SERIAL PRIMARY KEY,
    vehicle_type vehicle_type NOT NULL
);

CREATE TABLE flights
(
    vehicle_id          INTEGER PRIMARY KEY REFERENCES vehicles (vehicle_id) ON UPDATE CASCADE,
    airline_name        VARCHAR(100) NOT NULL,
    flight_class        VARCHAR(50)  NOT NULL,
    number_of_stop      INTEGER CHECK (number_of_stop >= 0) DEFAULT 0,
    flight_code         VARCHAR(50)  NOT NULL,
    origin_airport      VARCHAR(100) NOT NULL,
    destination_airport VARCHAR(100) NOT NULL,
    facility            JSONB
);

CREATE TABLE trains
(
    vehicle_id              INTEGER PRIMARY KEY REFERENCES vehicles (vehicle_id) ON UPDATE CASCADE,
    train_stars             INTEGER CHECK (train_stars > 0 AND train_stars < 6) NOT NULL,
    choosing_a_closed_coupe BOOLEAN DEFAULT False,
    facility                JSONB
);

CREATE TABLE buses
(
    vehicle_id       INTEGER PRIMARY KEY REFERENCES vehicles (vehicle_id) ON UPDATE CASCADE,
    company_name     VARCHAR(100) NOT NULL,
    bus_type         VARCHAR(50)  NOT NULL,
    number_of_chairs INTEGER CHECK (number_of_chairs > 0) DEFAULT 25,
    facility         JSONB
);

CREATE TABLE tickets
(
    ticket_id               SERIAL PRIMARY KEY,
    vehicle_id              INTEGER REFERENCES vehicles (vehicle_id) ON UPDATE CASCADE   NOT NULL,
    origin_location_id      INTEGER REFERENCES locations (location_id) ON UPDATE CASCADE NOT NULL,
    destination_location_id INTEGER REFERENCES locations (location_id) ON UPDATE CASCADE NOT NULL,
    departure_start         TIMESTAMP                                                    NOT NULL,
    departure_end           TIMESTAMP                                                    NOT NULL,
    is_round_trip           BOOLEAN                                                      NOT NULL DEFAULT FALSE,
    return_start            TIMESTAMP,
    return_end              TIMESTAMP,
    price                   INTEGER CHECK (price > 0)                                    NOT NULL,
    total_capacity          INTEGER CHECK ( total_capacity > 0 )                         NOT NULL,
    remaining_capacity      INTEGER CHECK (remaining_capacity >= 0)                      NOT NULL,
    ticket_status           BOOLEAN                                                               DEFAULT TRUE
);

CREATE TYPE reservation_status As ENUM ('RESERVED', 'NOT_RESERVED', 'TEMPORARY');

CREATE TABLE reservations
(
    reservation_id               SERIAL PRIMARY KEY,
    username                     VARCHAR(50) REFERENCES users (username) ON UPDATE CASCADE,
    ticket_id                    INTEGER REFERENCES tickets (ticket_id) ON UPDATE CASCADE NOT NULL,
    reservation_status           reservation_status                                       NOT NULL DEFAULT 'NOT_RESERVED',
    date_and_time_of_reservation TIMESTAMP,
    reservation_seat             INTEGER CHECK (reservation_seat > 0)                     NOT NULL
);

CREATE TYPE payment_status As ENUM ('PAID', 'NOT_PAID', 'WAITING');
CREATE TYPE payment_method As ENUM ('CRYPTOCURRENCY', 'WALLET', 'CREDIT_CARD');

CREATE TABLE payments
(
    payment_id               SERIAL PRIMARY KEY,
    username                 VARCHAR(50) REFERENCES users (username) ON UPDATE CASCADE          NOT NULL,
    reservation_id           INTEGER REFERENCES reservations (reservation_id) ON UPDATE CASCADE NOT NULL,
    amount_paid              INTEGER CHECK (amount_paid > 0)                                    NOT NULL,
    payment_status           payment_status                                                     NOT NULL DEFAULT 'NOT_PAID',
    date_and_time_of_payment TIMESTAMP                                                                   DEFAULT CURRENT_TIMESTAMP,
    payment_method           payment_method                                                     NOT NULL DEFAULT 'CREDIT_CARD'
);

CREATE TYPE report_type As ENUM ('PAYMENT', 'TRAVEL_DELAY', 'CANCEL', 'OTHER');
CREATE TYPE report_status As ENUM ('CHECKED', 'UNCHECKED');

CREATE TABLE reports
(
    report_id      SERIAL PRIMARY KEY,
    username       VARCHAR(50) REFERENCES users (username) ON UPDATE CASCADE          NOT NULL,
    reservation_id INTEGER REFERENCES reservations (reservation_id) ON UPDATE CASCADE NOT NULL,
    report_type    report_type                                                        NOT NULL,
    report_text    TEXT                                                               NOT NULL,
    report_status  report_status                                                      NOT NULL DEFAULT 'UNCHECKED'
);

CREATE TYPE operation_type As ENUM ('BUY', 'CANCEL');
CREATE TYPE buy_status AS ENUM ('SUCCESSFUL', 'UNSUCCESSFUL')

CREATE TABLE reservations_history
(
    reservation_history_id     SERIAL PRIMARY KEY,
    username                   VARCHAR(50) REFERENCES users (username) ON UPDATE CASCADE          NOT NULL,
    reservation_id             INTEGER REFERENCES reservations (reservation_id) ON UPDATE CASCADE NOT NULL,
    date_and_time              TIMESTAMP                                                          DEFAULT CURRENT_TIMESTAMP,
    operation_type             operation_type                                                     NOT NULL,
    cancel_by                  VARCHAR(50) REFERENCES users (username) ON UPDATE CASCADE,
    buy_status                 buy_status,

    CONSTRAINT check_status_for_operation_type CHECK (
        (operation_type = 'CANCEL' AND buy_status IS NULL AND cancel_by IS NOT NULL) OR
        (operation_type = 'BUY' AND buy_status IS NOT NULL AND cancel_by IS NULL)
    )
);

CREATE TYPE request_subject AS ENUM ('CANCEL', 'CHANGE_DATE');

CREATE TABLE requests
(
    request_id      SERIAL PRIMARY KEY,
    username        VARCHAR(50) REFERENCES users (username) ON UPDATE CASCADE          NOT NULL,
    reservation_id  INTEGER REFERENCES reservations (reservation_id) ON UPDATE CASCADE NOT NULL,
    request_subject request_subject                                                    NOT NULL,
    request_text    TEXT                                                               NOT NULL,
    is_checked      BOOLEAN                                                            NOT NULL DEFAULT FALSE,
    is_accepted     BOOLEAN                                                            NOT NULL DEFAULT FALSE,
    check_by        VARCHAR(50) REFERENCES users (username) ON UPDATE CASCADE,
    date_and_time   TIMESTAMP                                                                   DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX idx_tickets_vehicle_id ON tickets (vehicle_id);
CREATE INDEX idx_reservations_ticket_id ON reservations (ticket_id);
CREATE INDEX idx_payments_reservation_id ON payments (reservation_id);
CREATE INDEX idx_reservations_username ON reservations (username);
CREATE INDEX idx_payments_payment_status ON payments (payment_status);
CREATE INDEX idx_payments_date_and_time ON payments (date_and_time_of_payment);
CREATE INDEX idx_tickets_origin_location_id ON tickets (origin_location_id);
CREATE INDEX idx_locations_province ON locations (province);
CREATE INDEX idx_users_date_of_sign_in ON users (date_of_sign_in);
CREATE INDEX idx_users_user_role ON users (user_role);
CREATE INDEX idx_reservations_history_cancel_by ON reservations_history (cancel_by);
CREATE INDEX idx_reservations_history_operation_type ON reservations_history (operation_type);
CREATE INDEX idx_users_name ON users (name);
CREATE INDEX idx_flights_airline_name ON flights (airline_name);
CREATE INDEX idx_reports_reservation_id ON reports (reservation_id);
