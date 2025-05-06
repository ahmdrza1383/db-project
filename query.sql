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