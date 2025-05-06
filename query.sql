--1
select n.name
from users n
where n.username in
      (select u.username from users u)
except
(select rh.username from reservations_history rh where rh.operation_type = 'BUY');

--2
