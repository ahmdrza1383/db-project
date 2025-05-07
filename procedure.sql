--1
create
or replace procedure  get_user_ticket(
input_email VARCHAR,
input_phone_number VARCHAR,
inout res refcursor
)
language PLPGSQL
as $$
declare
user_name_ VARCHAR;
begin
select username
into user_name_
from users
where email = input_email
   or phone_number = input_phone_number;

open res for
select r.reservation_id,
       r.ticket_id,
       l1.city AS origin_city,
       l2.city AS destination_city,
       t.departure_start,
       r.date_and_time_of_reservation
FROM reservations r
         JOIN tickets t ON r.ticket_id = t.ticket_id
         JOIN locations l1 ON t.origin_location_id = l1.location_id
         JOIN locations l2 ON t.destination_location_id = l2.location_id
WHERE r.username = user_name_
  AND r.reservation_status = 'RESERVED'
ORDER BY r.date_and_time_of_reservation DESC;
end;
$$;

begin;
CALL get_user_ticket('mehdi.shariati@email.com', null, 'my_table');
fetch all my_table;
close my_table;
commit;

--2

create
or replace procedure  get_user_have_cancelation(
input_email VARCHAR,
input_phone_number VARCHAR,
inout res refcursor
)
language PLPGSQL
as $$
declare
user_name_ VARCHAR;
begin
select username
into user_name_
from users
where email = input_email
   or phone_number = input_phone_number;

open res for
select distinct u.name
from users u
         join reservations_history rh on rh.username = u.username
where rh.cancel_by = user_name_;
end;
$$;

begin;
CALL get_user_have_cancelation('admin1@email.com', null, 'my_table');
fetch all my_table;
close my_table;
commit;

--3

create
or replace procedure  get_reservation_in_city(
input_city VARCHAR,
inout res refcursor
)
language PLPGSQL
as $$
declare
location_id_ INTEGER;
begin
SELECT location_id
INTO location_id_
FROM locations
WHERE city = input_city;

open res for
select r.reservation_id,
       r.ticket_id,
       l1.city AS origin_city,
       l2.city AS destination_city,
       t.departure_start,
       r.date_and_time_of_reservation
FROM reservations r
         JOIN tickets t ON r.ticket_id = t.ticket_id
         JOIN locations l1 ON t.origin_location_id = l1.location_id
         JOIN locations l2 ON t.destination_location_id = l2.location_id
where t.origin_location_id = location_id_
  and r.reservation_status = 'RESERVED'
ORDER BY r.date_and_time_of_reservation DESC;
end;
$$;

begin;
CALL get_reservation_in_city('Mashhad', 'my_table');
fetch all my_table;
close my_table;
commit;
--4
CREATE
OR REPLACE PROCEDURE search_tickets_by_term(
    input_term VARCHAR,
    INOUT res REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
OPEN res FOR
SELECT r.ticket_id,
       r.reservation_id,
       r.username,
       u.name  AS passenger_name,
       l1.city AS origin_city,
       l2.city AS destination_city,
       f.flight_class,
       t.departure_start,
       b.company_name
FROM reservations r
         JOIN users u ON r.username = u.username
         JOIN tickets t ON r.ticket_id = t.ticket_id
         JOIN locations l1 ON t.origin_location_id = l1.location_id
         JOIN locations l2 ON t.destination_location_id = l2.location_id
         left JOIN flights f ON t.vehicle_id = f.vehicle_id
         left join buses b on b.vehicle_id = t.vehicle_id
WHERE r.reservation_status = 'RESERVED'
  AND (
    u.name ILIKE '%' || input_term || '%'
          OR l1.city ILIKE '%' || input_term || '%'
          OR l2.city ILIKE '%' || input_term || '%'
          OR f.flight_class ILIKE '%' || input_term || '%'
          or b.company_name ilike '%' || input_term || '%'
    );
END;
$$;

begin;
CALL search_tickets_by_term('ab', 'my_table');
fetch all my_table;
close my_table;
commit;

--5
create
or replace procedure  get_user_in_city(
input_email VARCHAR,
input_phone_number VARCHAR,
inout res refcursor
)
language PLPGSQL
as $$
declare
location_ INTEGER;
begin
select city
into location_
from users
where email = input_email
   or phone_number = input_phone_number;

open res for
select u.username,
       u.name,
       u.email,
       u.phone_number,
       u.date_of_sign_in,
       l.city
from users u
         join locations l on l.location_id = u.city
WHERE l.location_id = location_;
end;
$$;

begin;
CALL get_user_in_city(null,'09121112233', 'my_table');
fetch all my_table;
close my_table;
commit;

--6
create
or replace procedure  get_top_user_by_buy_ticket(
input_date 	DATE,
input_n INTEGER,
inout res refcursor
)
language PLPGSQL
as $$
begin
open res for
SELECT u.username,
       u.name,
       u.email,
       COUNT(r.reservation_id) AS reservation_count
FROM users u
         LEFT JOIN reservations r ON u.username = r.username
WHERE r.reservation_status = 'RESERVED'
  AND DATE (r.date_and_time_of_reservation) >= input_date
GROUP BY u.username
ORDER BY reservation_count DESC, u.username
    LIMIT input_n;
end;
$$;

begin;
CALL get_top_user_by_buy_ticket('2025-03-10'	,5, 'my_table');
fetch all my_table;
close my_table;
commit;


--7
CREATE
OR REPLACE PROCEDURE get_canceled_tickets_by_vehicle_type(
    input_vehicle_type VARCHAR,
    INOUT res REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
OPEN res FOR
SELECT rh.reservation_id,
       r.ticket_id,
       rh.cancel_by,
       l1.city          AS origin_city,
       l2.city          AS destination_city,
       t.departure_start,
       rh.date_and_time AS cancel_date
FROM reservations_history rh
         JOIN reservations r ON rh.reservation_id = r.reservation_id
         JOIN tickets t ON r.ticket_id = t.ticket_id
         JOIN vehicles v ON t.vehicle_id = v.vehicle_id
         JOIN locations l1 ON t.origin_location_id = l1.location_id
         JOIN locations l2 ON t.destination_location_id = l2.location_id
WHERE rh.operation_type = 'CANCEL'
  AND rh.reservation_history_status = 'CANCELED'
  AND v.vehicle_type = input_vehicle_type::vehicle_type
ORDER BY rh.date_and_time DESC;
END;
$$;


begin;
CALL get_canceled_tickets_by_vehicle_type('BUS', 'my_table');
fetch all my_table;
close my_table;
commit;

--8
rollback;
CREATE
OR REPLACE PROCEDURE get_top_users_by_report_subject(
    input_report_subject VARCHAR,
    INOUT res REFCURSOR
)
LANGUAGE plpgsql
AS $$
BEGIN
OPEN res FOR
SELECT u.username,
       u.name,
       u.email,
       COUNT(r.report_id) AS report_count
FROM users u
         LEFT JOIN reports r ON u.username = r.username
WHERE r.report_type = input_report_subject::report_type
GROUP BY u.username
ORDER BY report_count DESC, u.username;
END;
$$;

begin;
CALL get_top_users_by_report_subject('PAYMENT', 'my_table');
fetch all my_table;
close my_table;
commit;