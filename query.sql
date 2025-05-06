--1 without join
select n.name from users n
    where n.username in
        (select u.username from users u ) except  (select rh.username from reservations_history rh where rh.operation_type = 'BUY');

--1 with join
select u.name
	from users u left join reservations_history rh
		on u.username  = rh.username
			where rh.reservation_history_id is null
			and u.user_role = 'USER';

--2 without join
select u.name
    from users u
        where u.username in
            (select distinct(rh.username) from reservations_history rh
                where rh.operation_type = 'BUY')

--2 with join
select u.name
	from users u inner join 
	(select distinct(rh1.username) from reservations_history rh1 where rh1.operation_type = 'BUY') rh
		on u.username = rh.username;


--3
select p.username, extract(month from p.date_and_time_of_payment) as mounth, sum(p.amount_paid)
    from payments p
    	group by extract(month from p.date_and_time_of_payment), p.username;

--4 based on the last person who purchased the ticket.
select k.username from
	(select r.username, count(*) as n
		from reservations r inner join tickets t
			on t.ticket_id = r.ticket_id
				where r.reservation_status = 'RESERVED'
					group by r.username, t.origin_location_id) k
						group by k.username
							having sum(k.n) = count(k.n);

--4 Based on all purchases.
select p.username from
    (select k.username, count(*) as n from
        ((select rh.username, r.ticket_id from
            reservations_history rh inner join reservations r  on r.reservation_id = rh.reservation_id where rh.operation_type = 'BUY')k
                inner join tickets t on k.ticket_id = t.ticket_id)
                    group by t.origin_location_id, k.username) p
                        group by p.username having sum(p.n) = count(p.n);

--5
select u.name
	from users u  inner join payments p
		on u.username  = p.username
			order by p.date_and_time_of_payment desc
				limit 1;


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
select name, count(r.reservation_id) as count_of_reservation
from users u
         join reservations r on r.username = u.username
where DATE (r.date_and_time_of_reservation) >= CURRENT_DATE - interval '7 days'
group by u.username
order by count (r.reservation_id) desc limit 3;

--9
select l.city, count(r.reservation_id)
from reservations r
         join tickets t on t.ticket_id = r.ticket_id
         join locations l on l.location_id = t.origin_location_id
where l.province = 'Tehran'
group by l.city;

--10
select u.username, l.city
from users u
         join reservations r on r.username = u.username
         join tickets t on t.ticket_id = r.ticket_id
         join locations l on l.location_id = t.origin_location_id
where u.username = (select username
                    from users u2
                    order by u2.date_of_sign_in limit 1
    );
