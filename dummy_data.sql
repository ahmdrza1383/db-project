INSERT INTO locations (city, province) VALUES
('Tehran', 'Tehran'),
('Karaj', 'Tehran'),
('Varamin', 'Tehran'),
('Rey', 'Tehran'),
('Isfahan', 'Isfahan'),
('Shiraz', 'Fars'),
('Mashhad', 'Razavi Khorasan'),
('Tabriz', 'East Azerbaijan'),
('Ahvaz', 'Khuzestan'),
('Kermanshah', 'Kermanshah'),
('Rasht', 'Gilan'),
('Bandar Abbas', 'Hormozgan'),
('Yazd', 'Yazd'),
('Qom', 'Qom'),
('Kerman', 'Kerman'),
('Zahedan', 'Sistan and Baluchestan'),
('Arak', 'Markazi'),
('Hamedan', 'Hamedan'),
('Gorgan', 'Golestan'),
('Sanandaj', 'Kurdistan'),
('Qazvin', 'Qazvin'),
('Urmia', 'West Azerbaijan'),
('Zanjan', 'Zanjan'),
('Semnan', 'Semnan'),
('Bushehr', 'Bushehr'),
('Birjand', 'South Khorasan'),
('Bojnurd', 'North Khorasan'),
('Sari', 'Mazandaran'),
('Amol', 'Mazandaran'),
('Babol', 'Mazandaran'),
('Gachsaran', 'Kohgiluyeh and Boyer-Ahmad'),
('Ilam', 'Ilam'),
('Khorramabad', 'Lorestan'),
('Ardabil', 'Ardabil'),
('Chabahar', 'Sistan and Baluchestan'),
('Dezful', 'Khuzestan'),
('Borujerd', 'Lorestan'),
('Sabzevar', 'Razavi Khorasan'),
('Malayer', 'Hamedan'),
('Maragheh', 'East Azerbaijan'),
('Neyshabur', 'Razavi Khorasan'),
('Saveh', 'Markazi'),
('Shahrud', 'Semnan'),
('Torbat Heydarieh', 'Razavi Khorasan'),
('Ghoochan', 'Razavi Khorasan'),
('Kashmar', 'Razavi Khorasan'),
('Baft', 'Kerman'),
('Jiroft', 'Kerman');

-- افزودن کاربران با شماره تلفن‌های یکتا
INSERT INTO users (username, password, user_role, name, email, phone_number, city, authentication_method) VALUES
('ali123', 'hashed_password_1', 'USER', 'Ali Rezaei', 'ali.rezaei@email.com', '09121112233', 1, 'EMAIL'),
('sara456', 'hashed_password_2', 'USER', 'Sara Ahmadi', 'sara.ahmadi@email.com', '09134445566', 5, 'PHONE_NUMBER'),
('mohammad789', 'hashed_password_3', 'USER', 'Mohammad Hosseini', 'mohammad.hosseini@email.com', '09157778899', 7, 'EMAIL'),
('zahra101', 'hashed_password_4', 'USER', 'Zahra Karimzadeh', 'zahra.karimzadeh@email.com', '09160001122', 8, 'EMAIL'),
('reza202', 'hashed_password_5', 'USER', 'Reza Mohammadi', 'reza.mohammadi@email.com', '09173334455', 9, 'PHONE_NUMBER'),
('leila303', 'hashed_password_6', 'USER', 'Leila Hosseinzadeh', 'leila.hosseinzadeh@email.com', '09186667788', 6, 'EMAIL'),
('hassan404', 'hashed_password_7', 'USER', 'Hassan Ebrahimi', 'hassan.ebrahimi@email.com', '09199990011', 10, 'PHONE_NUMBER'),
('nazanin505', 'hashed_password_8', 'USER', 'Nazanin Rahimi', 'nazanin.rahimi@email.com', '09112223344', 11, 'EMAIL'),
('amir606', 'hashed_password_9', 'USER', 'Amir Hosseini', 'amir.hosseini@email.com', '09125556677', 12, 'PHONE_NUMBER'),
('fateme707', 'hashed_password_10', 'USER', 'Fateme Ghasemi', 'fateme.ghasemi@email.com', '09138889900', 13, 'EMAIL'),
('ahmad808', 'hashed_password_11', 'USER', 'Ahmad Rezaei', 'ahmad.rezaei@email.com', '09141112234', 14, 'PHONE_NUMBER'),
('mahsa909', 'hashed_password_12', 'USER', 'Mahsa Ahmadi', 'mahsa.ahmadi@email.com', '09154445567', 15, 'EMAIL'),
('kaveh1010', 'hashed_password_13', 'USER', 'Kaveh Hosseini', 'kaveh.hosseini@email.com', '09167778890', 16, 'PHONE_NUMBER'),
('sima1111', 'hashed_password_14', 'USER', 'Sima Karimzadeh', 'sima.karimzadeh@email.com', '09170001123', 17, 'EMAIL'),
('behnam1212', 'hashed_password_15', 'USER', 'Behnam Mohammadi', 'behnam.mohammadi@email.com', '09183334456', 18, 'PHONE_NUMBER'),
('parisa1313', 'hashed_password_16', 'USER', 'Parisa Hosseinzadeh', 'parisa.hosseinzadeh@email.com', '09196667789', 19, 'EMAIL'),
('kamran1414', 'hashed_password_17', 'USER', 'Kamran Ebrahimi', 'kamran.ebrahimi@email.com', '09199990012', 20, 'PHONE_NUMBER'),
('niloofar1515', 'hashed_password_18', 'USER', 'Niloofar Rahimi', 'niloofar.rahimi@email.com', '09112223345', 1, 'EMAIL'),
('arash1616', 'hashed_password_19', 'USER', 'Arash Hosseini', 'arash.hosseini@email.com', '09125556678', 5, 'PHONE_NUMBER'),
('shirin1717', 'hashed_password_20', 'USER', 'Shirin Ghasemi', 'shirin.ghasemi@email.com', '09138889901', 6, 'EMAIL'),
('admin1', 'hashed_password_21', 'ADMIN', 'Admin User 1', 'admin1@email.com', '09141112235', 1, 'EMAIL'),
('admin2', 'hashed_password_22', 'ADMIN', 'Admin User 2', 'admin2@email.com', '09154445568', 5, 'EMAIL'),
('user1818', 'hashed_password_23', 'USER', 'Ali Asghar', 'ali.asghar@email.com', '09167778891', 7, 'PHONE_NUMBER'),
('user1919', 'hashed_password_24', 'USER', 'Maryam Jafari', 'maryam.jafari@email.com', '09170001124', 8, 'EMAIL'),
('user2020', 'hashed_password_25', 'USER', 'Hossein Kazemi', 'hossein.kazemi@email.com', '09183334457', 9, 'PHONE_NUMBER'),
('user2121', 'hashed_password_26', 'USER', 'Fatemeh Rahimi', 'fatemeh.rahimi@email.com', '09196667790', 10, 'EMAIL'),
('user2222', 'hashed_password_27', 'USER', 'Reza Ahmadi', 'reza.ahmadi@email.com', '09199990013', 11, 'PHONE_NUMBER'),
('user2323', 'hashed_password_28', 'USER', 'Sara Hosseini', 'sara.hosseini@email.com', '09112223346', 12, 'EMAIL'),
('user2424', 'hashed_password_29', 'USER', 'Mohsen Ghasemi', 'mohsen.ghasemi@email.com', '09125556679', 13, 'PHONE_NUMBER'),
('user2525', 'hashed_password_30', 'USER', 'Zahra Rezaei', 'zahra.rezaei@email.com', '09138889902', 14, 'EMAIL'),
('user2626', 'hashed_password_31', 'USER', 'Ali Mohammadi', 'ali.mohammadi@email.com', '09141112236', 15, 'PHONE_NUMBER'),
('user2727', 'hashed_password_32', 'USER', 'Leila Karimzadeh', 'leila.karimzadeh@email.com', '09154445569', 16, 'EMAIL'),
('user2828', 'hashed_password_33', 'USER', 'Hassan Ahmadi', 'hassan.ahmadi@email.com', '09167778892', 17, 'PHONE_NUMBER'),
('user2929', 'hashed_password_34', 'USER', 'Nazanin Hosseini', 'nazanin.hosseini@email.com', '09170001125', 18, 'PHONE_NUMBER'),
('user3030', 'hashed_password_35', 'USER', 'Amir Rezaei', 'amir.rezaei@email.com', '09183334458', 19, 'EMAIL'),
('user3131', 'hashed_password_36', 'USER', 'Fateme Mohammadi', 'fateme.mohammadi@email.com', '09196667791', 20, 'PHONE_NUMBER'),
('user3232', 'hashed_password_37', 'USER', 'Ahmad Karimzadeh', 'ahmad.karimzadeh@email.com', '09199990014', 1, 'EMAIL'),
('user3333', 'hashed_password_38', 'USER', 'Mahsa Hosseini', 'mahsa.hosseini@email.com', '09112223347', 5, 'PHONE_NUMBER'),
('user3434', 'hashed_password_39', 'USER', 'Kaveh Ahmadi', 'kaveh.ahmadi@email.com', '09125556680', 6, 'EMAIL'),
('user3535', 'hashed_password_40', 'USER', 'Sima Rezaei', 'sima.rezaei@email.com', '09138889903', 7, 'PHONE_NUMBER'),
('user3636', 'hashed_password_41', 'USER', 'Behnam Mohammadi', 'behnam.mohammadi2@email.com', '09141112237', 8, 'PHONE_NUMBER'),
('user3737', 'hashed_password_42', 'USER', 'Parisa Karimzadeh', 'parisa.karimzadeh@email.com', '09154445570', 9, 'EMAIL'),
('user3838', 'hashed_password_43', 'USER', 'Kamran Ahmadi', 'kamran.ahmadi@email.com', '09167778893', 10, 'PHONE_NUMBER'),
('user3939', 'hashed_password_44', 'USER', 'Niloofar Hosseini', 'niloofar.hosseini@email.com', '09170001126', 11, 'PHONE_NUMBER'),
('user4040', 'hashed_password_45', 'USER', 'Arash Rezaei', 'arash.rezaei@email.com', '09183334459', 12, 'PHONE_NUMBER'),
('user4141', 'hashed_password_46', 'USER', 'Shirin Mohammadi', 'shirin.mohammadi@email.com', '09196667792', 13, 'PHONE_NUMBER'),
('user4242', 'hashed_password_47', 'USER', 'Ali Karimzadeh', 'ali.karimzadeh@email.com', '09199990015', 14, 'PHONE_NUMBER'),
('user4343', 'hashed_password_48', 'USER', 'Leila Ahmadi', 'leila.ahmadi@email.com', '09112223348', 15, 'PHONE_NUMBER'),
('user4444', 'hashed_password_49', 'USER', 'Hassan Hosseini', 'hassan.hosseini@email.com', '09125556681', 16, 'PHONE_NUMBER'),
('user4545', 'hashed_password_50', 'USER', 'Nazanin Rezaei', 'nazanin.rezaei@email.com', '09138889904', 17, 'PHONE_NUMBER'),
('user4646', 'hashed_password_51', 'USER', 'Ehsan Mohammadi', 'ehsan.mohammadi@email.com', '09141112238', 18, 'EMAIL'),
('user4747', 'hashed_password_52', 'USER', 'Maryam Karimzadeh', 'maryam.karimzadeh@email.com', '09154445571', 19, 'PHONE_NUMBER'),
('user4848', 'hashed_password_53', 'USER', 'Reza Hosseini', 'reza.hosseini@email.com', '09167778894', 20, 'EMAIL'),
('user4949', 'hashed_password_54', 'USER', 'Sara Ahmadi', 'sara.ahmadi2@email.com', '09170001127', 21, 'PHONE_NUMBER'),
('user5050', 'hashed_password_55', 'USER', 'Ali Rezaei', 'ali.rezaei2@email.com', '09183334460', 22, 'EMAIL'),
('user5151', 'hashed_password_56', 'USER', 'Zahra Mohammadi', 'zahra.mohammadi@email.com', '09196667793', 23, 'PHONE_NUMBER'),
('user5252', 'hashed_password_57', 'USER', 'Hassan Karimzadeh', 'hassan.karimzadeh@email.com', '09199990016', 24, 'EMAIL'),
('user5353', 'hashed_password_58', 'USER', 'Leila Hosseini', 'leila.hosseini2@email.com', '09112223349', 25, 'PHONE_NUMBER'),
('user5454', 'hashed_password_59', 'USER', 'Amir Ahmadi', 'amir.ahmadi@email.com', '09125556682', 26, 'EMAIL'),
('user5555', 'hashed_password_60', 'USER', 'Fateme Rezaei', 'fateme.rezaei@email.com', '09138889905', 27, 'PHONE_NUMBER'),
('user5656', 'hashed_password_61', 'USER', 'Ahmad Mohammadi', 'ahmad.mohammadi@email.com', '09141112239', 28, 'EMAIL'),
('user5757', 'hashed_password_62', 'USER', 'Mahsa Hosseini', 'mahsa.hosseini2@email.com', '09154445572', 29, 'PHONE_NUMBER'),
('user5858', 'hashed_password_63', 'USER', 'Kaveh Ahmadi', 'kaveh.ahmadi2@email.com', '09167778895', 30, 'EMAIL'),
('user5959', 'hashed_password_64', 'USER', 'Sima Rezaei', 'sima.rezaei2@email.com', '09170001128', 31, 'PHONE_NUMBER'),
('user6060', 'hashed_password_65', 'USER', 'Behnam Karimzadeh', 'behnam.karimzadeh@email.com', '09183334461', 32, 'EMAIL'),
('user6161', 'hashed_password_66', 'USER', 'Parisa Hosseini', 'parisa.hosseini2@email.com', '09196667794', 33, 'PHONE_NUMBER'),
('user6262', 'hashed_password_67', 'USER', 'Kamran Ahmadi', 'kamran.ahmadi2@email.com', '09199990017', 34, 'EMAIL'),
('user6363', 'hashed_password_68', 'USER', 'Niloofar Rezaei', 'niloofar.rezaei2@email.com', '09112223350', 35, 'PHONE_NUMBER'),
('user6464', 'hashed_password_69', 'USER', 'Arash Mohammadi', 'arash.mohammadi@email.com', '09125556683', 36, 'EMAIL'),
('user6565', 'hashed_password_70', 'USER', 'Shirin Karimzadeh', 'shirin.karimzadeh@email.com', '09138889906', 37, 'PHONE_NUMBER'),
('user6666', 'hashed_password_71', 'USER', 'Ali Hosseini', 'ali.hosseini2@email.com', '09141112240', 38, 'EMAIL'),
('user6767', 'hashed_password_72', 'USER', 'Leila Ahmadi', 'leila.ahmadi2@email.com', '09154445573', 39, 'PHONE_NUMBER'),
('user6868', 'hashed_password_73', 'USER', 'Hassan Rezaei', 'hassan.rezaei2@email.com', '09167778896', 40, 'EMAIL'),
('user6969', 'hashed_password_74', 'USER', 'Nazanin Mohammadi', 'nazanin.mohammadi@email.com', '09170001129', 41, 'PHONE_NUMBER'),
('user7070', 'hashed_password_75', 'USER', 'Amir Karimzadeh', 'amir.karimzadeh@email.com', '09183334462', 42, 'EMAIL'),
('user7171', 'hashed_password_76', 'USER', 'Fateme Hosseini', 'fateme.hosseini2@email.com', '09196667795', 43, 'PHONE_NUMBER'),
('user7272', 'hashed_password_77', 'USER', 'Ahmad Ahmadi', 'ahmad.ahmadi2@email.com', '09199990018', 44, 'EMAIL'),
('user7373', 'hashed_password_78', 'USER', 'Mahsa Rezaei', 'mahsa.rezaei2@email.com', '09112223351', 45, 'PHONE_NUMBER'),
('user7474', 'hashed_password_79', 'USER', 'Kaveh Mohammadi', 'kaveh.mohammadi@email.com', '09125556684', 46, 'EMAIL'),
('user7575', 'hashed_password_80', 'USER', 'Sima Karimzadeh', 'sima.karimzadeh2@email.com', '09138889907', 47, 'PHONE_NUMBER'),
('user7676', 'hashed_password_81', 'USER', 'Behnam Hosseini', 'behnam.hosseini2@email.com', '09141112241', 48, 'EMAIL'),
('user7777', 'hashed_password_82', 'USER', 'Parisa Ahmadi', 'parisa.ahmadi2@email.com', '09154445574', 1, 'PHONE_NUMBER'),
('user7878', 'hashed_password_83', 'USER', 'Kamran Rezaei', 'kamran.rezaei2@email.com', '09167778897', 5, 'EMAIL'),
('user7979', 'hashed_password_84', 'USER', 'Niloofar Mohammadi', 'niloofar.mohammadi2@email.com', '09170001130', 6, 'PHONE_NUMBER'),
('user8080', 'hashed_password_85', 'USER', 'Arash Hosseini', 'arash.hosseini2@email.com', '09183334463', 7, 'EMAIL'),
('user8181', 'hashed_password_86', 'USER', 'Shirin Karimzadeh', 'shirin.karimzadeh2@email.com', '09196667796', 8, 'PHONE_NUMBER'),
('user8282', 'hashed_password_87', 'USER', 'Ali Ahmadi', 'ali.ahmadi2@email.com', '09199990019', 9, 'EMAIL'),
('user8383', 'hashed_password_88', 'USER', 'Leila Rezaei', 'leila.rezaei2@email.com', '09112223352', 10, 'PHONE_NUMBER'),
('user8484', 'hashed_password_89', 'USER', 'Hassan Mohammadi', 'hassan.mohammadi2@email.com', '09125556685', 11, 'EMAIL'),
('user8585', 'hashed_password_90', 'USER', 'Nazanin Hosseini', 'nazanin.hosseini2@email.com', '09138889908', 12, 'PHONE_NUMBER'),
('user8686', 'hashed_password_91', 'USER', 'Amir Karimzadeh', 'amir.karimzadeh2@email.com', '09141112242', 13, 'EMAIL'),
('user8787', 'hashed_password_92', 'USER', 'Fateme Ahmadi', 'fateme.ahmadi2@email.com', '09154445575', 14, 'PHONE_NUMBER'),
('user8888', 'hashed_password_93', 'USER', 'Ahmad Rezaei', 'ahmad.rezaei2@email.com', '09167778898', 15, 'EMAIL'),
('user8989', 'hashed_password_94', 'USER', 'Mahsa Hosseini', 'mahsa.hosseini3@email.com', '09170001131', 16, 'PHONE_NUMBER'),
('user9090', 'hashed_password_95', 'USER', 'Kaveh Mohammadi', 'kaveh.mohammadi2@email.com', '09183334464', 17, 'EMAIL'),
('user9191', 'hashed_password_96', 'USER', 'Sima Ahmadi', 'sima.ahmadi2@email.com', '09196667797', 18, 'PHONE_NUMBER'),
('user9292', 'hashed_password_97', 'USER', 'Behnam Rezaei', 'behnam.rezaei2@email.com', '09199990020', 19, 'EMAIL'),
('user9393', 'hashed_password_98', 'USER', 'Parisa Hosseini', 'parisa.hosseini3@email.com', '09112223353', 20, 'PHONE_NUMBER'),
('user9494', 'hashed_password_99', 'USER', 'Kamran Karimzadeh', 'kamran.karimzadeh2@email.com', '09125556686', 21, 'EMAIL'),
('user9595', 'hashed_password_100', 'USER', 'Niloofar Ahmadi', 'niloofar.ahmadi2@email.com', '09138889909', 22, 'PHONE_NUMBER');


-- افزودن وسایل نقلیه (100 مورد)
INSERT INTO vehicles (vehicle_type) VALUES
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 1-5
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 6-10
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 11-15
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 16-20
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 21-25
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 26-30
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 31-35
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 36-40
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 41-45
('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), ('FLIGHT'), -- 46-50
('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'),     -- 51-55
('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'),     -- 56-60
('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'),     -- 61-65
('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'),     -- 66-70
('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'), ('TRAIN'),     -- 71-75
('BUS'), ('BUS'), ('BUS'), ('BUS'), ('BUS'),               -- 76-80
('BUS'), ('BUS'), ('BUS'), ('BUS'), ('BUS'),               -- 81-85
('BUS'), ('BUS'), ('BUS'), ('BUS'), ('BUS'),               -- 86-90
('BUS'), ('BUS'), ('BUS'), ('BUS'), ('BUS'),               -- 91-95
('BUS'), ('BUS'), ('BUS'), ('BUS'), ('BUS');               -- 96-100

-- افزودن پروازها (50 مورد - vehicle_id از 1 تا 50)
INSERT INTO flights (vehicle_id, airline_name, flight_class, number_of_stop, flight_code, origin_airport, destination_airport, facility) VALUES
(1, 'Iran Air', 'Economy', 0, 'IR101', 'Mehrabad Airport', 'Mashhad Airport', '{"meals": "included", "wifi": false}'),
(2, 'Mahan Air', 'Business', 1, 'MH102', 'Imam Khomeini Airport', 'Shiraz Airport', '{"meals": "included", "wifi": true, "extra_legroom": true}'),
(3, 'Qeshm Air', 'Economy', 0, 'QS103', 'Mehrabad Airport', 'Tabriz Airport', '{"meals": "optional", "wifi": false}'),
(4, 'Iran Air', 'Economy', 1, 'IR104', 'Imam Khomeini Airport', 'Ahvaz Airport', '{"meals": "included", "wifi": false}'),
(5, 'Mahan Air', 'Business', 0, 'MH105', 'Mehrabad Airport', 'Kermanshah Airport', '{"meals": "included", "wifi": true}'),
(6, 'Iran Aseman', 'Economy', 0, 'IA106', 'Mehrabad Airport', 'Rasht Airport', '{"meals": "optional", "wifi": false}'),
(7, 'Zagros Airlines', 'Business', 1, 'ZG107', 'Imam Khomeini Airport', 'Bandar Abbas Airport', '{"meals": "included", "wifi": true}'),
(8, 'Kish Air', 'Economy', 0, 'KI108', 'Mehrabad Airport', 'Yazd Airport', '{"meals": "optional", "wifi": false}'),
(9, 'Iran Air', 'Economy', 1, 'IR109', 'Imam Khomeini Airport', 'Qom Airport', '{"meals": "included", "wifi": false}'),
(10, 'Mahan Air', 'Business', 0, 'MH110', 'Mehrabad Airport', 'Kerman Airport', '{"meals": "included", "wifi": true}'),
(11, 'Qeshm Air', 'Economy', 0, 'QS111', 'Mehrabad Airport', 'Zahedan Airport', '{"meals": "optional", "wifi": false}'),
(12, 'Iran Air', 'Business', 1, 'IR112', 'Imam Khomeini Airport', 'Arak Airport', '{"meals": "included", "wifi": true}'),
(13, 'Mahan Air', 'Economy', 0, 'MH113', 'Mehrabad Airport', 'Hamedan Airport', '{"meals": "optional", "wifi": false}'),
(14, 'Zagros Airlines', 'Business', 1, 'ZG114', 'Imam Khomeini Airport', 'Gorgan Airport', '{"meals": "included", "wifi": true}'),
(15, 'Kish Air', 'Economy', 0, 'KI115', 'Mehrabad Airport', 'Sanandaj Airport', '{"meals": "optional", "wifi": false}'),
(16, 'Iran Aseman', 'Economy', 1, 'IA116', 'Imam Khomeini Airport', 'Tehran Airport', '{"meals": "included", "wifi": false}'),
(17, 'Qeshm Air', 'Business', 0, 'QS117', 'Mehrabad Airport', 'Isfahan Airport', '{"meals": "included", "wifi": true}'),
(18, 'Mahan Air', 'Economy', 1, 'MH118', 'Imam Khomeini Airport', 'Shiraz Airport', '{"meals": "optional", "wifi": false}'),
(19, 'Iran Air', 'Business', 0, 'IR119', 'Mehrabad Airport', 'Mashhad Airport', '{"meals": "included", "wifi": true}'),
(20, 'Zagros Airlines', 'Economy', 1, 'ZG120', 'Imam Khomeini Airport', 'Tabriz Airport', '{"meals": "optional", "wifi": false}'),
(21, 'Iran Air', 'Economy', 0, 'IR121', 'Mehrabad Airport', 'Ahvaz Airport', '{"meals": "included", "wifi": false}'),
(22, 'Mahan Air', 'Business', 1, 'MH122', 'Imam Khomeini Airport', 'Kermanshah Airport', '{"meals": "included", "wifi": true}'),
(23, 'Qeshm Air', 'Economy', 0, 'QS123', 'Mehrabad Airport', 'Rasht Airport', '{"meals": "optional", "wifi": false}'),
(24, 'Iran Aseman', 'Business', 1, 'IA124', 'Imam Khomeini Airport', 'Bandar Abbas Airport', '{"meals": "included", "wifi": true}'),
(25, 'Kish Air', 'Economy', 0, 'KI125', 'Mehrabad Airport', 'Yazd Airport', '{"meals": "optional", "wifi": false}'),
(26, 'Zagros Airlines', 'Economy', 1, 'ZG126', 'Imam Khomeini Airport', 'Qom Airport', '{"meals": "included", "wifi": false}'),
(27, 'Iran Air', 'Business', 0, 'IR127', 'Mehrabad Airport', 'Kerman Airport', '{"meals": "included", "wifi": true}'),
(28, 'Mahan Air', 'Economy', 1, 'MH128', 'Imam Khomeini Airport', 'Zahedan Airport', '{"meals": "optional", "wifi": false}'),
(29, 'Qeshm Air', 'Business', 0, 'QS129', 'Mehrabad Airport', 'Arak Airport', '{"meals": "included", "wifi": true}'),
(30, 'Iran Aseman', 'Economy', 1, 'IA130', 'Imam Khomeini Airport', 'Hamedan Airport', '{"meals": "included", "wifi": false}'),
(31, 'Kish Air', 'Business', 0, 'KI131', 'Mehrabad Airport', 'Gorgan Airport', '{"meals": "included", "wifi": true}'),
(32, 'Zagros Airlines', 'Economy', 1, 'ZG132', 'Imam Khomeini Airport', 'Sanandaj Airport', '{"meals": "optional", "wifi": false}'),
(33, 'Iran Air', 'Business', 0, 'IR133', 'Mehrabad Airport', 'Qazvin Airport', '{"meals": "included", "wifi": true}'),
(34, 'Mahan Air', 'Economy', 1, 'MH134', 'Imam Khomeini Airport', 'Urmia Airport', '{"meals": "optional", "wifi": false}'),
(35, 'Qeshm Air', 'Business', 0, 'QS135', 'Mehrabad Airport', 'Zanjan Airport', '{"meals": "included", "wifi": true}'),
(36, 'Iran Aseman', 'Economy', 1, 'IA136', 'Imam Khomeini Airport', 'Semnan Airport', '{"meals": "included", "wifi": false}'),
(37, 'Kish Air', 'Business', 0, 'KI137', 'Mehrabad Airport', 'Bushehr Airport', '{"meals": "included", "wifi": true}'),
(38, 'Zagros Airlines', 'Economy', 1, 'ZG138', 'Imam Khomeini Airport', 'Birjand Airport', '{"meals": "optional", "wifi": false}'),
(39, 'Iran Air', 'Business', 0, 'IR139', 'Mehrabad Airport', 'Bojnurd Airport', '{"meals": "included", "wifi": true}'),
(40, 'Mahan Air', 'Economy', 1, 'MH140', 'Imam Khomeini Airport', 'Sari Airport', '{"meals": "optional", "wifi": false}'),
(41, 'Qeshm Air', 'Economy', 0, 'QS141', 'Mehrabad Airport', 'Amol Airport', '{"meals": "optional", "wifi": false}'),
(42, 'Iran Aseman', 'Business', 1, 'IA142', 'Imam Khomeini Airport', 'Babol Airport', '{"meals": "included", "wifi": true}'),
(43, 'Kish Air', 'Economy', 0, 'KI143', 'Mehrabad Airport', 'Gachsaran Airport', '{"meals": "optional", "wifi": false}'),
(44, 'Zagros Airlines', 'Business', 1, 'ZG144', 'Imam Khomeini Airport', 'Ilam Airport', '{"meals": "included", "wifi": true}'),
(45, 'Iran Air', 'Economy', 0, 'IR145', 'Mehrabad Airport', 'Khorramabad Airport', '{"meals": "included", "wifi": false}'),
(46, 'Mahan Air', 'Business', 1, 'MH146', 'Imam Khomeini Airport', 'Ardabil Airport', '{"meals": "included", "wifi": true}'),
(47, 'Qeshm Air', 'Economy', 0, 'QS147', 'Mehrabad Airport', 'Chabahar Airport', '{"meals": "optional", "wifi": false}'),
(48, 'Iran Aseman', 'Business', 1, 'IA148', 'Imam Khomeini Airport', 'Dezful Airport', '{"meals": "included", "wifi": true}'),
(49, 'Kish Air', 'Economy', 0, 'KI149', 'Mehrabad Airport', 'Borujerd Airport', '{"meals": "optional", "wifi": false}'),
(50, 'Zagros Airlines', 'Business', 1, 'ZG150', 'Imam Khomeini Airport', 'Sabzevar Airport', '{"meals": "included", "wifi": true}');

-- افزودن قطارها (25 مورد - vehicle_id از 51 تا 75)
INSERT INTO trains (vehicle_id, train_stars, choosing_a_closed_coupe, facility) VALUES
(51, 4, true, '{"meals": "optional", "wifi": false, "power_outlets": true}'),
(52, 3, false, '{"meals": "included", "wifi": false}'),
(53, 5, true, '{"meals": "included", "wifi": true, "power_outlets": true}'),
(54, 2, false, '{"meals": "optional", "wifi": false}'),
(55, 4, true, '{"meals": "included", "wifi": false, "extra_seating": true}'),
(56, 3, false, '{"meals": "optional", "wifi": true}'),
(57, 4, true, '{"meals": "included", "wifi": false}'),
(58, 5, true, '{"meals": "included", "wifi": true, "power_outlets": true}'),
(59, 2, false, '{"meals": "optional", "wifi": false}'),
(60, 3, true, '{"meals": "included", "wifi": false}'),
(61, 4, false, '{"meals": "optional", "wifi": true}'),
(62, 5, true, '{"meals": "included", "wifi": true, "power_outlets": true}'),
(63, 3, false, '{"meals": "optional", "wifi": false}'),
(64, 4, true, '{"meals": "included", "wifi": false}'),
(65, 2, false, '{"meals": "optional", "wifi": true}'),
(66, 3, true, '{"meals": "included", "wifi": false}'),
(67, 4, false, '{"meals": "optional", "wifi": true}'),
(68, 5, true, '{"meals": "included", "wifi": true, "power_outlets": true}'),
(69, 2, false, '{"meals": "optional", "wifi": false}'),
(70, 3, true, '{"meals": "included", "wifi": false}'),
(71, 4, false, '{"meals": "optional", "wifi": true}'),
(72, 5, true, '{"meals": "included", "wifi": true, "power_outlets": true}'),
(73, 3, false, '{"meals": "optional", "wifi": false}'),
(74, 4, true, '{"meals": "included", "wifi": false}'),
(75, 2, false, '{"meals": "optional", "wifi": true}');

-- افزودن اتوبوس‌ها (25 مورد - vehicle_id از 76 تا 100)
INSERT INTO buses (vehicle_id, company_name, bus_type, number_of_chairs, facility) VALUES
(76, 'Hamsafar', 'VIP', 30, '{"air_conditioning": true, "snacks": true}'),
(77, 'Seiro Safar', 'Normal', 40, '{"air_conditioning": true, "snacks": false}'),
(78, 'Taavoni', 'Semi-Lux', 35, '{"air_conditioning": true, "snacks": true}'),
(79, 'Pars Tourist', 'VIP', 28, '{"air_conditioning": true, "wifi": true}'),
(80, 'Zagros', 'Normal', 45, '{"air_conditioning": false, "snacks": false}'),
(81, 'Hamsafar', 'VIP', 32, '{"air_conditioning": true, "snacks": true}'),
(82, 'Seiro Safar', 'Normal', 38, '{"air_conditioning": true, "snacks": false}'),
(83, 'Taavoni', 'Semi-Lux', 34, '{"air_conditioning": true, "snacks": true}'),
(84, 'Pars Tourist', 'VIP', 30, '{"air_conditioning": true, "wifi": true}'),
(85, 'Zagros', 'Normal', 42, '{"air_conditioning": false, "snacks": false}'),
(86, 'Hamsafar', 'VIP', 31, '{"air_conditioning": true, "snacks": true}'),
(87, 'Seiro Safar', 'Normal', 39, '{"air_conditioning": true, "snacks": false}'),
(88, 'Taavoni', 'Semi-Lux', 36, '{"air_conditioning": true, "snacks": true}'),
(89, 'Pars Tourist', 'VIP', 29, '{"air_conditioning": true, "wifi": true}'),
(90, 'Zagros', 'Normal', 44, '{"air_conditioning": false, "snacks": false}'),
(91, 'Hamsafar', 'VIP', 33, '{"air_conditioning": true, "snacks": true}'),
(92, 'Seiro Safar', 'Normal', 41, '{"air_conditioning": true, "snacks": false}'),
(93, 'Taavoni', 'Semi-Lux', 37, '{"air_conditioning": true, "snacks": true}'),
(94, 'Pars Tourist', 'VIP', 27, '{"air_conditioning": true, "wifi": true}'),
(95, 'Zagros', 'Normal', 43, '{"air_conditioning": false, "snacks": false}'),
(96, 'Hamsafar', 'VIP', 32, '{"air_conditioning": true, "snacks": true}'),
(97, 'Seiro Safar', 'Normal', 40, '{"air_conditioning": true, "snacks": false}'),
(98, 'Taavoni', 'Semi-Lux', 35, '{"air_conditioning": true, "snacks": true}'),
(99, 'Pars Tourist', 'VIP', 28, '{"air_conditioning": true, "wifi": true}'),
(100, 'Zagros', 'Normal', 45, '{"air_conditioning": false, "snacks": false}');

-- افزودن تیکت‌ها (20 تیکت)
INSERT INTO tickets (vehicle_id, origin_location_id, destination_location_id, departure_start, departure_end, price,total_capacity, remaining_capacity) VALUES
-- تیکت‌های پرواز (vehicle_id: 1 تا 10)
(1, 1, 7, '2025-05-06 08:00:00', '2025-05-06 09:30:00', 3000000, 5,0), -- Tehran to Mashhad
(2, 1, 6, '2025-05-07 07:00:00', '2025-05-07 08:30:00', 3500000, 5,0),  -- Tehran to Shiraz
(3, 1, 8, '2025-05-08 09:00:00', '2025-05-08 10:30:00', 3200000, 5,0),  -- Tehran to Tabriz
(4, 1, 9, '2025-05-09 08:30:00', '2025-05-09 10:00:00', 3400000, 5,0),  -- Tehran to Ahvaz
(5, 1, 10, '2025-05-10 07:00:00', '2025-05-10 08:30:00', 3100000, 5,0), -- Tehran to Kermanshah
(6, 7, 1, '2025-05-11 10:00:00', '2025-05-11 11:30:00', 3000000, 5,0), -- Mashhad to Tehran
(7, 6, 8, '2025-05-12 07:30:00', '2025-05-12 09:00:00', 3400000, 5,0),  -- Shiraz to Tabriz
(8, 9, 10, '2025-05-13 08:00:00', '2025-05-13 09:30:00', 3300000, 5,0), -- Ahvaz to Kermanshah
(9, 1, 15, '2025-05-14 09:30:00', '2025-05-14 11:00:00', 3400000, 5,0), -- Tehran to Kerman
(10, 15, 1, '2025-05-15 06:00:00', '2025-05-15 07:30:00', 3100000, 5,0), -- Kerman to Tehran
-- تیکت‌های قطار (vehicle_id: 51 تا 55)
(51, 1, 6, '2025-05-16 07:00:00', '2025-05-16 15:00:00', 1500000, 5,0), -- Tehran to Shiraz
(52, 1, 7, '2025-05-17 08:00:00', '2025-05-17 14:00:00', 1200000, 5,0), -- Tehran to Mashhad
(53, 1, 8, '2025-05-18 09:00:00', '2025-05-18 15:00:00', 1400000, 5,0), -- Tehran to Tabriz
(54, 1, 9, '2025-05-19 07:30:00', '2025-05-19 13:30:00', 1300000, 5,0), -- Tehran to Ahvaz
(55, 7, 1, '2025-05-20 08:30:00', '2025-05-20 14:30:00', 1200000, 5,0), -- Mashhad to Tehran
-- تیکت‌های اتوبوس (vehicle_id: 76 تا 80)
(76, 1, 2, '2025-05-21 07:00:00', '2025-05-21 08:00:00', 300000, 5,0),  -- Tehran to Karaj
(77, 1, 3, '2025-05-22 08:00:00', '2025-05-22 09:00:00', 350000, 5,0),  -- Tehran to Varamin
(78, 1, 4, '2025-05-23 09:00:00', '2025-05-23 10:00:00', 400000, 5,0),  -- Tehran to Rey
(79, 1, 5, '2025-05-24 07:30:00', '2025-05-24 12:30:00', 600000, 5,0),  -- Tehran to Isfahan
(80, 5, 1, '2025-05-25 07:30:00', '2025-05-25 12:30:00', 600000, 5,0);  -- Isfahan to Tehran

-- افزودن رزروها (100 رزرو)
INSERT INTO reservations (username, ticket_id, reservation_status, date_and_time_of_reservation, reservation_seat) VALUES
-- رزروهای تیکت 1 (Tehran to Mashhad - پرواز)
('ali123', 1, 'RESERVED', '2025-05-02 10:00:00', 1),
('sara456', 1, 'RESERVED', '2025-05-02 12:00:00', 2),
('mohammad789', 1, 'RESERVED', '2025-05-03 09:00:00', 3),
('zahra101', 1, 'RESERVED', '2025-05-03 11:00:00', 4),
('reza202', 1, 'RESERVED', '2025-05-04 08:00:00', 5),
-- رزروهای تیکت 2 (Tehran to Shiraz - پرواز)
('leila303', 2, 'RESERVED', '2025-05-03 10:00:00', 1),
('hassan404', 2, 'RESERVED', '2025-05-03 12:00:00', 2),
('nazanin505', 2, 'RESERVED', '2025-05-04 09:00:00', 3),
('amir606', 2, 'RESERVED', '2025-05-04 11:00:00', 4),
('fateme707', 2, 'RESERVED', '2025-05-05 08:00:00', 5),
-- رزروهای تیکت 3 (Tehran to Tabriz - پرواز)
('ahmad808', 3, 'RESERVED', '2025-05-04 10:00:00', 1),
('mahsa909', 3, 'RESERVED', '2025-05-04 12:00:00', 2),
('kaveh1010', 3, 'RESERVED', '2025-05-05 09:00:00', 3),
('sima1111', 3, 'RESERVED', '2025-05-05 11:00:00', 4),
('behnam1212', 3, 'RESERVED', '2025-05-06 08:00:00', 5),
-- رزروهای تیکت 4 (Tehran to Ahvaz - پرواز)
('parisa1313', 4, 'RESERVED', '2025-05-05 10:00:00', 1),
('kamran1414', 4, 'RESERVED', '2025-05-05 12:00:00', 2),
('niloofar1515', 4, 'RESERVED', '2025-05-06 09:00:00', 3),
('arash1616', 4, 'RESERVED', '2025-05-06 11:00:00', 4),
('shirin1717', 4, 'RESERVED', '2025-05-07 08:00:00', 5),
-- رزروهای تیکت 5 (Tehran to Kermanshah - پرواز)
('user1818', 5, 'RESERVED', '2025-05-06 10:00:00', 1),
('user1919', 5, 'RESERVED', '2025-05-06 12:00:00', 2),
('user2020', 5, 'RESERVED', '2025-05-07 09:00:00', 3),
('user2121', 5, 'RESERVED', '2025-05-07 11:00:00', 4),
('user2222', 5, 'RESERVED', '2025-05-08 08:00:00', 5),
-- رزروهای تیکت 6 (Mashhad to Tehran - پرواز)
('user2323', 6, 'RESERVED', '2025-05-07 10:00:00', 1),
('user2424', 6, 'RESERVED', '2025-05-07 12:00:00', 2),
('user2525', 6, 'RESERVED', '2025-05-08 09:00:00', 3),
('user2626', 6, 'RESERVED', '2025-05-08 11:00:00', 4),
('user2727', 6, 'RESERVED', '2025-05-09 08:00:00', 5),
-- رزروهای تیکت 7 (Shiraz to Tabriz - پرواز)
('user2828', 7, 'RESERVED', '2025-05-08 10:00:00', 1),
('user2929', 7, 'RESERVED', '2025-05-08 12:00:00', 2),
('user3030', 7, 'RESERVED', '2025-05-09 09:00:00', 3),
('user3131', 7, 'RESERVED', '2025-05-09 11:00:00', 4),
('user3232', 7, 'RESERVED', '2025-05-10 08:00:00', 5),
-- رزروهای تیکت 8 (Ahvaz to Kermanshah - پرواز)
('user3333', 8, 'RESERVED', '2025-05-09 10:00:00', 1),
('user3434', 8, 'RESERVED', '2025-05-09 12:00:00', 2),
('user3535', 8, 'RESERVED', '2025-05-10 09:00:00', 3),
('user3636', 8, 'RESERVED', '2025-05-10 11:00:00', 4),
('user3737', 8, 'RESERVED', '2025-05-11 08:00:00', 5),
-- رزروهای تیکت 9 (Tehran to Kerman - پرواز)
('user3838', 9, 'RESERVED', '2025-05-10 10:00:00', 1),
('user3939', 9, 'RESERVED', '2025-05-10 12:00:00', 2),
('user4040', 9, 'RESERVED', '2025-05-11 09:00:00', 3),
('user4141', 9, 'RESERVED', '2025-05-11 11:00:00', 4),
('user4242', 9, 'RESERVED', '2025-05-12 08:00:00', 5),
-- رزروهای تیکت 10 (Kerman to Tehran - پرواز)
('user4343', 10, 'RESERVED', '2025-05-11 10:00:00', 1),
('user4444', 10, 'RESERVED', '2025-05-11 12:00:00', 2),
('user4545', 10, 'RESERVED', '2025-05-12 09:00:00', 3),
('user4646', 10, 'RESERVED', '2025-05-12 11:00:00', 4),
('user4747', 10, 'RESERVED', '2025-05-13 08:00:00', 5),
-- رزروهای تیکت 11 (Tehran to Shiraz - قطار)
('user4848', 11, 'RESERVED', '2025-05-12 10:00:00', 1),
('user4949', 11, 'RESERVED', '2025-05-12 12:00:00', 2),
('user5050', 11, 'RESERVED', '2025-05-13 09:00:00', 3),
('user5151', 11, 'RESERVED', '2025-05-13 11:00:00', 4),
('user5252', 11, 'RESERVED', '2025-05-14 08:00:00', 5),
-- رزروهای تیکت 12 (Tehran to Mashhad - قطار)
('user5353', 12, 'RESERVED', '2025-05-13 10:00:00', 1),
('user5454', 12, 'RESERVED', '2025-05-13 12:00:00', 2),
('user5555', 12, 'RESERVED', '2025-05-14 09:00:00', 3),
('user5656', 12, 'RESERVED', '2025-05-14 11:00:00', 4),
('user5757', 12, 'RESERVED', '2025-05-15 08:00:00', 5),
-- رزروهای تیکت 13 (Tehran to Tabriz - قطار)
('user5858', 13, 'RESERVED', '2025-05-14 10:00:00', 1),
('user5959', 13, 'RESERVED', '2025-05-14 12:00:00', 2),
('user6060', 13, 'RESERVED', '2025-05-15 09:00:00', 3),
('user6161', 13, 'RESERVED', '2025-05-15 11:00:00', 4),
('user6262', 13, 'RESERVED', '2025-05-16 08:00:00', 5),
-- رزروهای تیکت 14 (Tehran to Ahvaz - قطار)
('user6363', 14, 'RESERVED', '2025-05-15 10:00:00', 1),
('user6464', 14, 'RESERVED', '2025-05-15 12:00:00', 2),
('user6565', 14, 'RESERVED', '2025-05-16 09:00:00', 3),
('user6666', 14, 'RESERVED', '2025-05-16 11:00:00', 4),
('user6767', 14, 'RESERVED', '2025-05-17 08:00:00', 5),
-- رزروهای تیکت 15 (Mashhad to Tehran - قطار)
('user6868', 15, 'RESERVED', '2025-05-16 10:00:00', 1),
('user6969', 15, 'RESERVED', '2025-05-16 12:00:00', 2),
('user7070', 15, 'RESERVED', '2025-05-17 09:00:00', 3),
('user7171', 15, 'RESERVED', '2025-05-17 11:00:00', 4),
('user7272', 15, 'RESERVED', '2025-05-18 08:00:00', 5),
-- رزروهای تیکت 16 (Tehran to Karaj - اتوبوس)
('user7373', 16, 'RESERVED', '2025-05-17 10:00:00', 1),
('user7474', 16, 'RESERVED', '2025-05-17 12:00:00', 2),
('user7575', 16, 'RESERVED', '2025-05-18 09:00:00', 3),
('user7676', 16, 'RESERVED', '2025-05-18 11:00:00', 4),
('user7777', 16, 'RESERVED', '2025-05-19 08:00:00', 5),
-- رزروهای تیکت 17 (Tehran to Varamin - اتوبوس)
('user7878', 17, 'RESERVED', '2025-05-18 10:00:00', 1),
('user7979', 17, 'RESERVED', '2025-05-18 12:00:00', 2),
('user8080', 17, 'RESERVED', '2025-05-19 09:00:00', 3),
('user8181', 17, 'RESERVED', '2025-05-19 11:00:00', 4),
('user8282', 17, 'RESERVED', '2025-05-20 08:00:00', 5),
-- رزروهای تیکت 18 (Tehran to Rey - اتوبوس)
('user8383', 18, 'RESERVED', '2025-05-19 10:00:00', 1),
('user8484', 18, 'RESERVED', '2025-05-19 12:00:00', 2),
('user8585', 18, 'RESERVED', '2025-05-20 09:00:00', 3),
('user8686', 18, 'RESERVED', '2025-05-20 11:00:00', 4),
('user8787', 18, 'RESERVED', '2025-05-21 08:00:00', 5),
-- رزروهای تیکت 19 (Tehran to Isfahan - اتوبوس)
('user8888', 19, 'RESERVED', '2025-05-20 10:00:00', 1),
('user8989', 19, 'RESERVED', '2025-05-20 12:00:00', 2),
('user9090', 19, 'RESERVED', '2025-05-21 09:00:00', 3),
('user9191', 19, 'RESERVED', '2025-05-21 11:00:00', 4),
('user9292', 19, 'RESERVED', '2025-05-22 08:00:00', 5),
-- رزروهای تیکت 20 (Isfahan to Tehran - اتوبوس)
('user9393', 20, 'RESERVED', '2025-05-21 10:00:00', 1),
('user9494', 20, 'RESERVED', '2025-05-21 12:00:00', 2),
('user9595', 20, 'RESERVED', '2025-05-22 09:00:00', 3),
('ali123', 20, 'RESERVED', '2025-05-22 11:00:00', 4),
('sara456', 20, 'RESERVED', '2025-05-23 08:00:00', 5);



-- افزودن پرداخت‌ها (100 پرداخت)
INSERT INTO payments (username, reservation_id, amount_paid, payment_status, date_and_time_of_payment, payment_method) VALUES
-- پرداخت برای رزروهای تیکت 1 (Tehran to Mashhad - پرواز، قیمت: 3000000)
('ali123', 1, 3000000, 'PAID', '2025-05-02 10:15:00', 'CREDIT_CARD'), -- ali123: EMAIL
('sara456', 2, 3000000, 'PAID', '2025-05-02 12:15:00', 'WALLET'), -- sara456: PHONE_NUMBER
('mohammad789', 3, 3000000, 'PAID', '2025-05-03 09:15:00', 'CREDIT_CARD'), -- mohammad789: EMAIL
('zahra101', 4, 3000000, 'PAID', '2025-05-03 11:15:00', 'CREDIT_CARD'), -- zahra101: EMAIL
('reza202', 5, 3000000, 'PAID', '2025-05-04 08:15:00', 'WALLET'), -- reza202: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 2 (Tehran to Shiraz - پرواز، قیمت: 3500000)
('leila303', 6, 3500000, 'PAID', '2025-05-03 10:15:00', 'CREDIT_CARD'), -- leila303: EMAIL
('hassan404', 7, 3500000, 'PAID', '2025-05-03 12:15:00', 'WALLET'), -- hassan404: PHONE_NUMBER
('nazanin505', 8, 3500000, 'PAID', '2025-05-04 09:15:00', 'CREDIT_CARD'), -- nazanin505: EMAIL
('amir606', 9, 3500000, 'PAID', '2025-05-04 11:15:00', 'WALLET'), -- amir606: PHONE_NUMBER
('fateme707', 10, 3500000, 'PAID', '2025-05-05 08:15:00', 'CREDIT_CARD'), -- fateme707: EMAIL
-- پرداخت برای رزروهای تیکت 3 (Tehran to Tabriz - پرواز، قیمت: 3200000)
('ahmad808', 11, 3200000, 'PAID', '2025-05-04 10:15:00', 'WALLET'), -- ahmad808: PHONE_NUMBER
('mahsa909', 12, 3200000, 'PAID', '2025-05-04 12:15:00', 'CREDIT_CARD'), -- mahsa909: EMAIL
('kaveh1010', 13, 3200000, 'PAID', '2025-05-05 09:15:00', 'WALLET'), -- kaveh1010: PHONE_NUMBER
('sima1111', 14, 3200000, 'PAID', '2025-05-05 11:15:00', 'CREDIT_CARD'), -- sima1111: EMAIL
('behnam1212', 15, 3200000, 'PAID', '2025-05-06 08:15:00', 'WALLET'), -- behnam1212: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 4 (Tehran to Ahvaz - پرواز، قیمت: 3400000)
('parisa1313', 16, 3400000, 'PAID', '2025-05-05 10:15:00', 'CREDIT_CARD'), -- parisa1313: EMAIL
('kamran1414', 17, 3400000, 'PAID', '2025-05-05 12:15:00', 'WALLET'), -- kamran1414: PHONE_NUMBER
('niloofar1515', 18, 3400000, 'PAID', '2025-05-06 09:15:00', 'CREDIT_CARD'), -- niloofar1515: EMAIL
('arash1616', 19, 3400000, 'PAID', '2025-05-06 11:15:00', 'WALLET'), -- arash1616: PHONE_NUMBER
('shirin1717', 20, 3400000, 'PAID', '2025-05-07 08:15:00', 'CREDIT_CARD'), -- shirin1717: EMAIL
-- پرداخت برای رزروهای تیکت 5 (Tehran to Kermanshah - پرواز، قیمت: 3100000)
('user1818', 21, 3100000, 'PAID', '2025-05-06 10:15:00', 'WALLET'), -- user1818: PHONE_NUMBER
('user1919', 22, 3100000, 'PAID', '2025-05-06 12:15:00', 'CREDIT_CARD'), -- user1919: EMAIL
('user2020', 23, 3100000, 'PAID', '2025-05-07 09:15:00', 'WALLET'), -- user2020: PHONE_NUMBER
('user2121', 24, 3100000, 'PAID', '2025-05-07 11:15:00', 'CREDIT_CARD'), -- user2121: EMAIL
('user2222', 25, 3100000, 'PAID', '2025-05-08 08:15:00', 'WALLET'), -- user2222: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 6 (Mashhad to Tehran - پرواز، قیمت: 3000000)
('user2323', 26, 3000000, 'PAID', '2025-05-07 10:15:00', 'CREDIT_CARD'), -- user2323: EMAIL
('user2424', 27, 3000000, 'PAID', '2025-05-07 12:15:00', 'WALLET'), -- user2424: PHONE_NUMBER
('user2525', 28, 3000000, 'PAID', '2025-05-08 09:15:00', 'CREDIT_CARD'), -- user2525: EMAIL
('user2626', 29, 3000000, 'PAID', '2025-05-08 11:15:00', 'WALLET'), -- user2626: PHONE_NUMBER
('user2727', 30, 3000000, 'PAID', '2025-05-09 08:15:00', 'CREDIT_CARD'), -- user2727: EMAIL
-- پرداخت برای رزروهای تیکت 7 (Shiraz to Tabriz - پرواز، قیمت: 3400000)
('user2828', 31, 3400000, 'PAID', '2025-05-08 10:15:00', 'WALLET'), -- user2828: PHONE_NUMBER
('user2929', 32, 3400000, 'PAID', '2025-05-08 12:15:00', 'WALLET'), -- user2929: PHONE_NUMBER
('user3030', 33, 3400000, 'PAID', '2025-05-09 09:15:00', 'CREDIT_CARD'), -- user3030: EMAIL
('user3131', 34, 3400000, 'PAID', '2025-05-09 11:15:00', 'WALLET'), -- user3131: PHONE_NUMBER
('user3232', 35, 3400000, 'PAID', '2025-05-10 08:15:00', 'CREDIT_CARD'), -- user3232: EMAIL
-- پرداخت برای رزروهای تیکت 8 (Ahvaz to Kermanshah - پرواز، قیمت: 3300000)
('user3333', 36, 3300000, 'PAID', '2025-05-09 10:15:00', 'WALLET'), -- user3333: PHONE_NUMBER
('user3434', 37, 3300000, 'PAID', '2025-05-09 12:15:00', 'CREDIT_CARD'), -- user3434: EMAIL
('user3535', 38, 3300000, 'PAID', '2025-05-10 09:15:00', 'WALLET'), -- user3535: PHONE_NUMBER
('user3636', 39, 3300000, 'PAID', '2025-05-10 11:15:00', 'CREDIT_CARD'), -- user3636: EMAIL
('user3737', 40, 3300000, 'PAID', '2025-05-11 08:15:00', 'WALLET'), -- user3737: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 9 (Tehran to Kerman - پرواز، قیمت: 3400000)
('user3838', 41, 3400000, 'PAID', '2025-05-10 10:15:00', 'CREDIT_CARD'), -- user3838: EMAIL
('user3939', 42, 3400000, 'PAID', '2025-05-10 12:15:00', 'WALLET'), -- user3939: PHONE_NUMBER
('user4040', 43, 3400000, 'PAID', '2025-05-11 09:15:00', 'CREDIT_CARD'), -- user4040: EMAIL
('user4141', 44, 3400000, 'PAID', '2025-05-11 11:15:00', 'WALLET'), -- user4141: PHONE_NUMBER
('user4242', 45, 3400000, 'PAID', '2025-05-12 08:15:00', 'CREDIT_CARD'), -- user4242: EMAIL
-- پرداخت برای رزروهای تیکت 10 (Kerman to Tehran - پرواز، قیمت: 3100000)
('user4343', 46, 3100000, 'PAID', '2025-05-11 10:15:00', 'WALLET'), -- user4343: PHONE_NUMBER
('user4444', 47, 3100000, 'PAID', '2025-05-11 12:15:00', 'CREDIT_CARD'), -- user4444: EMAIL
('user4545', 48, 3100000, 'PAID', '2025-05-12 09:15:00', 'WALLET'), -- user4545: PHONE_NUMBER
('user4646', 49, 3100000, 'PAID', '2025-05-12 11:15:00', 'CREDIT_CARD'), -- user4646: EMAIL
('user4747', 50, 3100000, 'PAID', '2025-05-13 08:15:00', 'WALLET'), -- user4747: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 11 (Tehran to Shiraz - قطار، قیمت: 1500000)
('user4848', 51, 1500000, 'PAID', '2025-05-12 10:15:00', 'CREDIT_CARD'), -- user4848: EMAIL
('user4949', 52, 1500000, 'PAID', '2025-05-12 12:15:00', 'WALLET'), -- user4949: PHONE_NUMBER
('user5050', 53, 1500000, 'PAID', '2025-05-13 09:15:00', 'CREDIT_CARD'), -- user5050: EMAIL
('user5151', 54, 1500000, 'PAID', '2025-05-13 11:15:00', 'WALLET'), -- user5151: PHONE_NUMBER
('user5252', 55, 1500000, 'PAID', '2025-05-14 08:15:00', 'CREDIT_CARD'), -- user5252: EMAIL
-- پرداخت برای رزروهای تیکت 12 (Tehran to Mashhad - قطار، قیمت: 1200000)
('user5353', 56, 1200000, 'PAID', '2025-05-13 10:15:00', 'WALLET'), -- user5353: PHONE_NUMBER
('user5454', 57, 1200000, 'PAID', '2025-05-13 12:15:00', 'CREDIT_CARD'), -- user5454: EMAIL
('user5555', 58, 1200000, 'PAID', '2025-05-14 09:15:00', 'WALLET'), -- user5555: PHONE_NUMBER
('user5656', 59, 1200000, 'PAID', '2025-05-14 11:15:00', 'CREDIT_CARD'), -- user5656: EMAIL
('user5757', 60, 1200000, 'PAID', '2025-05-15 08:15:00', 'WALLET'), -- user5757: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 13 (Tehran to Tabriz - قطار، قیمت: 1400000)
('user5858', 61, 1400000, 'PAID', '2025-05-14 10:15:00', 'CREDIT_CARD'), -- user5858: EMAIL
('user5959', 62, 1400000, 'PAID', '2025-05-14 12:15:00', 'WALLET'), -- user5959: PHONE_NUMBER
('user6060', 63, 1400000, 'PAID', '2025-05-15 09:15:00', 'CREDIT_CARD'), -- user6060: EMAIL
('user6161', 64, 1400000, 'PAID', '2025-05-15 11:15:00', 'WALLET'), -- user6161: PHONE_NUMBER
('user6262', 65, 1400000, 'PAID', '2025-05-16 08:15:00', 'CREDIT_CARD'), -- user6262: EMAIL
-- پرداخت برای رزروهای تیکت 14 (Tehran to Ahvaz - قطار، قیمت: 1300000)
('user6363', 66, 1300000, 'PAID', '2025-05-15 10:15:00', 'WALLET'), -- user6363: EMAIL
('user6464', 67, 1300000, 'PAID', '2025-05-15 12:15:00', 'WALLET'), -- user6464: PHONE_NUMBER
('user6565', 68, 1300000, 'PAID', '2025-05-16 09:15:00', 'CREDIT_CARD'), -- user6565: EMAIL
('user6666', 69, 1300000, 'PAID', '2025-05-16 11:15:00', 'WALLET'), -- user6666: PHONE_NUMBER
('user6767', 70, 1300000, 'PAID', '2025-05-17 08:15:00', 'CREDIT_CARD'), -- user6767: EMAIL
-- پرداخت برای رزروهای تیکت 15 (Mashhad to Tehran - قطار، قیمت: 1200000)
('user6868', 71, 1200000, 'PAID', '2025-05-16 10:15:00', 'WALLET'), -- user6868: PHONE_NUMBER
('user6969', 72, 1200000, 'PAID', '2025-05-16 12:15:00', 'CREDIT_CARD'), -- user6969: EMAIL
('user7070', 73, 1200000, 'PAID', '2025-05-17 09:15:00', 'WALLET'), -- user7070: PHONE_NUMBER
('user7171', 74, 1200000, 'PAID', '2025-05-17 11:15:00', 'CREDIT_CARD'), -- user7171: EMAIL
('user7272', 75, 1200000, 'PAID', '2025-05-18 08:15:00', 'WALLET'), -- user7272: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 16 (Tehran to Karaj - اتوبوس، قیمت: 300000)
('user7373', 76, 300000, 'PAID', '2025-05-17 10:15:00', 'CREDIT_CARD'), -- user7373: EMAIL
('user7474', 77, 300000, 'PAID', '2025-05-17 12:15:00', 'WALLET'), -- user7474: PHONE_NUMBER
('user7575', 78, 300000, 'PAID', '2025-05-18 09:15:00', 'CREDIT_CARD'), -- user7575: EMAIL
('user7676', 79, 300000, 'PAID', '2025-05-18 11:15:00', 'WALLET'), -- user7676: PHONE_NUMBER
('user7777', 80, 300000, 'PAID', '2025-05-19 08:15:00', 'CREDIT_CARD'), -- user7777: EMAIL
-- پرداخت برای رزروهای تیکت 17 (Tehran to Varamin - اتوبوس، قیمت: 350000)
('user7878', 81, 350000, 'PAID', '2025-05-18 10:15:00', 'WALLET'), -- user7878: PHONE_NUMBER
('user7979', 82, 350000, 'PAID', '2025-05-18 12:15:00', 'CREDIT_CARD'), -- user7979: EMAIL
('user8080', 83, 350000, 'PAID', '2025-05-19 09:15:00', 'WALLET'), -- user8080: PHONE_NUMBER
('user8181', 84, 350000, 'PAID', '2025-05-19 11:15:00', 'CREDIT_CARD'), -- user8181: EMAIL
('user8282', 85, 350000, 'PAID', '2025-05-20 08:15:00', 'WALLET'), -- user8282: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 18 (Tehran to Rey - اتوبوس، قیمت: 400000)
('user8383', 86, 400000, 'PAID', '2025-05-19 10:15:00', 'CREDIT_CARD'), -- user8383: EMAIL
('user8484', 87, 400000, 'PAID', '2025-05-19 12:15:00', 'WALLET'), -- user8484: PHONE_NUMBER
('user8585', 88, 400000, 'PAID', '2025-05-20 09:15:00', 'CREDIT_CARD'), -- user8585: EMAIL
('user8686', 89, 400000, 'PAID', '2025-05-20 11:15:00', 'WALLET'), -- user8686: PHONE_NUMBER
('user8787', 90, 400000, 'PAID', '2025-05-21 08:15:00', 'CREDIT_CARD'), -- user8787: EMAIL
-- پرداخت برای رزروهای تیکت 19 (Tehran to Isfahan - اتوبوس، قیمت: 600000)
('user8888', 91, 600000, 'PAID', '2025-05-20 10:15:00', 'WALLET'), -- user8888: PHONE_NUMBER
('user8989', 92, 600000, 'PAID', '2025-05-20 12:15:00', 'CREDIT_CARD'), -- user8989: EMAIL
('user9090', 93, 600000, 'PAID', '2025-05-21 09:15:00', 'WALLET'), -- user9090: PHONE_NUMBER
('user9191', 94, 600000, 'PAID', '2025-05-21 11:15:00', 'CREDIT_CARD'), -- user9191: EMAIL
('user9292', 95, 600000, 'PAID', '2025-05-22 08:15:00', 'WALLET'), -- user9292: PHONE_NUMBER
-- پرداخت برای رزروهای تیکت 20 (Isfahan to Tehran - اتوبوس، قیمت: 600000)
('user9393', 96, 600000, 'PAID', '2025-05-21 10:15:00', 'CREDIT_CARD'), -- user9393: EMAIL
('user9494', 97, 600000, 'PAID', '2025-05-21 12:15:00', 'WALLET'), -- user9494: PHONE_NUMBER
('user9595', 98, 600000, 'PAID', '2025-05-22 09:15:00', 'CREDIT_CARD'), -- user9595: EMAIL
('ali123', 99, 600000, 'PAID', '2025-05-22 11:15:00', 'CREDIT_CARD'), -- ali123: EMAIL
('sara456', 100, 600000, 'PAID', '2025-05-23 08:15:00', 'WALLET'); -- sara456: PHONE_NUMBER


-- افزودن تاریخچه رزروها (100 سطر)
INSERT INTO reservations_history (username, reservation_id, date_and_time, operation_type) VALUES
-- تاریخچه برای رزروهای تیکت 1 (Tehran to Mashhad - پرواز)
('ali123', 1, '2025-05-02 10:15:00', 'BUY'),
('sara456', 2, '2025-05-02 12:15:00', 'BUY'),
('mohammad789', 3, '2025-05-03 09:15:00', 'BUY'),
('zahra101', 4, '2025-05-03 11:15:00', 'BUY'),
('reza202', 5, '2025-05-04 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 2 (Tehran to Shiraz - پرواز)
('leila303', 6, '2025-05-03 10:15:00', 'BUY'),
('hassan404', 7, '2025-05-03 12:15:00', 'BUY'),
('nazanin505', 8, '2025-05-04 09:15:00', 'BUY'),
('amir606', 9, '2025-05-04 11:15:00', 'BUY'),
('fateme707', 10, '2025-05-05 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 3 (Tehran to Tabriz - پرواز)
('ahmad808', 11, '2025-05-04 10:15:00', 'BUY'),
('mahsa909', 12, '2025-05-04 12:15:00', 'BUY'),
('kaveh1010', 13, '2025-05-05 09:15:00', 'BUY'),
('sima1111', 14, '2025-05-05 11:15:00', 'BUY'),
('behnam1212', 15, '2025-05-06 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 4 (Tehran to Ahvaz - پرواز)
('parisa1313', 16, '2025-05-05 10:15:00', 'BUY'),
('kamran1414', 17, '2025-05-05 12:15:00', 'BUY'),
('niloofar1515', 18, '2025-05-06 09:15:00', 'BUY'),
('arash1616', 19, '2025-05-06 11:15:00', 'BUY'),
('shirin1717', 20, '2025-05-07 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 5 (Tehran to Kermanshah - پرواز)
('user1818', 21, '2025-05-06 10:15:00', 'BUY'),
('user1919', 22, '2025-05-06 12:15:00', 'BUY'),
('user2020', 23, '2025-05-07 09:15:00', 'BUY'),
('user2121', 24, '2025-05-07 11:15:00', 'BUY'),
('user2222', 25, '2025-05-08 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 6 (Mashhad to Tehran - پرواز)
('user2323', 26, '2025-05-07 10:15:00', 'BUY'),
('user2424', 27, '2025-05-07 12:15:00', 'BUY'),
('user2525', 28, '2025-05-08 09:15:00', 'BUY'),
('user2626', 29, '2025-05-08 11:15:00', 'BUY'),
('user2727', 30, '2025-05-09 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 7 (Shiraz to Tabriz - پرواز)
('user2828', 31, '2025-05-08 10:15:00', 'BUY'),
('user2929', 32, '2025-05-08 12:15:00', 'BUY'),
('user3030', 33, '2025-05-09 09:15:00', 'BUY'),
('user3131', 34, '2025-05-09 11:15:00', 'BUY'),
('user3232', 35, '2025-05-10 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 8 (Ahvaz to Kermanshah - پرواز)
('user3333', 36, '2025-05-09 10:15:00', 'BUY'),
('user3434', 37, '2025-05-09 12:15:00', 'BUY'),
('user3535', 38, '2025-05-10 09:15:00', 'BUY'),
('user3636', 39, '2025-05-10 11:15:00', 'BUY'),
('user3737', 40, '2025-05-11 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 9 (Tehran to Kerman - پرواز)
('user3838', 41, '2025-05-10 10:15:00', 'BUY'),
('user3939', 42, '2025-05-10 12:15:00', 'BUY'),
('user4040', 43, '2025-05-11 09:15:00', 'BUY'),
('user4141', 44, '2025-05-11 11:15:00', 'BUY'),
('user4242', 45, '2025-05-12 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 10 (Kerman to Tehran - پرواز)
('user4343', 46, '2025-05-11 10:15:00', 'BUY'),
('user4444', 47, '2025-05-11 12:15:00', 'BUY'),
('user4545', 48, '2025-05-12 09:15:00', 'BUY'),
('user4646', 49, '2025-05-12 11:15:00', 'BUY'),
('user4747', 50, '2025-05-13 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 11 (Tehran to Shiraz - قطار)
('user4848', 51, '2025-05-12 10:15:00', 'BUY'),
('user4949', 52, '2025-05-12 12:15:00', 'BUY'),
('user5050', 53, '2025-05-13 09:15:00', 'BUY'),
('user5151', 54, '2025-05-13 11:15:00', 'BUY'),
('user5252', 55, '2025-05-14 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 12 (Tehran to Mashhad - قطار)
('user5353', 56, '2025-05-13 10:15:00', 'BUY'),
('user5454', 57, '2025-05-13 12:15:00', 'BUY'),
('user5555', 58, '2025-05-14 09:15:00', 'BUY'),
('user5656', 59, '2025-05-14 11:15:00', 'BUY'),
('user5757', 60, '2025-05-15 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 13 (Tehran to Tabriz - قطار)
('user5858', 61, '2025-05-14 10:15:00', 'BUY'),
('user5959', 62, '2025-05-14 12:15:00', 'BUY'),
('user6060', 63, '2025-05-15 09:15:00', 'BUY'),
('user6161', 64, '2025-05-15 11:15:00', 'BUY'),
('user6262', 65, '2025-05-16 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 14 (Tehran to Ahvaz - قطار)
('user6363', 66, '2025-05-15 10:15:00', 'BUY'),
('user6464', 67, '2025-05-15 12:15:00', 'BUY'),
('user6565', 68, '2025-05-16 09:15:00', 'BUY'),
('user6666', 69, '2025-05-16 11:15:00', 'BUY'),
('user6767', 70, '2025-05-17 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 15 (Mashhad to Tehran - قطار)
('user6868', 71, '2025-05-16 10:15:00', 'BUY'),
('user6969', 72, '2025-05-16 12:15:00', 'BUY'),
('user7070', 73, '2025-05-17 09:15:00', 'BUY'),
('user7171', 74, '2025-05-17 11:15:00', 'BUY'),
('user7272', 75, '2025-05-18 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 16 (Tehran to Karaj - اتوبوس)
('user7373', 76, '2025-05-17 10:15:00', 'BUY'),
('user7474', 77, '2025-05-17 12:15:00', 'BUY'),
('user7575', 78, '2025-05-18 09:15:00', 'BUY'),
('user7676', 79, '2025-05-18 11:15:00', 'BUY'),
('user7777', 80, '2025-05-19 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 17 (Tehran to Varamin - اتوبوس)
('user7878', 81, '2025-05-18 10:15:00', 'BUY'),
('user7979', 82, '2025-05-18 12:15:00', 'BUY'),
('user8080', 83, '2025-05-19 09:15:00', 'BUY'),
('user8181', 84, '2025-05-19 11:15:00', 'BUY'),
('user8282', 85, '2025-05-20 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 18 (Tehran to Rey - اتوبوس)
('user8383', 86, '2025-05-19 10:15:00', 'BUY'),
('user8484', 87, '2025-05-19 12:15:00', 'BUY'),
('user8585', 88, '2025-05-20 09:15:00', 'BUY'),
('user8686', 89, '2025-05-20 11:15:00', 'BUY'),
('user8787', 90, '2025-05-21 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 19 (Tehran to Isfahan - اتوبوس)
('user8888', 91, '2025-05-20 10:15:00', 'BUY'),
('user8989', 92, '2025-05-20 12:15:00', 'BUY'),
('user9090', 93, '2025-05-21 09:15:00', 'BUY'),
('user9191', 94, '2025-05-21 11:15:00', 'BUY'),
('user9292', 95, '2025-05-22 08:15:00', 'BUY'),
-- تاریخچه برای رزروهای تیکت 20 (Isfahan to Tehran - اتوبوس)
('user9393', 96, '2025-05-21 10:15:00', 'BUY'),
('user9494', 97, '2025-05-21 12:15:00', 'BUY'),
('user9595', 98, '2025-05-22 09:15:00', 'BUY'),
('ali123', 99, '2025-05-22 11:15:00', 'BUY'),
('sara456', 100, '2025-05-23 08:15:00', 'BUY');

update reservations_history
set "reservation_history_status" = 'SUCCESSFUL'


-- افزودن 30 گزارش
INSERT INTO reports (username, reservation_id, report_type, report_text) VALUES
-- گزارش‌های نوع PAYMENT
('ali123', 1, 'PAYMENT', 'پرداخت من دو بار کسر شده است، لطفاً بررسی کنید.'),
('sara456', 2, 'PAYMENT', 'مبلغ پرداخت با تیکت مطابقت ندارد.'),
('mohammad789', 3, 'PAYMENT', 'تراکنش پرداخت ناموفق بود اما رزرو ثبت شده است.'),
-- گزارش‌های نوع TRAVEL_DELAY
('zahra101', 4, 'TRAVEL_DELAY', 'پرواز تأخیر داشته و به موقع حرکت نکرد.'),
('reza202', 5, 'TRAVEL_DELAY', 'قطار با تأخیر 2 ساعته رسید.'),
('leila303', 6, 'TRAVEL_DELAY', 'اتوبوس هنوز به مقصد نرسیده است.'),
-- گزارش‌های نوع CANCEL
('hassan404', 7, 'CANCEL', 'می‌خواهم رزرو را لغو کنم، لطفاً کمک کنید.'),
('nazanin505', 8, 'CANCEL', 'رزرو به اشتباه ثبت شده، نیاز به لغو دارم.'),
('amir606', 9, 'CANCEL', 'تاریخ سفر اشتباه است، درخواست لغو دارم.'),
-- گزارش‌های نوع OTHER
('fateme707', 10, 'OTHER', 'اطلاعات صندلی برایم ارسال نشده است.'),
('ahmad808', 11, 'OTHER', 'نیاز به اطلاعات بیشتر درباره مسیر دارم.'),
('mahsa909', 12, 'OTHER', 'مشکل در دسترسی به بلیط الکترونیکی.'),
-- گزارش‌های نوع PAYMENT
('kaveh1010', 13, 'PAYMENT', 'پرداخت با کارت اعتباری انجام نشد.'),
('sima1111', 14, 'PAYMENT', 'مبلغ اضافی از حسابم کسر شده است.'),
('behnam1212', 15, 'PAYMENT', 'درخواست بازپرداخت دارم.'),
-- گزارش‌های نوع TRAVEL_DELAY
('parisa1313', 16, 'TRAVEL_DELAY', 'پرواز 3 ساعت تأخیر داشت.'),
('kamran1414', 17, 'TRAVEL_DELAY', 'قطار با تأخیر به ایستگاه رسید.'),
('niloofar1515', 18, 'TRAVEL_DELAY', 'اتوبوس طبق برنامه حرکت نکرد.'),
-- گزارش‌های نوع CANCEL
('arash1616', 19, 'CANCEL', 'نیاز به لغو فوری رزرو دارم.'),
('shirin1717', 20, 'CANCEL', 'رزرو را به اشتباه انجام داده‌ام.'),
('user1818', 21, 'CANCEL', 'تاریخ سفر تغییر کرده، درخواست لغو.'),
-- گزارش‌های نوع OTHER
('user1919', 22, 'OTHER', 'شماره بلیط برایم ارسال نشده است.'),
('user2020', 23, 'OTHER', 'نیاز به پشتیبانی برای تغییر صندلی دارم.'),
('user2121', 24, 'OTHER', 'لینک بلیط کار نمی‌کند.'),
-- گزارش‌های نوع PAYMENT
('user2222', 25, 'PAYMENT', 'پرداخت با کیف پول مشکل دارد.'),
('user2323', 26, 'PAYMENT', 'تراکنش ناموفق بود، اما رزرو فعال است.'),
('user2424', 27, 'PAYMENT', 'درخواست بررسی تراکنش.'),
-- گزارش‌های نوع TRAVEL_DELAY
('user2525', 28, 'TRAVEL_DELAY', 'پرواز با تأخیر 4 ساعته مواجه شد.'),
('user2626', 29, 'TRAVEL_DELAY', 'قطار هنوز به مقصد نرسیده است.'),
('user2727', 30, 'TRAVEL_DELAY', 'اتوبوس با تأخیر حرکت کرد.'),
-- گزارش‌های نوع CANCEL
('user2828', 31, 'CANCEL', 'نیاز به لغو رزرو به دلیل تغییر برنامه.'),
('user2929', 32, 'CANCEL', 'رزرو را به اشتباه ثبت کرده‌ام.');

-- new data
INSERT INTO users (username, password, user_role, name, email, phone_number, city, authentication_method) VALUES
('mehdi2121', 'hashed_password_101', 'USER', 'Mehdi Shariati', 'mehdi.shariati@email.com', '09201112233', 2, 'EMAIL'),
('narges2222', 'hashed_password_102', 'USER', 'Narges Bahrami', 'narges.bahrami@email.com', '09214445566', 3, 'PHONE_NUMBER'),
('yasin2323', 'hashed_password_103', 'USER', 'Yasin Ghaffari', 'yasin.ghaffari@email.com', '09227778899', 4, 'EMAIL'),
('sanaz2424', 'hashed_password_104', 'USER', 'Sanaz Mousavi', 'sanaz.mousavi@email.com', '09230001122', 5, 'PHONE_NUMBER'),
('omid2525', 'hashed_password_105', 'USER', 'Omid Shokri', 'omid.shokri@email.com', '09243334455', 6, 'EMAIL'),
('bahar2626', 'hashed_password_106', 'USER', 'Bahar Azizi', 'bahar.azizi@email.com', '09256667788', 7, 'PHONE_NUMBER'),
('kianoush2727', 'hashed_password_107', 'USER', 'Kianoush Farhadi', 'kianoush.farhadi@email.com', '09269990011', 8, 'EMAIL'),
('elnaz2828', 'hashed_password_108', 'USER', 'Elnaz Gholami', 'elnaz.gholami@email.com', '09272223344', 9, 'PHONE_NUMBER'),
('pouya2929', 'hashed_password_109', 'USER', 'Pouya Khosravi', 'pouya.khosravi@email.com', '09285556677', 10, 'EMAIL'),
('setareh3030', 'hashed_password_110', 'USER', 'Setareh Esmaili', 'setareh.esmaili@email.com', '09298889900', 11, 'PHONE_NUMBER'),
('shayan3131', 'hashed_password_111', 'USER', 'Shayan Rahmani', 'shayan.rahmani@email.com', '09301112234', 12, 'EMAIL'),
('hanieh3232', 'hashed_password_112', 'USER', 'Hanieh Shariati', 'hanieh.shariati@email.com', '09314445567', 13, 'PHONE_NUMBER'),
('babak3333', 'hashed_password_113', 'USER', 'Babak Ghaffari', 'babak.ghaffari@email.com', '09327778890', 14, 'EMAIL'),
('golnaz3434', 'hashed_password_114', 'USER', 'Golnaz Mousavi', 'golnaz.mousavi@email.com', '09330001123', 15, 'PHONE_NUMBER'),
('farhad3535', 'hashed_password_115', 'USER', 'Farhad Shokri', 'farhad.shokri@email.com', '09343334456', 16, 'EMAIL'),
('mahtab3636', 'hashed_password_116', 'USER', 'Mahtab Azizi', 'mahtab.azizi@email.com', '09356667789', 17, 'PHONE_NUMBER'),
('rostam3737', 'hashed_password_117', 'USER', 'Rostam Farhadi', 'rostam.farhadi@email.com', '09369990012', 18, 'EMAIL'),
('taraneh3838', 'hashed_password_118', 'USER', 'Taraneh Gholami', 'taraneh.gholami@email.com', '09372223345', 19, 'PHONE_NUMBER'),
('khashayar3939', 'hashed_password_119', 'USER', 'Khashayar Khosravi', 'khashayar.khosravi@email.com', '09385556678', 20, 'EMAIL'),
('parvaneh4040', 'hashed_password_120', 'USER', 'Parvaneh Esmaili', 'parvaneh.esmaili@email.com', '09398889901', 21, 'PHONE_NUMBER');

INSERT INTO tickets (vehicle_id, origin_location_id, destination_location_id, departure_start, departure_end, price,total_capacity, remaining_capacity) VALUES
(76,1,12, '2025-04-10 08:30:00', '2025-04-10 14:00:00', 3000000, 10, 3);

INSERT INTO reservations (username, ticket_id, reservation_status, date_and_time_of_reservation, reservation_seat) VALUES
('mehdi2121', 21,'RESERVED', '2025-4-8 10:00:00', 1),
('mehdi2121', 21,'RESERVED', '2025-4-8 10:00:00', 2),
('mehdi2121', 21,'RESERVED', '2025-4-8 10:00:00', 3),
('narges2222', 21,'RESERVED', '2025-4-7 20:00:00', 4),
('narges2222', 21,'RESERVED', '2025-4-7 20:00:00', 5),
('elnaz2828', 21,'RESERVED', '2025-4-9 02:00:00', 6),
('golnaz3434', 21,'RESERVED', '2025-4-9 23:00:00', 7),
(NULL, 21,'NOT_RESERVED', null, 8),
(NULL, 21,'NOT_RESERVED', null, 9),
(NULL, 21,'NOT_RESERVED', null, 10);

INSERT INTO payments (username, reservation_id, amount_paid, payment_status, date_and_time_of_payment, payment_method) VALUES
('mehdi2121', 101, 3000000, 'PAID', '2025-04-08 10:07:00', 'CREDIT_CARD'),
('mehdi2121', 102, 3000000, 'PAID', '2025-04-08 10:07:00', 'CREDIT_CARD'),
('mehdi2121', 103, 3000000, 'PAID', '2025-04-08 10:07:00', 'CREDIT_CARD'),
('narges2222', 104, 3000000, 'NOT_PAID', '2025-04-07 16:30:00', 'WALLET'),
('narges2222', 104, 3000000, 'PAID', '2025-04-07 20:10:00', 'CREDIT_CARD'),
('narges2222', 105, 3000000, 'PAID', '2025-04-07 20:10:00', 'CREDIT_CARD'),
('elnaz2828', 106, 3000000, 'PAID', '2025-04-09 02:05:00', 'CREDIT_CARD'),
('golnaz3434', 107, 3000000, 'PAID', '2025-04-09 23:01:00', 'CREDIT_CARD');

INSERT INTO reservations_history (username, reservation_id, date_and_time, operation_type, reservation_history_status) VALUES
('mehdi2121', 101,  '2025-04-08 10:07:00', 'BUY', 'SUCCESSFUL'),
('mehdi2121', 102,  '2025-04-08 10:07:00', 'BUY', 'SUCCESSFUL'),
('mehdi2121', 103,  '2025-04-08 10:07:00', 'BUY', 'SUCCESSFUL'),
('narges2222', 104,  '2025-04-07 16:30:00', 'BUY', 'UNSUCCESSFUL'),
('narges2222', 104,  '2025-04-07 20:10:00', 'BUY', 'SUCCESSFUL'),
('narges2222', 105,  '2025-04-07 20:10:00', 'BUY', 'SUCCESSFUL'),
('elnaz2828', 106,  '2025-04-09 02:05:00', 'BUY', 'SUCCESSFUL'),
('golnaz3434', 107,  '2025-04-09 23:01:00', 'BUY', 'SUCCESSFUL');
