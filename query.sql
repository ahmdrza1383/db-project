--1 without join
select n.name
from users n
where n.username in
      ((select u.username from users u where u.user_role = 'USER')
       except
       (select rh.username
        from reservations_history rh
        where rh.operation_type = 'BUY'
          and rh.reservation_history_status = 'SUCCESSFUL'));


--1 with join
select u.name
from users u
         left join reservations_history rh
                   on u.username = rh.username
where rh.reservation_history_id is null
  and u.user_role = 'USER';

--2 without join
select u.name
from users u
where u.user_role = 'USER'
  and u.username in
      (select distinct(rh.username)
       from reservations_history rh
       where rh.operation_type = 'BUY'
         and rh.reservation_history_status = 'SUCCESSFUL')

--2 with join
select u.name
from users u
         inner join
     (select distinct(rh1.username) from reservations_history rh1 where rh1.operation_type = 'BUY') rh
     on u.username = rh.username;


--3
select q.username, coalesce(q.month, 0) as month, sum(coalesce(q.amount_paid, 0)) as total_paid
from (select k.username, extract (month from k.date_and_time_of_payment) as month, k.amount_paid
    from (select u.username, p.date_and_time_of_payment, p.amount_paid
    from (select u1.username from users u1 where u1.user_role = 'USER') u
    left join (select * from payments p1 where p1.payment_status = 'PAID') p on u.username = p.username) k) q
group by q.username, q.month

--4 based on the last person who purchased the ticket.
select k.username
from (select r.username, count(*) as n
      from reservations r
               inner join tickets t
                          on t.ticket_id = r.ticket_id
      where r.reservation_status = 'RESERVED'
      group by r.username, t.origin_location_id) k
group by k.username
having sum(k.n) = count(k.n);

--4 Based on all purchases.
select p.username
from (select k.username, count(*) as n
      from ((select rh.username, r.ticket_id
             from reservations_history rh
                      inner join reservations r on r.reservation_id = rh.reservation_id
             where rh.operation_type = 'BUY'
               AND rh.reservation_history_status = 'SUCCESSFUL') k
          inner join tickets t on k.ticket_id = t.ticket_id)
      group by t.origin_location_id, k.username) p
group by p.username
having sum(p.n) = count(p.n);

--5
select u.name
from users u
         inner join payments p
                    on u.username = p.username
order by p.date_and_time_of_payment desc limit 1;

--6
select phone_number
from users u
         join payments p on p.username = u.username
group by u.username
having sum(p.amount_paid) > (select avg(total_paid)
                             from (select sum(amount_paid) as total_paid
                                   from payments
                                   group by username) as user_totals);

select email
from users u
         left join payments p on p.username = u.username
group by u.username
having sum(COALESCE(p.amount_paid, 0)) > (select avg(total_paid)
                                          from (select sum(coalesce(p2.amount_paid, 0)) as total_paid
                                                from users u2
                                                         left join payments p2 on u2.username = p2.username
                                                group by u2.username));

--7
select count(r.reservation_id), v.vehicle_type as type
from reservations r
         join tickets t
              On t.ticket_id = r.ticket_id
         join vehicles v
              On v.vehicle_id = t.vehicle_id
where r.reservation_status = 'RESERVED'
group by v.vehicle_type;

--8
select name, count(rh.reservation_id) as count_of_reservation
from users u
         join reservations_history rh on rh.username = u.username
where DATE (rh.date_and_time) >= CURRENT_DATE - interval '7 days'
group by u.username
order by count (rh.reservation_id) desc limit 3;

--9
select l.city, count(r.reservation_id)
from reservations_history rh
         join reservations r on r.reservation_id = rh.reservation_id
         join tickets t on t.ticket_id = r.ticket_id
         join locations l on l.location_id = t.origin_location_id
where l.province = 'Tehran'
  and rh.reservation_history_status = 'SUCCESSFUL'
  and rh.operation_type = 'BUY'
group by l.city;

--10
select u.username, l.city
from users u
         join reservations r on r.username = u.username
         join reservations_history rh on r.reservation_id = rh.reservation_id
         join tickets t on t.ticket_id = r.ticket_id
         join locations l on l.location_id = t.origin_location_id
where u.username = (select username
                    from users u2
                    order by u2.date_of_sign_in limit 1
    );

--11
select u.name
from users u
where u.user_role = 'ADMIN';

--12
select u.name
from users u
         inner join
     (select rh.username, count(*) as n
      from reservations_history rh
      where rh.operation_type = 'BUY'
        and rh.reservation_history_status = 'SUCCESSFUL'
      group by rh.username) k
     on u.username = k.username
where k.n > 1;

--13
select distinct(u.username)
from users u
         join reservations_history rh on rh.username = u.username
         join reservations r on r.reservation_id = rh.reservation_id
         join tickets t on t.ticket_id = r.ticket_id
         join vehicles v on v.vehicle_id = t.vehicle_id
where u.user_role = 'USER'
  and rh.operation_type = 'BUY'
  and rh.reservation_history_status = 'SUCCESSFUL'
group by u.username, v.vehicle_type
having count(*) < 3


--14
SELECT rh.username
FROM reservations_history rh
         INNER JOIN reservations r
                    ON r.reservation_id = rh.reservation_id
         INNER JOIN tickets t
                    ON t.ticket_id = r.ticket_id
         INNER JOIN vehicles v
                    ON v.vehicle_id = t.vehicle_id
WHERE rh.operation_type = 'BUY'
  AND rh.reservation_history_status = 'SUCCESSFUL'
GROUP BY rh.username
HAVING COUNT(DISTINCT v.vehicle_type) >= 3


--15
SELECT t.ticket_id,
       t.price,
       t.departure_start,
       l1.city          AS origin_city,
       l2.city          AS destination_city,
       rh.date_and_time AS purchase_time,
       u.username,
       u.name
FROM reservations_history rh
         INNER JOIN reservations r ON rh.reservation_id = r.reservation_id
         INNER JOIN tickets t ON r.ticket_id = t.ticket_id
         INNER JOIN users u ON rh.username = u.username
         INNER JOIN locations l1 ON t.origin_location_id = l1.location_id
         INNER JOIN locations l2 ON t.destination_location_id = l2.location_id
WHERE rh.operation_type = 'BUY'
  AND rh.reservation_history_status = 'SUCCESSFUL'
  AND DATE (rh.date_and_time) = CURRENT_DATE
ORDER BY rh.date_and_time;

--16
select t.ticket_id, count(r.reservation_id) as res_count
from tickets t
         join reservations r on t.ticket_id = r.ticket_id
where r.reservation_status = 'RESERVED'
group by t.ticket_id
order by res_count desc limit 1
offset 1;

select t.ticket_id, (t.total_capacity - t.remaining_capacity) * 100 / t.total_capacity as buy_percentage
from tickets t
order by buy_percentage desc
offset 1 limit 1;

--17
-- find admin with accepted cancelation
select check_by, count(*)
from requests r
where r.request_subject = 'CANCEL'
  and r.is_checked = true
  and r.is_accepted = true
group by r.check_by
order by count(*);

--all admin with cancel percent
SELECT u.username                                                          AS admin_username,
       COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*)
                                  FROM requests r2
                                  WHERE r2.check_by = u.username
                                    AND r2.request_subject = 'CANCEL'), 0) AS cancel_percentage
FROM users u
         JOIN
     requests r ON r.check_by = u.username
WHERE u.user_role = 'ADMIN'
  AND r.request_subject = 'CANCEL'
  AND r.is_accepted = true
GROUP BY u.username
ORDER BY cancel_percentage desc LIMIT 1;

--18
select name, count(*)
from users u
         join reservations_history rh on rh.username = u.username
where rh.operation_type = 'CANCEL'
  and rh.reservation_history_status = 'CANCELED'
group by u.username
order by count(*) desc limit 1;

update users
set name = 'redington'
where username = (select u.username
                  from users u
                           join reservations_history rh on rh.username = u.username
                  where rh.operation_type = 'CANCEL'
                    and rh.reservation_history_status = 'CANCELED'
                  group by u.username
                  order by count(*) desc limit 1
    );

--19
SELECT u.username
from users u
         JOIN reservations_history rh ON rh.username = u.username
WHERE rh.operation_type = 'CANCEL'
  AND rh.reservation_history_status = 'CANCELED'
  and u.name = 'ridingtone'

delete
from reservation
where username = (SELECT u.username
                  from users u
                           JOIN reservations_history rh ON rh.username = u.username
                  WHERE rh.operation_type = 'CANCEL'
                    AND rh.reservation_history_status = 'CANCELED'
                    and u.name = 'ridingtone' limit 1
    );

--20
update reservations
set reservation_status           = 'NOT_RESERVED',
    username                     = null,
    date_and_time_of_reservation = null
where reservation_id in (select r.reservation_id
                         from reservations r
                         where r.reservation_status = 'TEMPORARY'
                           and current_timestamp - r.date_and_time_of_reservation > interval '10 minutes'
    );

--21
SELECT DISTINCT t.ticket_id
FROM tickets t
         JOIN flights f ON t.vehicle_id = f.vehicle_id
         JOIN reservations r ON t.ticket_id = r.ticket_id
WHERE f.airline_name = 'Mahan Air'
  AND r.reservation_status = 'RESERVED'
  AND DATE (r.date_and_time_of_reservation) = CURRENT_DATE - INTERVAL '1 day';

update tickets
set price = price * 90 / 100
where ticket_id in (SELECT DISTINCT t.ticket_id
                    FROM tickets t
                             JOIN flights f ON t.vehicle_id = f.vehicle_id
                             JOIN reservations r ON t.ticket_id = r.ticket_id
                    WHERE f.airline_name = 'Mahan Air'
                      AND r.reservation_status = 'RESERVED'
                      AND DATE (r.date_and_time_of_reservation) = CURRENT_DATE - INTERVAL '1 day');

--22
select t.ticket_id, count(*)
from reports r
         join reservations r2 on r.reservation_id = r2.reservation_id
         join tickets t on t.ticket_id = r2.ticket_id
group by t.ticket_id
order by count(*) desc limit 1;


select r.report_type, count(*)
from reports r
         join reservations r4 on r4.reservation_id = r.reservation_id
         join tickets t2 on t2.ticket_id = r4.ticket_id
where t2.ticket_id =
      (select t.ticket_id
       from reports r3
                join reservations r2 on r3.reservation_id = r2.reservation_id
                join tickets t on t.ticket_id = r2.ticket_id
       group by t.ticket_id
       order by count(*) desc limit 1
    )
group by r.report_type;
