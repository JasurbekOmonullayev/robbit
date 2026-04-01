# Excel -> ClickUp Sync Dokumentatsiya

## 1) Maqsad
`Jiddi_lead.xlsx` faylidagi `baza` sheet ma'lumotlarini ClickUp ga avtomatik yuborish.

Asosiy talablar:
- Har `2 soat`da ishga tushsin.
- Har ishga tushganda faqat yangi leadlar yuborilsin.
- Deduplikatsiya kaliti: `2. Lead ID`.
- Agar `Lead ID` ClickUp da allaqachon mavjud bo'lsa, qayta task yaratilmasin.
- Agar `Lead ID` yo'q bo'lsa, yangi task yaratiladi.

## 2) Excel strukturasi

### `baza` sheet (manba)
Asosiy ustunlar:
- `SANA`
- `2. Lead ID`
- `3. Ismingizni kiriting!`
- `4. Bog'lanish uchun telefon raqamingizni yozing!`
- `5. Phone number`
- `6. Siz biznes egasimisiz?`
- `7. Biznesingiz qayerda faoliyat yuritadi?`
- `8. Marketing uchun byudjetingiz qancha atrofida?`
- `9. Biznesingiz qaysi yo'nalish/sohada? (ta'lim, sayohat, tovar, bad, consulting, ishlab chiqarish)`
- `10. Источник`
- `11. Ad Name`
- `12. Статус`

### `columns` sheet (mapping)
Ustunlar:
- `sheets_columns_name`
- `clickup_columns_name`
- `clickup_column_id`

`columns` sheet Excel ustunini ClickUp custom field bilan bog'lash uchun ishlatiladi.

## 3) Aniqlangan mapping

| Excel (`sheets_columns_name`) | ClickUp (`clickup_columns_name`) | `clickup_column_id` |
|---|---|---|
| SANA | Sana | 3c9400f1-0fb2-433e-a05e-e39686bac778 |
| 2. Lead ID | Lead ID | 5dcd1a73-7d90-469c-9488-cb78fe479dbf |
| 3. Ismingizni kiriting! | Name | (bo'sh) |
| 4. Bog'lanish uchun telefon raqamingizni yozing! | Contact Phone Number | 198c281d-f07d-4c03-91c5-cf5a6104e74d |
| 5. Phone number | Telefon raqam | e012967a-7b6f-4790-a16d-140a9e5295f9 |
| 6. Siz biznes egasimisiz? | Siz biznes egasimisiz? | cecc463a-9ce4-4c07-a611-05a95f4bf195 |
| 7. Biznesingiz qayerda faoliyat yuritadi? | Biznesingiz qayerda faoliyat yuritadi? | 3889cd08-95df-4714-b6f6-3c662ed1ecf8 |
| 8. Marketing uchun byudjetingiz qancha atrofida? | Marketing uchun byudjetingiz qancha atrofida? | c363d4e1-eb37-4d29-a24e-a21d2816bc1b |
| 9. Biznesingiz qaysi yo'nalish/sohada? (ta'lim, sayohat, tovar, bad, consulting, ishlab chiqarish) | Biznesingiz qaysi yo'nalish/sohada? (ta'lim, sayohat, tovar, bad, consulting, ishlab chiqarish) | a7228d6f-3569-417f-abb9-a16d9be73e92 |
| 10. Источник | Источник | 9ffb167e-bc8f-4fb4-9175-1733154aa3f8 |
| 11. Ad Name | Ad Name | 8d70e073-5145-4fca-892f-08184adabfa4 |

Izoh:
- `3. Ismingizni kiriting! -> Name` uchun `clickup_column_id` bo'sh. Bu odatda task nomiga (`task.name`) yoziladi, custom field emas.

## 4) Sync algoritmi

1. `columns` sheetdan mappingni o'qish.
2. `baza` sheetdagi barcha satrlarni o'qish.
3. Har satr uchun:
   - `Lead ID` ni olish (`2. Lead ID`).
   - Bo'sh bo'lsa satrni tashlab ketish.
4. ClickUp listdagi mavjud tasklardan `Lead ID` custom field qiymatlarini yig'ish.
5. Agar joriy `Lead ID` mavjud to'plamda bo'lsa: `skip`.
6. Aks holda yangi task yaratish:
   - `task.name`: `3. Ismingizni kiriting!` (bo'sh bo'lsa `Lead <Lead ID>`)
   - `custom_fields`: `columns` sheetdagi `clickup_column_id` mavjud bo'lgan fieldlar.
7. Yaratilgan tasklardan keyin logga yozish (`created/skipped/errors`).

## 5) Deduplikatsiya qoidasi (eng muhim)

- Bitta va yagona kalit: `Lead ID` (`2. Lead ID`).
- Tekshiruv manbasi: ClickUp ichidagi `Lead ID` custom field.
- Natija:
  - mavjud bo'lsa: create qilinmaydi
  - mavjud bo'lmasa: create qilinadi

Bu yondashuv har 2 soatlik ishga tushishda takroriy task yaratishni oldini oladi.

## 6) Har 2 soatda ishga tushirish

Variantlar:
- Windows Task Scheduler: scriptni har 2 soatda ishga tushiradi.
- Yoki serverda cron/PM2/APScheduler interval bilan.

Minimal tavsiya:
- Scheduler scriptni `00:00`, `02:00`, `04:00` ... da ishga tushirsin.
- Har run alohida bo'lgani uchun xotira yo'qolsa ham deduplikatsiya ClickUp tekshiruvi orqali saqlanadi.

## 7) API darajasida yuboriladigan data

Har yangi lead uchun ClickUp ga:
- `name`: lead ismi
- `custom_fields`: mapping bo'yicha qiymatlar
- `Lead ID` custom field: albatta yuboriladi

## 8) Xatoliklarni boshqarish

- API xatoligida retry (masalan 3 marta, exponential backoff).
- Excelda bo'sh yoki noto'g'ri satrlarni loglab skip qilish.
- Run yakunida summary:
  - `read_count`
  - `created_count`
  - `skipped_count`
  - `error_count`

## 9) Keyingi implementatsiya rejasi

1. Script (`sync_excel_to_clickup`) yoziladi.
2. `.env` orqali token va list ma'lumotlari olinadi.
3. Dry-run rejimi bilan test qilinadi.
4. Real create yoqiladi.
5. Task Scheduler ga ulanadi.

## 10) Sizdan kerak bo'ladigan ma'lumotlar

Ishga tushirish uchun quyidagilar kerak:

1. ClickUp API token.
2. Qaysi Space/Folder/List ga task qo'shilishi (`list_id`).
3. `Lead ID` custom field aynan `5dcd1a73-7d90-469c-9488-cb78fe479dbf` ekanini tasdiq.
4. `SANA` field turi ClickUp da qanday (`date` yoki `text`) ekanini tasdiq.
5. `12. Статус` ham yuboriladimi yoki yo'qmi (hozir mappingda yo'q).
6. Task nomi sifatida doim `3. Ismingizni kiriting!` ishlatilsinmi.
7. Scriptni qaysi muhitda ishlatamiz:
   - sizning kompyuterda (Windows Task Scheduler)
   - yoki server/VPS da.

---

Agar xohlasangiz, keyingi bosqichda shu hujjat asosida to'liq ishlaydigan scriptni yozib, test rejimida ishga tushirib beraman.
