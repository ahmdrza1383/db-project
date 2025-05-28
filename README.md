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
