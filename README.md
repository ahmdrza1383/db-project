<div dir="rtl">

# فاز 1 پروژه

## 1. پیاده‌سازی مدل‌ها

ابتدا مدل‌های داخل داک به‌صورت کامل پیاده‌سازی شده‌اند. طراحی جداول با دقت از روی مدل‌ها انجام شده و در ابتدا ارتباطات بین جداول طبق برداشت از داک تنظیم و پیاده‌سازی شده است.  

### به عنوان نمونه:  

### جدول users:

ستون **username** شناسه یکتای کاربر است که به عنوان نام کاربری استفاده می‌شود.  
ستون **password** رمز عبور کاربر را نگهداری می‌کند.  
ستون **role** نقش کاربر را مشخص می‌کند.  
ستون **name** نام کامل کاربر را مشخص می‌کند.  
ستون **email** ایمیل کاربر را نگهداری می‌کند.  
ستون **phone_number** شماره تلفن کاربر را نگهداری می‌کند.  
ستون **city** شهر محل سکونت کاربر را مشخص می‌کند.  
ستون **date_of_sign_in** تاریخ ثبت‌نام کاربر را نگهداری می‌کند.  
ستون **profile_picture** عکس پروفایل کاربر را به صورت داده باینری نگهداری می‌کند.  
ستون **authentication_method** روش ورود کاربر به سامانه را مشخص می‌کند.  

---

### جدول tickets:

ستون **ticket_id** شناسه یکتای بلیط است که به‌صورت خودکار افزایش پیدا می‌کند.  
ستون **vehicle_id** شماره وسیله نقلیه‌ای است که این بلیط به آن مربوط می‌شود.  
ستون **origin** مبدا حرکت وسیله نقلیه را مشخص می‌کند.  
ستون **destination** مقصد حرکت وسیله نقلیه را مشخص می‌کند.  
ستون **date_and_time_of_departure** تاریخ و زمان حرکت وسیله نقلیه را نگهداری می‌کند.  
ستون **date_and_time_of_arrival** تاریخ و زمان رسیدن وسیله نقلیه به مقصد را نگهداری می‌کند.  
ستون **price** قیمت بلیط را مشخص می‌کند و باید بیشتر از صفر باشد.  
ستون **remaining_capacity** تعداد ظرفیت باقی‌مانده برای فروش بلیط را مشخص می‌کند و نمی‌تواند عدد منفی باشد.  

---

### نکته:  
- فعلاً کلیدهای خارجی مشخص نشده‌اند. این موضوع در مرحله طراحی روابط بررسی و پیاده‌سازی خواهد شد.  

---

## 2. پیاده‌سازی ارتباطات بین جداول

برای ارتباطات بین جداول، طبق داک و نیازهای پروژه، به صورت زیر عمل شده است:  
- جداول به‌طور مناسب به یکدیگر مرتبط شده‌اند.  
- چون روابط ما از نوع n به m نیستند، جدول جدیدی برای ارتباطات طراحی نشده است و صرفاً روابط با کلید خارجی برقرار شده‌اند.  

### به عنوان نمونه:  

### کلیدهای خارجی جدول payments:

ستون **username** به جدول users اشاره دارد و مشخص می‌کند که این پرداخت مربوط به کدام کاربر است.  
ستون **reservation_id** به جدول reservations اشاره دارد و نشان می‌دهد که پرداخت مربوط به کدام رزرو است.  

---

### کلیدهای خارجی جدول reports:

ستون **username** به جدول users اشاره دارد و مشخص می‌کند که این گزارش توسط کدام کاربر ثبت شده است.  
ستون **reservation_id** به جدول reservations اشاره دارد و مشخص می‌کند که این گزارش مربوط به کدام رزرو است.  

---

### نکته:  
- فعلاً جداولی که برای مقادیر مشخص طراحی شده‌اند، در این بخش آورده نشده‌اند.  
- در رابطه بین users و reservations، ما سه حالت **خرید، لغو، و تغییر** داریم. با این حال، در جدول reservations فقط یک ستون به نام **username** وجود دارد که آخرین کاربری که بلیط را خریداری کرده نگهداری می‌شود.  
- در صورتی که کاربر بلیط را لغو کند، مقدار **username** به **NULL** تغییر پیدا می‌کند و **status** مناسب برای لغو ست می‌شود.  
- همچنین تغییر بلیط، به صورت **لغو بلیط قبلی و خرید بلیط جدید** در نظر گرفته می‌شود.  

---

## 3. تاریخچه خرید و فروش بلیط‌ها

برای تکمیل طراحی، جدولی برای نگهداری **تاریخچه خرید و فروش بلیط‌ها** ایجاد شده است. این جدول تاریخچه کلیه عملیات **خرید، لغو، و تغییر رزرو بلیط‌ها** را ثبت می‌کند و امکان پیگیری دقیق سوابق را فراهم می‌آورد.  
به دلیل روش پیاده‌سازی روابط بین کاربر و رزرو که در بخش قبل توضیح داده شد، برای نگهداری تاریخچه تمامی عملیات‌ها، نیاز به این جدول جداگانه وجود دارد.  
کلید اصلی این جدول ترکیبی از **username**، **reservation_id**، و **date_and_time** است.  
همچنین تغییر یک بلیط، به صورت **لغو بلیط قبلی و خرید بلیط جدید در یک لحظه** در این جدول ثبت می‌شود.  

---

## 4. جداول با مقادیر مشخص

برای ستون‌هایی که فقط باید **مقادیر مشخص** داشته باشند، جداول جداگانه طراحی شده‌اند و این مقادیر به صورت **دستی** در دیتابیس وارد شده‌اند.  
این کار باعث **محدود کردن انتخاب‌ها** و جلوگیری از **ورود داده اشتباه** می‌شود.  

### به عنوان نمونه:  

### جدول roles:

ستون **role_id** شناسه یکتای نقش است که به‌صورت خودکار افزایش پیدا می‌کند.  
ستون **role** نام نقش را نگهداری می‌کند. این نقش مشخص می‌کند که کاربر چه سطح دسترسی یا وظیفه‌ای در سیستم دارد (مانند کاربر عادی یا مدیر).  

---

### جدول authentication_methods:

ستون **authentication_method_id** شناسه یکتای روش احراز هویت است که به‌صورت خودکار افزایش پیدا می‌کند.  
ستون **authentication_method** روش ورود کاربر به سامانه را نگهداری می‌کند (مانند ایمیل یا شماره تلفن).  

---

## 5. ویژگی‌های اضافه برای وسایل نقلیه

برای ویژگی‌های خاص و اضافی وسایل نقلیه، یک جدول جداگانه طراحی شده است. اطلاعات این جدول به صورت **JSON** ذخیره می‌شود تا نیازی به تعریف ستون جدید برای هر ویژگی وجود نداشته باشد.  
این روش باعث **انعطاف‌پذیری بالا** در افزودن ویژگی‌های جدید برای وسایل نقلیه در آینده می‌شود.  

---

## 6. کدهای پایگاه داده

در نهایت، بر اساس دیاگرام‌های طراحی‌شده، **کدهای SQL** مربوط به ایجاد جداول و ارتباطات آنها نوشته شده‌اند.  
این کدها به‌صورت **دقیق و منطبق با مدل‌ها** و همچنین **بهینه‌شده** پیاده‌سازی شده‌اند.
</div>

<div dir="rtl">

# فاز ۲ پروژه
## کوئری ها
## کوئری ۱ (بدون JOIN)

<div dir="ltr">

```sql
select n.name
from users n
where n.username in
      ((select u.username from users u where u.user_role = 'USER')
       except
       (select rh.username
        from reservations_history rh
        where rh.operation_type = 'BUY'
          and rh.reservation_history_status = 'SUCCESSFUL'));
```
<div dir="rtl">

### توضیح:
 نام کاربرانی که نقش USER دارن و هیچ خرید موفقی نکردن.  
چرا users: برای گرفتن نام و نقش کاربر.  
چرا reservations_history: برای چک کردن خریدهای موفق.  
چرا EXCEPT: برای حذف کاربران با خرید موفق.
## کوئری ۱ (با JOIN)

<div dir="ltr">

```sql
select u.name
from users u
         left join reservations_history rh
                   on u.username = rh.username
where rh.reservation_history_id is null
  and u.user_role = 'USER';
  ```
<div dir="rtl">


### توضیح:

 نام کاربرانی که نقش USER دارن و هیچ خرید موفقی نکردن.  
چرا users: برای گرفتن نام و نقش کاربر.  
چرا reservations_history: برای چک کردن خریدهای موفق.  
چرا LEFT JOIN: برای پیدا کردن کاربرایی که توی reservations_history هیچ رکوردی ندارن.

## کوئری ۲ (بدون JOIN)

<div dir="ltr">

```sql
select u.name
from users u
where u.user_role = 'USER'
  and u.username in
      (select distinct(rh.username)
       from reservations_history rh
       where rh.operation_type = 'BUY'
         and rh.reservation_history_status = 'SUCCESSFUL')
```
<div dir="rtl">

### توضیح:

 نام کاربرانی که نقش USER دارن و حداقل یه بلیط خریدن.  
چرا users: برای گرفتن نام و فیلتر نقش کاربر.  
چرا reservations_history: برای پیدا کردن کاربرانی که خرید موفق کردن.  
چرا IN: برای انتخاب کاربرانی که توی لیست خریدهای موفق هستن.

## کوئری ۲ (با JOIN)

<div dir="ltr">

```sql
select u.name
from users u
         inner join
     (select distinct(rh1.username) from reservations_history rh1 where rh1.operation_type = 'BUY') rh
     on u.username = rh.username;
```
<div dir="rtl">

### توضیح:

 نام کاربرانی که حداقل یه بلیط خریدن.  
چرا users: برای گرفتن نام کاربر.  
چرا reservations_history: برای پیدا کردن کاربرانی که خرید کردن.  
چرا INNER JOIN: برای انتخاب فقط کاربرانی که توی reservations_history خرید دارن.


markdown

Copy
# فاز ۲ پروژه

## کوئری ۳
<div dir="ltr">

```sql
select q.username, coalesce(q.month, 0) as month, sum(coalesce(q.amount_paid, 0)) as total_paid
from (select k.username, extract (month from k.date_and_time_of_payment) as month, k.amount_paid
    from (select u.username, p.date_and_time_of_payment, p.amount_paid
    from (select u1.username from users u1 where u1.user_role = 'USER') u
    left join (select * from payments p1 where p1.payment_status = 'PAID') p on u.username = p.username) k) q
group by q.username, q.month

```
<div dir="rtl">


### توضیح:
 مجموع پرداخت‌های هر کاربر در ماه‌های مختلف.  
چرا users: برای گرفتن کاربران با نقش USER.  
چرا payments: برای محاسبه پرداخت‌های موفق.  
چرا LEFT JOIN: برای شامل کردن کاربران بدون پرداخت.


## کوئری ۴ (بر اساس آخرین خریدار بلیط)

<div dir="ltr">

```sql
select k.username
from (select r.username, count(*) as n
      from reservations r
               inner join tickets t
                          on t.ticket_id = r.ticket_id
      where r.reservation_status = 'RESERVED'
      group by r.username, t.origin_location_id) k
group by k.username
having sum(k.n) = count(k.n);

```
<div dir="rtl">

### توضیح:
 کاربرانی که در هر شهر فقط یه بلیط رزرو کردن.  
چرا reservations: برای گرفتن رزروهای کاربران.  
چرا tickets: برای دسترسی به شهر مبدا.  
چرا INNER JOIN: برای اتصال رزروها به بلیط‌ها.



## کوئری ۵
<div dir="ltr">

```sql
select u.name
from users u
         inner join payments p
                    on u.username = p.username
order by p.date_and_time_of_payment desc limit 1;
```
<div dir="rtl">

### توضیح:
 نام کاربری که جدیدترین بلیط رو خریده.  
چرا users: برای گرفتن نام کاربر.  
چرا payments: برای پیدا کردن آخرین پرداخت.  
چرا INNER JOIN: برای اتصال کاربران به پرداخت‌هاشون.


## کوئری ۶ (بر اساس افرادی که خرید داشتند)
<div dir="ltr">

```sql
select phone_number
from users u
         join payments p on p.username = u.username
group by u.username
having sum(p.amount_paid) > (select avg(total_paid)
                             from (select sum(amount_paid) as total_paid
                                   from payments
                                   group by username) as user_totals);
```
<div dir="rtl">

### توضیح:
 شماره تلفن کاربرانی که مجموع پرداخت‌هاشون از میانگین پرداخت کاربران بیشتره.  
چرا users: برای گرفتن شماره تلفن.  
چرا payments: برای محاسبه مجموع پرداخت‌ها.  
چرا INNER JOIN: فقط کاربران با پرداخت رو می‌خوایم.


## کوئری ۶ (بر اساس همه افراد)
<div dir="ltr">

```sql
select email
from users u
         left join payments p on p.username = u.username
group by u.username
having sum(COALESCE(p.amount_paid, 0)) > (select avg(total_paid)
                                          from (select sum(coalesce(p2.amount_paid, 0)) as total_paid
                                                from users u2
                                                         left join payments p2 on u2.username = p2.username
                                                group by u2.username));
```
<div dir="rtl">

### توضیح:
 ایمیل کاربرانی که مجموع پرداخت‌هاشون از میانگین کل کاربران بیشتره.  
چرا users: برای گرفتن ایمیل.  
چرا payments: برای محاسبه پرداخت‌ها.  
چرا LEFT JOIN: برای شامل کردن کاربران بدون پرداخت.

## کوئری ۷
<div dir="ltr">

```sql
select count(r.reservation_id), v.vehicle_type as type
from reservations r
         join tickets t
              on t.ticket_id = r.ticket_id
         join vehicles v
              on v.vehicle_id = t.vehicle_id
where r.reservation_status = 'RESERVED'
group by v.vehicle_type;
```
<div dir="rtl">

### توضیح:
 تعداد بلیط‌های فروخته‌شده برای هر نوع وسیله نقلیه.  
چرا reservations: برای شمارش رزروهای فعال.  
چرا tickets: برای اتصال رزروها به وسایل نقلیه.  
چرا vehicles: برای گرفتن نوع وسیله نقلیه.


## کوئری ۸
<div dir="ltr">

```sql
select name, count(rh.reservation_id) as count_of_reservation
from users u
         join reservations_history rh on rh.username = u.username
where DATE (rh.date_and_time) >= CURRENT_DATE - interval '7 days'
group by u.username
order by count (rh.reservation_id) desc limit 3;
```
<div dir="rtl">


### توضیح:
 نام ۳ کاربر با بیشترین خرید بلیط در هفته اخیر.  
چرا users: برای گرفتن نام کاربر.  
چرا reservations_history: برای شمارش رزروهای اخیر.  
چرا INNER JOIN: برای اتصال کاربران به رزروها.



## کوئری ۹
<div dir="ltr">

```sql
select l.city, count(r.reservation_id)
from reservations_history rh
         join reservations r on r.reservation_id = rh.reservation_id
         join tickets t on t.ticket_id = r.ticket_id
         join locations l on l.location_id = t.origin_location_id
where l.province = 'Tehran'
  and rh.reservation_history_status = 'SUCCESSFUL'
  and rh.operation_type = 'BUY'
group by l.city;
```
<div dir="rtl">

### توضیح:
 تعداد بلیط‌های فروخته‌شده در تهران به تفکیک شهر.  
چرا reservations_history: برای فیلتر خریدهای موفق.  
چرا reservations: برای اتصال به بلیط‌ها.  
چرا tickets و locations: برای گرفتن شهرهای مبدا.

## کوئری ۱۰
<div dir="ltr">

```sql
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
```
<div dir="rtl">

### توضیح:
 شهرهایی که قدیمی‌ترین کاربر ازشون بلیط خریده.  
چرا users: برای گرفتن قدیمی‌ترین کاربر.  
چرا reservations و reservations_history: برای پیدا کردن خریدها.  
چرا tickets و locations: برای گرفتن شهرهای مبدا.

## کوئری ۱۱
<div dir="lTR">

```sql
select u.name
from users u
where u.user_role = 'ADMIN';
```
<div dir="rtl">

### توضیح:
 نام پشتیبان‌های سایت.  
چرا users: برای گرفتن نام و نقش کاربران.  
چرا WHERE: برای فیلتر کردن ادمین‌ها.

## کوئری ۱۲
<div dir="ltr">

```sql
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
```
<div dir="rtl">


### توضیح:
 نام کاربرانی که حداقل ۲ بلیط خریدن.  
چرا users: برای گرفتن نام کاربر.  
چرا reservations_history: برای شمارش خریدهای موفق.  
چرا INNER JOIN: برای اتصال کاربران به خریدهای چندگانه.


## کوئری ۱۳
<div dir="ltr">

```sql
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
```

<div dir="rtl">

### توضیح:
 نام کاربرانی که حداکثر ۲ بلیط از یه وسیله نقلیه خریدن.  
چرا users: برای فیلتر کاربران USER.  
چرا reservations_history و reservations: برای پیدا کردن خریدهای موفق.  
چرا tickets و vehicles: برای گرفتن نوع وسیله نقلیه.

## کوئری ۱۴
<div dir="ltr">

```sql
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
```
<div dir="rtl">

### توضیح:
 یوزرنیم کاربرانی که از حداقل ۳ نوع وسیله نقلیه بلیط خریدن.  
چرا reservations_history: برای فیلتر خریدهای موفق.  
چرا reservations و tickets: برای اتصال به وسایل نقلیه.  
چرا vehicles: برای شمارش انواع وسایل نقلیه.

## کوئری ۱۵
<div dir="ltr">

```sql
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
```
<div dir="rtl">

### توضیح:
 اطلاعات بلیط‌های خریداری‌شده امروز به ترتیب ساعت خرید.  
چرا reservations_history: برای فیلتر خریدهای امروز.  
چرا reservations و tickets: برای گرفتن جزئیات بلیط.  
چرا users و locations: برای نام کاربر و شهرها.


## کوئری ۱۶ (بر اساس تعداد)
<div dir="ltr">

```sql
select t.ticket_id, count(r.reservation_id) as res_count
from tickets t
         join reservations r on t.ticket_id = r.ticket_id
where r.reservation_status = 'RESERVED'
group by t.ticket_id
order by res_count desc limit 1
offset 1;
```
<div dir="rtl">

### توضیح:
 دومین بلیط پر فروش بر اساس تعداد رزرو.  
چرا tickets: برای گرفتن شناسه بلیط.  
چرا reservations: برای شمارش رزروها.  
چرا INNER JOIN: برای اتصال بلیط‌ها به رزروها.

## کوئری ۱۶ (بر اساس درصد)
<div dir="rtl">

```sql
select t.ticket_id, (t.total_capacity - t.remaining_capacity) * 100 / t.total_capacity as buy_percentage
from tickets t
order by buy_percentage desc
offset 1 limit 1;
```
<div dir="rtl">

### توضیح:
 دومین بلیط پر فروش بر اساس درصد فروش.  
چرا tickets: برای محاسبه درصد فروش بلیط.  
چرا بدون JOIN: اطلاعات ظرفیت مستقیم در tickets موجوده.

## کوئری ۱۷
<div dir="ltr">

```sql
SELECT u.username AS admin_username,
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
```
<div dir="rtl">

### توضیح:
 نام ادمینی با بالاترین درصد لغو رزروها.  
چرا users: برای فیلتر ادمین‌ها.  
چرا requests: برای شمارش درخواست‌های لغو.  
چرا INNER JOIN: برای اتصال ادمین‌ها به درخواست‌ها.

## کوئری ۱۸
<div dir="ltr">

```sql
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
```
<div dir="rtl">

### توضیح:
 تغییر نام خانوادگی کاربری با بیشترین بلیط کنسل‌شده به ردینگتون.  
چرا users: برای آپدیت نام کاربر.  
چرا reservations_history: برای شمارش کنسلی‌ها.  
چرا INNER JOIN: برای اتصال کاربران به کنسلی‌ها.

## کوئری ۱۹
<div dir="ltr">

```sql
delete
from reservations
where username = (SELECT u.username
                  from users u
                           JOIN reservations_history rh ON rh.username = u.username
                  WHERE rh.operation_type = 'CANCEL'
                    AND rh.reservation_history_status = 'CANCELED'
                    and u.name = 'ridingtone' limit 1
    );
```
<div dir="rtl">

### توضیح:
 حذف بلیط‌های کنسل‌شده کاربر ردینگتون.  
چرا reservations: برای حذف رزروها.  
چرا users: برای فیلتر کاربر ردینگتون.  
چرا reservations_history: برای پیدا کردن کنسلی‌ها.

## کوئری ۲۰
<div dir="ltr">

```sql
update reservations
set reservation_status           = 'NOT_RESERVED',
    username                     = null,
    date_and_time_of_reservation = null
where reservation_id in (select r.reservation_id
                         from reservations r
                         where r.reservation_status = 'TEMPORARY'
                           and current_timestamp - r.date_and_time_of_reservation > interval '10 minutes'
    );
```
<div dir="rtl">

### توضیح:
 آزادسازی رزروهای موقت قدیمی‌تر از ۱۰ دقیقه.  
چرا reservations: برای آپدیت رزروها.  
چرا WHERE و زیرکوئری: برای فیلتر رزروهای موقت.

## کوئری ۲۱
<div dir="ltr">

```sql
update tickets
set price = price * 90 / 100
where ticket_id in (select t.ticket_id
                    from tickets t
                             join flights f on t.vehicle_id = f.vehicle_id
                    where f.airline_name = 'Mahan Air');
```
<div dir="rtl">

### توضیح:
 کاهش ۱۰٪ قیمت بلیط‌های شرکت ماهان.  
چرا tickets: برای آپدیت قیمت بلیط‌ها.  
چرا flights: برای فیلتر بلیط‌های ماهان.  
چرا INNER JOIN: برای اتصال بلیط‌ها به پروازها.

## کوئری ۲۲
<div dir="ltr">

```sql
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
```
<div dir="rtl">

### توضیح:
 نوع و تعداد گزارش‌ها برای بلیط با بیشترین گزارش.  
چرا reports: برای گرفتن نوع گزارش‌ها.  
چرا reservations: برای اتصال گزارش‌ها به بلیط‌ها.  
چرا tickets: برای شناسایی بلیط با بیشترین گزارش.


## پروسیجر ها

## پروسیجر ۱
<div dir="ltr">

```sql
CREATE OR REPLACE PROCEDURE get_user_ticket(
    input_email VARCHAR,
    input_phone_number VARCHAR,
    inout res refcursor
)
LANGUAGE PLPGSQL
AS $$
DECLARE
    user_name_ VARCHAR;
BEGIN
    SELECT username
    INTO user_name_
    FROM users
    WHERE email = input_email
       OR phone_number = input_phone_number;

    OPEN res FOR
    SELECT r.reservation_id,
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
END;
$$;

BEGIN;
CALL get_user_ticket('mehdi.shariati@email.com', NULL, 'my_table');
FETCH ALL my_table;
CLOSE my_table;
COMMIT;
```
<div dir="rtl">

### توضیح:
 گرفتن اطلاعات بلیط‌های رزروشده یه کاربر با ایمیل یا شماره تلفن.  
چرا users: برای پیدا کردن یوزرنیم با ایمیل یا شماره.  
چرا reservations و tickets: برای گرفتن جزئیات رزرو و بلیط.  
چرا locations: برای گرفتن شهرهای مبدا و مقصد.  
چرا refcursor: برای برگردوندن نتیجه به‌صورت جدول.


## پروسیجر ۲

<div dir="ltr">

```sql
CREATE OR REPLACE PROCEDURE get_user_have_cancelation(
    input_email VARCHAR,
    input_phone_number VARCHAR,
    inout res refcursor
)
LANGUAGE PLPGSQL
AS $$  
DECLARE
    user_name_ VARCHAR;
BEGIN
    SELECT username
    INTO user_name_
    FROM users
    WHERE email = input_email
       OR phone_number = input_phone_number;

    OPEN res FOR
    SELECT DISTINCT u.name
    FROM users u
             JOIN reservations_history rh ON rh.username = u.username
    WHERE rh.cancel_by = user_name_;
END;
  $$;

BEGIN;
CALL get_user_have_cancelation('admin1@email.com', NULL, 'my_table');
FETCH ALL my_table;
CLOSE my_table;
COMMIT;
```
<div dir="rtl">

### توضیح:
 گرفتن نام کاربرانی که رزروشون توسط کاربر خاصی لغو شده.  
چرا users: برای پیدا کردن یوزرنیم و نام.  
چرا reservations_history: برای گرفتن لغوهای انجام‌شده.  
چرا INNER JOIN: برای اتصال کاربران به لغوها.  
چرا refcursor: برای برگردوندن نتیجه به‌صورت جدول.

## پروسیجر ۳
<div dir="ltr">

```sql
CREATE OR REPLACE PROCEDURE get_reservation_in_city(
    input_city VARCHAR,
    inout res refcursor
)
LANGUAGE PLPGSQL
AS $$  
DECLARE
    location_id_ INTEGER;
BEGIN
    SELECT location_id
    INTO location_id_
    FROM locations
    WHERE city = input_city;

    OPEN res FOR
    SELECT r.reservation_id,
           r.ticket_id,
           l1.city AS origin_city,
           l2.city AS destination_city,
           t.departure_start,
           r.date_and_time_of_reservation
    FROM reservations r
             JOIN tickets t ON r.ticket_id = t.ticket_id
             JOIN locations l1 ON t.origin_location_id = l1.location_id
             JOIN locations l2 ON t.destination_location_id = l2.location_id
    WHERE t.origin_location_id = location_id_
      AND r.reservation_status = 'RESERVED'
    ORDER BY r.date_and_time_of_reservation DESC;
END;
  $$;

BEGIN;
CALL get_reservation_in_city('Mashhad', 'my_table');
FETCH ALL my_table;
CLOSE my_table;
COMMIT;
```
<div dir="rtl">

### توضیح:
 گرفتن اطلاعات رزروهای شهر خاص.  
چرا locations: برای پیدا کردن شناسه شهر.  
چرا reservations و tickets: برای جزئیات رزرو و بلیط.  
چرا INNER JOIN: برای اتصال رزروها به شهرها.  
چرا refcursor: برای برگردوندن نتیجه به‌صورت جدول.

## پروسیجر ۴
<div dir="ltr">

```sql
CREATE OR REPLACE PROCEDURE search_tickets_by_term(
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
           u.name AS passenger_name,
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
             LEFT JOIN flights f ON t.vehicle_id = f.vehicle_id
             LEFT JOIN buses b ON t.vehicle_id = b.vehicle_id
    WHERE r.reservation_status = 'RESERVED'
      AND (
            u.name ILIKE '%' || input_term || '%'
            OR l1.city ILIKE '%' || input_term || '%'
            OR l2.city ILIKE '%' || input_term || '%'
            OR f.flight_class ILIKE '%' || input_term || '%'
            OR b.company_name ILIKE '%' || input_term || '%'
        );
END;
  $$;

BEGIN;
CALL search_tickets_by_term('ab', 'my_table');
FETCH ALL my_table;
CLOSE my_table;
COMMIT;
```
<div dir="rtl">

### توضیح:
 جستجوی بلیط‌ها بر اساس عبارت در نام، شهرها، کلاس پرواز یا شرکت اتوبوس.  
چرا reservations: برای گرفتن رزروهای فعال.  
چرا users، tickets، locations: برای جزئیات کاربر و شهرها.  
چرا LEFT JOIN: برای شامل کردن پروازها و اتوبوس‌ها.  
چرا refcursor: برای برگردوندن نتیجه به‌صورت جدول.

## پروسیجر ۵
<div dir="ltr">

```sql
CREATE OR REPLACE PROCEDURE get_user_in_city(
    input_email VARCHAR,
    input_phone_number VARCHAR,
    INOUT res refcursor
)
LANGUAGE PLPGSQL
AS $$  
DECLARE
    location_ INTEGER;
BEGIN
    SELECT city
    INTO location_
    FROM users
    WHERE email = input_email
       OR phone_number = input_phone_number;

    OPEN res FOR
    SELECT u.username,
           u.name,
           u.email,
           u.phone_number,
           u.date_of_sign_in,
           l.city
    FROM users u
             JOIN locations l ON l.location_id = u.city
    WHERE l.location_id = location_;
END;
  $$;

BEGIN;
CALL get_user_in_city(NULL, '09121112233', 'my_table');
FETCH ALL my_table;
CLOSE my_table;
COMMIT;
```
<div dir="rtl">

### توضیح:
 گرفتن اطلاعات کاربران یک شهر با ایمیل یا شماره تلفن.  
چرا users: برای پیدا کردن شهر کاربر و اطلاعاتش.  
چرا locations: برای گرفتن نام شهر.  
چرا INNER JOIN: برای اتصال کاربران به شهرها.  
چرا refcursor: برای برگردوندن نتیجه به‌صورت جدول.


## پروسیجر ۶
<div dir="ltr">

```sql
CREATE OR REPLACE PROCEDURE get_top_user_by_buy_ticket(
    input_date DATE,
    input_n INTEGER,
    INOUT res refcursor
)
LANGUAGE PLPGSQL
AS $$  
BEGIN
    OPEN res FOR
    SELECT u.username,
           u.name,
           u.email,
           COUNT(r.reservation_id) AS reservation_count
    FROM users u
             LEFT JOIN reservations r ON u.username = r.username
    WHERE r.reservation_status = 'RESERVED'
      AND DATE(r.date_and_time_of_reservation) >= input_date
    GROUP BY u.username
    ORDER BY reservation_count DESC, u.username
    LIMIT input_n;
END;
  $$;

BEGIN;
CALL get_top_user_by_buy_ticket('2025-03-10', 5, 'my_table');
FETCH ALL my_table;
CLOSE my_table;
COMMIT;
```
<div dir="rtl">

### توضیح:
 گرفتن N کاربر برتر بر اساس تعداد رزرو بلیط از تاریخ مشخص.  
چرا users: برای اطلاعات کاربران.  
چرا reservations: برای شمارش رزروها.  
چرا LEFT JOIN: برای شامل کردن کاربران بدون رزرو.  
چرا refcursor: برای برگردوندن نتیجه به‌صورت جدول.

## پروسیجر ۷
<div dir="ltr">

```sql
CREATE OR REPLACE PROCEDURE get_canceled_tickets_by_vehicle_type(
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
           l1.city AS origin_city,
           l2.city AS destination_city,
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

BEGIN;
CALL get_canceled_tickets_by_vehicle_type('BUS', 'my_table');
FETCH ALL my_table;
CLOSE my_table;
COMMIT;
```
<div dir="rtl">

### توضیح:
 گرفتن اطلاعات بلیط‌های کنسل‌شده برای نوع وسیله نقلیه خاص.  
چرا reservations_history: برای فیلتر کنسلی‌ها.  
چرا reservations، tickets، vehicles: برای جزئیات بلیط و وسیله.  
چرا locations: برای شهرهای مبدا و مقصد.  
چرا refcursor: برای برگردوندن نتیجه به‌صورت جدول.

## پروسیجر ۸
<div dir="ltr">

```sql
CREATE OR REPLACE PROCEDURE get_top_users_by_report_subject(
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

BEGIN;
CALL get_top_users_by_report_subject('PAYMENT', 'my_table');
FETCH ALL my_table;
CLOSE my_table;
COMMIT;
```
<div dir="rtl">

### توضیح:
 گرفتن کاربران برتر بر اساس تعداد گزارش‌های یه موضوع خاص.  
چرا users: برای اطلاعات کاربران.  
چرا reports: برای شمارش گزارش‌ها.  
چرا LEFT JOIN: برای شامل کردن کاربران بدون گزارش.  
چرا refcursor: برای برگردوندن نتیجه به‌صورت جدول.

# فاز 3 پروژه
این پروژه یک برنامه بک‌اند مبتنی بر جنگو برای یک سیستم خرید بلیط است که از PostgreSQL به عنوان پایگاه داده اصلی و Redis برای کشینگ و مدیریت OTP استفاده می‌کند. Celery نیز برای وظایف ناهمگام به کار گرفته شده است.

## 1. نحوه راه‌اندازی و اجرای سرور بک‌اند

برای راه‌اندازی و اجرای سرور بک‌اند، مراحل زیر را دنبال کنید:

### پیش‌نیازها

* Docker و Docker Compose نصب شده باشند.
* (اختیاری، برای توسعه محلی پایتون) پایتون 3.9+ و `pip`.

### مراحل راه‌اندازی

1.  **کلون کردن مخزن:**
    ```bash
    git clone <your-repository-url>
    cd db-project-phase3
    ```

2.  **ساخت و اجرای کانتینرهای Docker:**
    این دستور ایمیج‌های Docker را برای برنامه وب و Celery worker شما می‌سازد و تمام سرویس‌های تعریف شده در `docker-compose.yml` (web, db, redis, celery) را راه‌اندازی می‌کند.
    ```bash
    docker-compose up --build -d
    ```
    * `--build`: قبل از شروع کانتینرها، ایمیج‌ها را می‌سازد (برای اولین اجرا یا در صورت تغییر `Dockerfile` لازم است).
    * `-d`: کانتینرها را در حالت جدا (در پس‌زمینه) اجرا می‌کند.

3.  **اعمال مایگریشن‌های پایگاه داده:**
    هنگامی که سرویس `db` سالم شد، مایگریشن‌های جنگو را اعمال کنید. باید این دستور را درون کانتینر `web` اجرا کنید.
    ```bash
    docker-compose exec web python manage.py migrate
    ```

4.  **بارگذاری داده‌های اولیه (اختیاری اما برای تست توصیه می‌شود):**
    اگر فایل `dummy_data.sql` با داده‌های اولیه دارید، می‌توانید آن را در کانتینر PostgreSQL خود بارگذاری کنید.
    ```bash
    docker-compose exec db psql -U postgres -d mydatabase -f /code/dummy_data.sql
    ```
    (توجه: مسیر `psql` و آرگومان‌ها ممکن است بسته به ایمیج PostgreSQL شما کمی متفاوت باشد. `/code/dummy_data.sql` فرض می‌کند `dummy_data.sql` در ریشه پروژه شما است و طبق `docker-compose.yml` به `/code` درون کانتینر mount شده است).

5.  **ایجاد یک سوپریوزر (اختیاری، برای دسترسی به پنل ادمین جنگو):**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    برای ایجاد یک کاربر ادمین، دستورات را دنبال کنید.

### دسترسی به سرور

سرور بک‌اند جنگو در آدرس `http://localhost:8000` اجرا خواهد شد.

* **پنل ادمین جنگو:** `http://localhost:8000/admin/`
* **مستندات API (Swagger UI):** `http://localhost:8000/api/docs/`
* **نوار ابزار دیباگ:** در صورت `True` بودن `DEBUG` در `settings.py` قابل دسترسی است (که به طور پیش‌فرض در حالت توسعه `True` است).

### توقف سرور

برای توقف تمام کانتینرهای Docker در حال اجرا:
```bash
docker-compose down
```
## 2. نحوه اتصال به پایگاه داده و تنظیمات Redis
این پروژه از PostgreSQL برای ذخیره‌سازی داده‌های پایدار و از Redis برای کشینگ (پروفایل‌های کاربر، نتایج جستجوی بلیط) و مدیریت OTP استفاده می‌کند.

### پیکربندی PostgreSQL
* نام سرویس: db

* ایمیج: postgres:17-alpine

* نام پایگاه داده: mydatabase

* کاربر: postgres

* رمز عبور: 1234 

* نگاشت پورت: 5433:5432 (هاست:کانتینر)

* ولوم داده: postgres_data (برای داده‌های پایدار)

* pg_hba.conf: فایل pg_hba.conf برای اجازه اتصال از تمام هاست‌ها (0.0.0.0/0 و ::/0) با استفاده از متد trust mount شده است که تنظیمات توسعه محلی را ساده می‌کند. توجه: در محیط تولید، این باید با متدهای احراز هویت محدودکننده‌تر پیکربندی شود.

## بخش مربوطه در docker-compose.yml
```bash
db:
  image: postgres:17-alpine
  restart: always
  container_name: mydatabase
  environment:
    - POSTGRES_USER=postgres
    - POSTGRES_DB=mydatabase
    - POSTGRES_PASSWORD=1234
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./pg_hba.conf:/etc/postgresql/pg_hba.conf
  ports:
    - "5433:5432"
  command: ["postgres", "-c", "hba_file=/etc/postgresql/pg_hba.conf"]
  ```

خود فایل pg_hba.conf شامل موارد زیر است:

## TYPE  DATABASE        USER            ADDRESS                 METHOD
```bash
local   all             all                                     trust
host    all             all             0.0.0.0/0               trust
host    all             all             ::/0                    trust
```
## پیکربندی Redis
* نام سرویس: redis

* ایمیج: redis:7-alpine

* نگاشت پورت: 6379:6379 (هاست:کانتینر)

* ولوم داده: redis_data (برای داده‌های پایدار، هرچند Redis در اینجا عمدتاً به عنوان کش استفاده می‌شود)


## بخش مربوطه در docker-compose.yml
```
redis:
  image: redis:7-alpine
  container_name: myredis
  restart: always
  ports:
     "6379:6379"
  volumes:
     redis_data:/data
```
## تنظیمات جنگو
فایل config/settings.py پارامترهای اتصال برای PostgreSQL و Redis را تعریف می‌کند و مقادیر را از متغیرهای محیطی تنظیم شده در docker-compose.yml می‌گیرد.

## بخش مربوطه در config/settings.py
```
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'mydatabase'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', 5432),
    }
}

CELERY_BROKER_URL = 'redis://redis:6379/0'
```
## 3. لیست تمام APIها و توضیحات ورودی/خروجی
این بخش نقاط پایانی API موجود، متدهای HTTP آن‌ها، بدنه درخواست مورد انتظار (JSON) و پاسخ‌های معمول را تشریح می‌کند.

URL پایه برای تمام نقاط پایانی API: http://localhost:8000/api-test/

### 1. درخواست OTP
* URL: request-otp/
* متد: POST
* توضیحات: فرآیند ورود مبتنی بر OTP را برای یک کاربر موجود و فعال با ارسال OTP به ایمیل یا شماره تلفن آن‌ها آغاز می‌کند.
### مثال بدنه درخواست:
```
{
    "identifier": "user@example.com"
}
// یا
{
    "identifier": "09123456789"
}
```
### پاسخ موفقیت‌آمیز (200 OK):
```
{
    "status": "success",
    "message": "یک OTP برای {identifier} جهت ورود ارسال شده است. این کد برای 5 دقیقه معتبر است."
}
```
### پاسخ‌های خطا (مثال‌ها):
* 400 Bad Request: {"status": "error", "message": "شناسه (ایمیل یا شماره تلفن) الزامی است."}
* 403 Forbidden: {"status": "error", "message": "حساب کاربری شما در حال حاضر غیرفعال است. لطفا با پشتیبانی تماس بگیرید."}
* 404 Not Found: {"status": "error", "message": "کاربر یافت نشد. لطفا ثبت نام کنید یا شناسه خود را بررسی کنید."}
* 429 Too Many Requests: {"status": "error", "message": "یک OTP قبلاً به این شناسه ارسال شده است..."}
* 503 Service Unavailable: {"status": "error", "message": "سرویس Redis در دسترس نیست. امکان درخواست OTP وجود ندارد."}
## 2. تایید OTP
* URL: verify-otp/
* متد: POST
* توضیحات: کد OTP ارائه شده را برای ورود تایید می‌کند و در صورت موفقیت، توکن‌های JWT را برمی‌گرداند.
### مثال بدنه درخواست:
```
{
    "identifier": "user@example.com",
    "otp_code": "123456"
}
```
### پاسخ موفقیت‌آمیز (200 OK):
```
{
    "status": "success",
    "message": "ورود موفقیت‌آمیز بود! OTP تایید شد.",
    "access_token": "<JWT_access_token_string>",
    "refresh_token": "<JWT_refresh_token_string>",
    "user_info": {
        "username": "<نام کاربری>",
        "name": "<نام کاربر یا null>",
        "email": "<ایمیل کاربر یا null>",
        "phone_number": "<شماره تلفن کاربر یا null>",
        "role": "<نقش کاربر>"
    }
}
```
### پاسخ‌های خطا (مثال‌ها):
* 400 Bad Request: {"status": "error", "message": "کد OTP نامعتبر است."}
* 404 Not Found: {"status": "error", "message": "کاربر یافت نشد، با وجود OTP معتبر. لطفا با پشتیبانی تماس بگیرید."}
* 503 Service Unavailable: {"status": "error", "message": "سرویس Redis در دسترس نیست. امکان تایید OTP وجود ندارد."}
## 3. ثبت نام کاربر
URL: user-signup/

متد: POST

توضیحات: یک کاربر جدید را در سیستم ثبت نام می‌کند.

### مثال بدنه درخواست:
```
{
    "username": "newuser",
    "password": "SecurePassword123!",
    "email": "user@example.com",
    "name": "Test User",
    "phone_number": "09123456789" // اختیاری
}
```
### پاسخ موفقیت‌آمیز (201 Created):
```
{
    "status": "success",
    "message": "کاربر با موفقیت ثبت نام شد!",
    "access_token": "<JWT_access_token_string>",
    "refresh_token": "<JWT_refresh_token_string>",
    "user_info": {
        "username": "newuser",
        "email": "user@example.com",
        "name": "Test User",
        "role": "USER"
    }
}
```
### پاسخ‌های خطا (مثال‌ها):
* 400 Bad Request: {"status": "error", "message": "فیلدهای الزامی از دست رفته: [نام فیلدها]"}
* 409 Conflict: {"status": "error", "message": "این نام کاربری قبلاً گرفته شده است. لطفا نام دیگری را انتخاب کنید."}
## 4. به‌روزرسانی پروفایل کاربر  
**URL:** `user-update-profile/`  
**متد:** `PATCH`  

**توضیحات:**  
به یک کاربر احراز هویت‌شده اجازه می‌دهد تا جزئیات پروفایل خود را به‌روزرسانی کند. این جزئیات می‌توانند شامل نام، نام کاربری، ایمیل، رمز عبور، شماره تلفن، تاریخ تولد، شناسه شهر، روش احراز هویت، و افزایش موجودی کیف پول باشند.

**احراز هویت:**  
ارسال توکن `Bearer` در هدر درخواست الزامی است.

---

### مثال بدنه درخواست:
```json
{
    "name": "New Full Name",
    "new_username": "new_unique_username123",
    "new_password": "aVeryStrongPassword!@#",
    "new_email": "new.email.unique@example.com",
    "phone_number": "09123456780",
    "date_of_birth": "1990-01-01",
    "city_id": 10,
    "new_authentication_method": "PHONE_NUMBER",
    "add_to_wallet_balance": 50000
}
```

---

### پاسخ موفقیت‌آمیز (200 OK):
```json
{
    "status": "success",
    "message": "پروفایل با موفقیت به‌روزرسانی شد.",
    "access_token": "<new_jwt_access_token_if_needed>",
    "refresh_token": "<new_jwt_refresh_token_if_needed>",
    "user_info": {
        "username": "current_or_new_username",
        "name": "New Full Name",
        "email": "current_or_new_email@example.com",
        "phone_number": "09123456780",
        "date_of_birth": "1990-01-01",
        "city_id": 10,
        "authentication_method": "PHONE_NUMBER",
        "role": "USER",
        "wallet_balance": 1500000
    }
}
```

---

### پاسخ‌های خطا (مثال‌ها):

- **400 Bad Request**:  
  ```json
  {"status": "error", "message": "نام نمی‌تواند خالی یا null باشد."}
  ```

- **401 Unauthorized**:  
  توکن از دست رفته یا نامعتبر است.

- **409 Conflict**:  
  ```json
  {"status": "error", "message": "این نام کاربری قبلاً گرفته شده است."}
  ```

# API مستندات سامانه بلیط

## 5. دریافت لیست شهرها

- **URL:** `cities-list/`
- **Method:** GET
- **Description:** لیستی از تمام شهرها و استان‌های موجود در سیستم را بازیابی می‌کند.

###  پاسخ موفقیت‌آمیز (200 OK)
```json
{
    "status": "success",
    "data": [
        {
            "location_id": 1,
            "city": "Tehran",
            "province": "Tehran"
        },
        {
            "location_id": 2,
            "city": "Mashhad",
            "province": "Razavi Khorasan"
        }
    ]
}
```

###  پاسخ‌های خطا
- **500 Internal Server Error**
```json
{"status": "error", "message": "خطای پایگاه داده هنگام دریافت شهرها رخ داد."}
```

---

## 6. جستجوی بلیط‌ها

- **URL:** `search-tickets/`
- **Method:** POST
- **Description:** جستجوی بلیط با فیلترهای مختلف

###  بدنه درخواست
```json
{
    "origin_city": "Tehran",
    "destination_city": "Mashhad",
    "departure_date": "2025-06-15",
    "vehicle_type": "FLIGHT",
    "min_price": 100000,
    "max_price": 500000,
    "company_name": "Mahan Air",
    "min_departure_time": "08:00",
    "max_departure_time": "18:00",
    "flight_class": "Economy",
    "train_stars": 4,
    "bus_type": "VIP"
}
```

###  پاسخ موفقیت‌آمیز (200 OK)
```json
{
    "status": "success",
    "data": [
        {
            "ticket_id": 1,
            "origin_city": "Tehran",
            "destination_city": "Mashhad",
            "departure_start": "YYYY-MM-DDTHH:MM:SS",
            "departure_end": "YYYY-MM-DDTHH:MM:SS",
            "price": 500000,
            "remaining_capacity": 20,
            "vehicle_type": "FLIGHT",
            "vehicle_details": {
                "airline_name": "Mahan Air",
                "flight_class": "Economy",
                "number_of_stop": 0,
                "flight_code": "IR-1234",
                "origin_airport": "Mehrabad",
                "destination_airport": "Mashhad",
                "facility": {"meal": true}
            }
        }
    ],
    "cached": true
}
```

###  پاسخ‌های خطا
```json
{"status": "error", "message": "پارامترهای الزامی از دست رفته: origin_city, destination_city, departure_date"}
{"status": "error", "message": "فرمت departure_date نامعتبر است. لطفا از فرمت YYYY-MM-DD استفاده کنید."}
```

---

## 7. دریافت جزئیات بلیط

- **URL:** `ticket-details/<int:ticket_id>/`
- **Method:** GET
- **Description:** اطلاعات کامل بلیط

###  پاسخ موفقیت‌آمیز (200 OK)
```json
{
    "status": "success",
    "data": {
        "ticket_id": 1,
        "departure_start": "YYYY-MM-DDTHH:MM:SSZ",
        "departure_end": "YYYY-MM-DDTHH:MM:SSZ",
        "price": 500000,
        "total_capacity": 50,
        "remaining_capacity": 25,
        "ticket_status": true,
        "is_round_trip": false,
        "return_start": null,
        "return_end": null,
        "origin_city": "Tehran",
        "origin_province": "Tehran",
        "destination_city": "Mashhad",
        "destination_province": "Razavi Khorasan",
        "vehicle_type": "TRAIN",
        "vehicle_details": {},
        "reservations": [
            {
                "reservation_id": 101,
                "reservation_status": "TEMPORARY",
                "reservation_seat": 5
            }
        ]
    }
}
```

###  پاسخ‌های خطا
```json
{"status": "error", "message": "بلیط یافت نشد."}
```

---

## 8. رزرو بلیط

- **URL:** `reserve-ticket/`
- **Method:** POST
- **Authentication:** Bearer Token (USER role)
- **Description:** رزرو موقت یک صندلی

###  بدنه درخواست
```json
{
    "ticket_id": 123,
    "seat_number": 5
}
```

###  پاسخ موفقیت‌آمیز (200 OK)
```json
{
    "status": "success",
    "message": "صندلی با موفقیت به صورت موقت رزرو شد. بررسی انقضا برنامه‌ریزی شد.",
    "reservation": {
        "reservation_id": 101,
        "ticket_id": 123,
        "seat_number": 5,
        "status": "TEMPORARY",
        "username": "currentuser",
        "reserved_at": "YYYY-MM-DDTHH:MM:SS.ffffffZ",
        "expires_in_minutes": 10
    }
}
```

###  پاسخ‌های خطا
```json
{"status": "error", "message": "ممنوع: فقط کاربران عادی می‌توانند بلیط رزرو کنند."}
{"status": "error", "message": "امکان رزرو بلیط برای سفری که قبلاً شروع شده یا گذشته است وجود ندارد."}
{"status": "error", "message": "ظرفیت باقی‌مانده برای بلیط با شناسه {id} وجود ندارد."}
```

---

## 9. لغو رزرو (بررسی سیاست)

- **URL:** `reservations/<int:reservation_id>/cancel/`
- **Method:** GET
- **Authentication:** Bearer Token

###  پاسخ موفقیت‌آمیز (200 OK)
```json
{
    "status": "success",
    "cancellation_info": {
        "reservation_id": 101,
        "ticket_price": 500000,
        "time_to_departure_hours": 25.5,
        "penalty_percentage": 10,
        "penalty_amount": 50000,
        "refund_amount": 450000
    }
}
```

###  پاسخ‌های خطا
```json
{"status": "error", "message": "ممنوع: شما فقط می‌توانید رزروهای خود را بررسی کنید."}
{"status": "error", "message": "رزرو نمی‌تواند لغو شود. وضعیت فعلی: {status}"}
```

---

## 10. ایجاد درخواست (لغو یا تغییر تاریخ)

- **URL:** `reservations/<int:reservation_id>/requests/`
- **Method:** POST
- **Authentication:** Bearer Token

###  بدنه درخواست
```json
{
    "request_subject": "CANCEL",
    "request_text": "من باید این سفر را به دلیل یک اورژانس خانوادگی لغو کنم."
}
```

###  پاسخ موفقیت‌آمیز (201 Created)
```json
{
    "status": "success",
    "message": "درخواست شما با موفقیت ارسال شد و در انتظار بررسی است.",
    "request_details": {
        "request_id": 1,
        "reservation_id": 101,
        "request_subject": "CANCEL",
        "request_text": "من باید این سفر را به دلیل یک اورژانس خانوادگی لغو کنم."
    }
}
```

###  پاسخ‌های خطا
```json
{"status": "error", "message": "هم 'request_subject' و هم 'request_text' الزامی هستند."}
{"status": "error", "message": "ممنوع: شما مالک این رزرو نیستید."}
{"status": "error", "message": "امکان ایجاد درخواست برای بلیطی که زمان حرکت آن گذشته است وجود ندارد."}
```

---

## 11. پرداخت بلیط‌ها

- **URL:** `pay-tickets/`
- **Method:** POST
- **Authentication:** Bearer Token

###  بدنه درخواست
```json
{
    "reservation_id": 101,
    "payment_method": "WALLET",
    "payment_status": "SUCCESSFUL"
}
```

### پاسخ موفقیت‌آمیز (200 OK)
```json
{
    "status": "success",
    "message": "پرداخت موفقیت‌آمیز بود. رزرو تایید شد.",
    "payment_details": {
        "payment_id": 1,
        "reservation_id": 101,
        "amount_paid": 500000,
        "payment_status": "SUCCESSFUL",
        "payment_method": "WALLET",
        "date_and_time_of_payment": "YYYY-MM-DDTHH:MM:SSZ"
    },
    "reservation_history": {
        "operation_type": "BUY",
        "history_status": "SUCCESSFUL",
        "date_and_time": "YYYY-MM-DDTHH:MM:SSZ"
    },
    "new_wallet_balance": 1500000
}
```

###  پاسخ‌های خطا
```json
{"status": "error", "message": "پرداخت ناموفق: موجودی کیف پول کافی نیست."}
{"status": "error", "message": "ممنوع: فقط کاربران عادی می‌توانند پرداخت انجام دهند."}
{"status": "error", "message": "رزرو موقت در Redis یافت نشد یا منقضی شده است."}
{"status": "error", "message": "وضعیت رزرو {status} است. فقط رزروهای TEMPORARY قابل پرداخت هستند."}
```

---


## 12. ادمین: دریافت رزروهای لغو شده

- **URL**: `admin/cancelled-reservations/`  
- **Method**: `POST`  
- **Authentication**: Bearer Token (فقط ادمین)  
- **Request Body (Optional)**:
```json
{
  "username": "user123",
  "ticket_id": 45
}
```
- **Response (200 OK)**:
```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "reservation_history_id": 1,
      "cancellation_time": "YYYY-MM-DDTHH:MM:SSZ",
      "canceled_by_user": "user123",
      "ticket_id": 45,
      "reservation_id": 101,
      "departure_start": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}
```

## 13. ادمین: دریافت لیست درخواست‌ها

- **URL**: `admin/requests/`  
- **Method**: `POST`  
- **Authentication**: Bearer Token (فقط ادمین)  
- **Request Body (Optional)**:
```json
{
  "username": "user123",
  "ticket_id": 45,
  "status": "PENDING"
}
```
- **Response (200 OK)**:
```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "request_id": 1,
      "username": "user123",
      "reservation_id": 101,
      "ticket_id": 45,
      "request_subject": "CANCEL",
      "request_text": "من باید این سفر را لغو کنم.",
      "requested_at": "YYYY-MM-DDTHH:MM:SSZ",
      "is_checked": false,
      "is_accepted": false
    }
  ]
}
```

## 14. ادمین: تایید درخواست

- **URL**: `admin/requests/<int:request_id>/approve/`  
- **Method**: `POST`  
- **Authentication**: Bearer Token (فقط ادمین)  
- **Request Body**: `{}`  
- **Response (200 OK)**:
```json
{
  "status": "success",
  "message": "لغو تایید شد. 450000 به کیف پول کاربر بازپرداخت شد."
}
```

## 15. ادمین: رد درخواست

- **URL**: `admin/requests/<int:request_id>/reject/`  
- **Method**: `POST`  
- **Authentication**: Bearer Token (فقط ادمین)  
- **Request Body**: `{}`  
- **Response (200 OK)**:
```json
{
  "status": "success",
  "message": "درخواست رد شد."
}
```

## 16. دریافت رزروهای کاربر

- **URL**: `user-bookings/`  
- **Method**: `POST`  
- **Authentication**: Bearer Token (کاربر عادی)  
- **Request Body (Optional)**:
```json
{
  "status": "RESERVED",
  "start_departure_date": "YYYY-MM-DD",
  "end_departure_date": "YYYY-MM-DD",
  "origin_city": "Tehran",
  "destination_city": "Mashhad",
  "ticket_id": 123,
  "reservation_id": 101,
  "operation_type": "BUY"
}
```
- **Response (200 OK)**:
```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "history_id": 1,
      "reservation_id": 101,
      "ticket_id": 123,
      "operation_type": "BUY",
      "operation_status": "SUCCESSFUL",
      "operation_time": "YYYY-MM-DDTHH:MM:SSZ",
      "ticket_details": {
        "origin_city": "Tehran",
        "destination_city": "Mashhad",
        "departure_start": "YYYY-MM-DDTHH:MM:SS"
      }
    }
  ]
}
```

## 17. گزارش مشکل

- **URL**: `report-issue/`  
- **Method**: `POST`  
- **Authentication**: Bearer Token (کاربر عادی)  
- **Request Body**:
```json
{
  "reservation_id": 123,
  "report_type": "PAYMENT",
  "report_text": "پرداخت من ناموفق بود اما بلیط همچنان به صورت موقت نمایش داده می‌شود."
}
```
- **Response (201 Created)**:
```json
{
  "status": "success",
  "message": "گزارش مشکل شما با موفقیت ارسال شد.",
  "report_details": {
    "report_id": 1,
    "reservation_id": 123,
    "username": "currentUser",
    "report_type": "PAYMENT",
    "report_text": "...",
    "report_status": "UNCHECKED"
  }
}
```

## 18. ادمین: مدیریت گزارش

- **URL**: `admin/reports/<int:report_id>/manage/`  
- **Method**: `PATCH`  
- **Authentication**: Bearer Token (ادمین)  
- **Request Body (Optional)**:
```json
{
  "admin_response": "ما گزارش شما را بررسی کرده‌ایم و به زودی اقدام خواهیم کرد."
}
```
- **Response (200 OK)**:
```json
{
  "status": "success",
  "message": "گزارش با موفقیت به‌روزرسانی شد.",
  "updated_report": {
    ...
  }
}
```

## 19. ادمین: دریافت گزارش‌ها

- **URL**: `admin/reports/`  
- **Method**: `POST`  
- **Authentication**: Bearer Token (ادمین)  
- **Request Body (Optional)**:
```json
{
  "username": "user123",
  "ticket_id": 501,
  "report_type": "PAYMENT",
  "report_status": "UNCHECKED",
  "reservation_id": 101
}
```
- **Response (200 OK)**:
```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "report_id": 1,
      "report_username": "user123",
      "reservation_id": 101,
      "ticket_id": 501,
      "report_type": "PAYMENT",
      "report_text": "...",
      "report_status": "UNCHECKED",
      "admin_response": null,
      "ticket_details": {
        "departure_start": "...",
        "departure_end": "...",
        "origin_city": "Tehran",
        "destination_city": "Mashhad"
      }
    }
  ]
}
```

# ۴. نحوه تست APIها با Postman

ما برای تست APIهای این پروژه از Postman استفاده کرده‌ایم. در اینجا یک مثال ساده برای شروع آمده است:

## تست API `user-signup` با Postman:

1. یک درخواست `POST`جدید ایجاد می  کنیم.
2. URL را به `http://localhost:8000/api-test/user-signup/` تنظیم می کنیم.
3. در تب **Body**، گزینه **raw** و سپس **JSON** را انتخاب می کنیم و JSON زیر را وارد می کنیم:

```json
{
    "username": "newuser",
    "password": "SecurePassword123!",
    "email": "user@example.com",
    "name": "Test User",
    "phone_number": "09123456789"
}
```
4. روی Send کلیک کنید.
### شما باید یک پاسخ 201 Created را مشاهده کنید که نشان‌دهنده موفقیت‌آمیز بودن ثبت نام کاربر است.











