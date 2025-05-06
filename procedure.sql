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

create or replace procedure  get_reservation_in_city(
input_city VARCHAR,
inout res refcursor
)
language PLPGSQL
as $$
declare
location_id_ INTEGER;
begin
	SELECT location_id INTO location_id_
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
