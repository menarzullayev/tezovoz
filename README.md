Sizning talabingiz bo'yicha, loyihani rivojlantirish uchun taklif qilingan 50 ta yangilanish va ularni amalga oshirish uchun zarur bo'lgan fayllar ro'yxatini tuzib chiqdim.

### 👥 Foydalanuvchi Boshqaruvi
1.  **Foydalanuvchining to‘liq profili sahifasini yaratish:** `ovoz/app/handlers/users/account.py` (o'zgartirish), `ovoz/app/keyboards/reply/main_menu.py` (o'zgartirish).
2.  **Foydalanuvchiga o‘zining shaxsiy ma’lumotlarini o‘zgartirish imkoniyatini berish:** `ovoz/app/fsm/user_profile.py` (yaratish), `ovoz/app/handlers/users/profile.py` (yaratish), `ovoz/app/db/queries/user_crud_queries.py` (o'zgartirish).
3.  **Foydalanuvchi hisobini o‘chirish funksiyasini berish:** `ovoz/app/handlers/users/account.py` (o'zgartirish), `ovoz/app/db/queries/user_crud_queries.py` (yaratish).
4.  **Foydalanuvchining oxirgi faollik vaqtini saqlash:** `ovoz/app/db/models/users.py` (o'zgartirish), `ovoz/app/middlewares/user_registration.py` (o'zgartirish).
5.  **Foydalanuvchi ro‘yxatdan o‘tgan sanani ko‘rsatish:** `ovoz/app/handlers/users/account.py` (o'zgartirish).
6.  **Har bir foydalanuvchiga unikal taklifnoma kodi berish:** `ovoz/app/db/models/users.py` (o'zgartirish), `ovoz/app/db/queries/user_crud_queries.py` (o'zgartirish), `ovoz/app/handlers/users/referral.py` (o'zgartirish).
7.  **Foydalanuvchining shaxsiy referral kodini o‘zgartirish:** `ovoz/app/fsm/user_profile.py` (yaratish), `ovoz/app/handlers/users/profile.py` (yaratish), `ovoz/app/db/models/users.py` (o'zgartirish).
8.  **Foydalanuvchilarning joylashuvini saqlash:** `ovoz/app/db/models/users.py` (o'zgartirish), `ovoz/app/fsm/user_profile.py` (yaratish), `ovoz/app/handlers/users/profile.py` (yaratish).
9.  **Balansni ko‘rsatishda umumiy pul yechish summasini aks ettirish:** `ovoz/app/handlers/users/account.py` (o'zgartirish), `ovoz/app/db/models/payment.py` (o'zgartirish), `ovoz/app/db/queries/payment_queries.py` (yaratish).
10. **Foydalanuvchi botdan bloklanganda bildirishnoma yuborish:** `ovoz/app/handlers/admin/user_management.py` (yaratish), `ovoz/app/utils/admin_utils.py` (o'zgartirish).

### 🗳️ Ovoz Berish Tizimi
11. **Ovoz berish tarixini ko‘rish funksiyasini yaratish:** `ovoz/app/handlers/users/account.py` (o'zgartirish), `ovoz/app/db/queries/vote_queries.py` (yaratish).
12. **Ovoz berishni bir necha bosqichga bo‘lish:** `ovoz/app/fsm/voting_fsm.py` (o'zgartirish), `ovoz/app/handlers/users/auto_vote_handlers.py` (o'zgartirish).
13. **Ovoz berishda tasdiqlash tugmasini qo‘shish:** `ovoz/app/keyboards/inline/voting_confirmation.py` (yaratish), `ovoz/app/handlers/users/auto_vote_handlers.py` (o'zgartirish).
14. **Har bir ovoz uchun foydalanuvchining IP manzilini saqlash:** `ovoz/app/db/models/votes.py` (o'zgartirish), `ovoz/app/middlewares/ip_logger.py` (yaratish), `ovoz/app/middlewares/__init__.py` (o'zgartirish).
15. **Takroriy ovoz berish uchun cheklovlar o‘rnatish:** `ovoz/app/middlewares/rate_limiter.py` (o'zgartirish), `ovoz/app/handlers/users/auto_vote_handlers.py` (o'zgartirish).
16. **Har bir ovoz uchun `device_info`ni saqlash:** `ovoz/app/db/models/votes.py` (o'zgartirish), `ovoz/app/middlewares/device_info.py` (yaratish), `ovoz/app/middlewares/__init__.py` (o'zgartirish).
17. **Avtomatik ovoz berishda xatolik yuz bersa, qo‘lda ovoz berish yo‘riqnomasini yuborish:** `ovoz/app/handlers/users/auto_vote_handlers.py` (o'zgartirish).
18. **CAPTCHA kiritishda xatolik yuz bersa, qayta urinish imkoniyatini berish:** `ovoz/app/handlers/users/auto_vote_handlers.py` (o'zgartirish).
19. **OTP kodini qayta yuborish tugmasini qo‘shish:** `ovoz/app/handlers/users/auto_vote_handlers.py` (o'zgartirish), `ovoz/app/keyboards/reply/otp_keyboard.py` (yaratish).
20. **Ovoz berish jarayonida vaqt cheklovini o‘rnatish:** `ovoz/app/db/models/sessions.py` (o'zgartirish), `ovoz/app/middlewares/session_timeout.py` (yaratish).

### 🔐 Admin Paneli va Moderatsiya
21. **To‘liq Admin Paneli menyusini yaratish:** `ovoz/app/handlers/admin/admin_panel.py` (yaratish), `ovoz/app/keyboards/reply/admin_menu.py` (yaratish).
22. **Adminlar uchun foydalanuvchilarni qidirish:** `ovoz/app/fsm/admin.py` (yaratish), `ovoz/app/handlers/admin/user_management.py` (yaratish).
23. **Adminlar tomonidan foydalanuvchi balansini qo‘lda o‘zgartirish:** `ovoz/app/handlers/admin/user_management.py` (yaratish), `ovoz/app/db/queries/user_crud_queries.py` (o'zgartirish).
24. **Foydalanuvchini bloklash yoki blokdan chiqarish:** `ovoz/app/handlers/admin/user_management.py` (yaratish), `ovoz/app/db/models/users.py` (o'zgartirish).
25. **Adminlar o‘rtasida xabarlarni almashish uchun chat tizimi:** `ovoz/app/handlers/admin/admin_chat.py` (yaratish), `ovoz/app/db/models/admin_message.py` (yaratish).
26. **`stats` buyrug'ida ko‘rsatiladigan ma'lumotlarni sozlash:** `ovoz/app/handlers/admin/stats.py` (o'zgartirish), `ovoz/app/db/models/settings.py` (o'zgartirish).
27. **Dinamik sozlamalar (masalan, `VOTING_MODE`) ni o‘zgartirish:** `ovoz/app/handlers/admin/settings_handler.py` (o'zgartirish), `ovoz/app/db/queries/settings_queries.py` (yaratish).
28. **Pul yechish so‘rovlari uchun "izoh" maydoni qo‘shish:** `ovoz/app/handlers/admin/payment_verification.py` (o'zgartirish), `ovoz/app/db/models/payment.py` (o'zgartirish).
29. **Pul yechish so‘rovlarini turlari bo‘yicha filtrlash:** `ovoz/app/handlers/admin/payment_verification.py` (o'zgartirish).
30. **Pul yechish so‘rovlarini eksport qilish:** `ovoz/app/handlers/admin/payment_verification.py` (o'zgartirish), `ovoz/app/utils/data_exporter.py` (yaratish).
31. **Foydalanuvchilardan kelgan fikr-mulohazalar uchun yangi handlerlar:** `ovoz/app/handlers/admin/contact_handler.py` (yaratish), `ovoz/app/db/models/contact.py` (o'zgartirish).
32. **Adminlar uchun barcha ovozlar tarixini ko‘rish:** `ovoz/app/handlers/admin/stats.py` (o'zgartirish), `ovoz/app/db/queries/vote_queries.py` (yaratish).
33. **Bot statistikasini jadvallar shaklida vizualizatsiya qilish:** `ovoz/app/utils/data_visualizer.py` (yaratish), `ovoz/app/handlers/admin/stats.py` (o'zgartirish).

### 💰 Monetizatsiya va Promokodlar
34. **Promokod yaratish funksiyasini qo‘shish:** `ovoz/app/fsm/admin.py` (o'zgartirish), `ovoz/app/handlers/admin/promocode_handler.py` (yaratish).
35. **Promokodlarni faollashtirish va faolsizlantirish:** `ovoz/app/handlers/admin/promocode_handler.py` (o'zgartirish).
36. **Promokodlarni bir marta yoki ko‘p marta ishlatish:** `ovoz/app/db/models/promocode.py` (o'zgartirish).
37. **Foydalanuvchilarga promokod kiritish uchun buyruq:** `ovoz/app/fsm/promocode.py` (yaratish), `ovoz/app/handlers/users/promocode_handler.py` (yaratish).
38. **Promokod ishlatilganligi haqidagi ma'lumotni saqlash:** `ovoz/app/db/models/promocode.py` (o'zgartirish), `ovoz/app/handlers/users/promocode_handler.py` (o'zgartirish).

### 🐛 Xatolar va Monitoring
39. **Bot ichidagi barcha xatolarni ma'lumotlar bazasiga saqlash:** `ovoz/app/handlers/errors.py` (o'zgartirish).
40. **Maxsus xatoliklar uchun adminlarga avtomatik xabar yuborish:** `ovoz/app/handlers/errors.py` (o'zgartirish), `ovoz/app/utils/admin_utils.py` (o'zgartirish).
41. **`rate_limiter` faollashganda foydalanuvchiga xabar berish:** `ovoz/app/middlewares/rate_limiter.py` (o'zgartirish).
42. **Log fayllarni admin panelidan ko'rish yoki yuklab olish:** `ovoz/app/handlers/admin/log_handler.py` (yaratish), `ovoz/app/utils/file_utils.py` (yaratish).

### 🔗 Referral Tizimi
43. **Referral bonusini dinamik sozlamalardan olish:** `ovoz/app/db/queries/referral_queries.py` (o'zgartirish), `ovoz/app/db/models/settings.py` (o'zgartirish).
44. **Referral bonusini faqat birinchi muvaffaqiyatli ovoz uchun berish:** `ovoz/app/db/queries/referral_queries.py` (o'zgartirish).
45. **Referral havolani takroran jo‘natishda xatolik bermaslik:** `ovoz/app/handlers/users/referral.py` (o'zgartirish).
46. **Har bir referralning statusini kuzatish:** `ovoz/app/db/models/referral.py` (o'zgartirish).
47. **Taklif qiluvchiga uning do'stlari tomonidan qancha ovoz berilganini ko'rsatish:** `ovoz/app/handlers/users/referral.py` (o'zgartirish).
48. **Referral link orqali kelgan yangi foydalanuvchiga maxsus xabar:** `ovoz/app/handlers/users/language_selection.py` (o'zgartirish).

### 🚀 Boshqa funksiyalar
49. **Ovoz berish jarayoni uchun maxsus FSM holatlarini yaratish:** `ovoz/app/fsm/voting_fsm.py` (o'zgartirish).
50. **Har bir yangilanish uchun DB sessiyasini ta'minlash:** `ovoz/app/middlewares/db_session.py` (o'zgartirish).