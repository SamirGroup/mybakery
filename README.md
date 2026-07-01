# 📱 Telefonlar katalogi — Telegram bot

Aiogram 3 + SQLAlchemy (async) + FastAPI asosida qurilgan namunaviy bot. Mijozlar telefonlar
katalogini kategoriyalar bo'yicha ko'rishi, qidirishi va buyurtma berishi mumkin. Admin botning
o'zi ichida kategoriya/mahsulot qo'shishi, tahrirlashi va o'chirishi mumkin.

## Imkoniyatlar

- 📂 Kategoriyalar va ularga tegishli telefonlar (nomi, narxi, tavsifi, soni, rasmi)
- 🔍 Nom bo'yicha qidiruv
- 🛒 "Buyurtma berish" — mijoz kontaktini adminlarga xabar sifatida yuboradi
- 🛠 To'liq admin panel (botning o'zida, alohida saytsiz):
  - kategoriya qo'shish / o'chirish
  - telefon qo'shish (kategoriya, nomi, tavsifi, narxi, soni, rasmi)
  - telefonni tahrirlash (har bir maydon alohida) va faol/nofaol qilish
  - telefonni o'chirish
- Ikki xil ishga tushirish rejimi:
  - **Polling** — local kompyuter yoki har qanday serverda (`main.py`)
  - **Webhook** — Vercel'da serverless (`api/index.py`, FastAPI)

## Loyiha tuzilishi

```
phone-bot/
├── bot/
│   ├── config.py            # .env dan sozlamalar
│   ├── core.py               # Bot/Dispatcher yaratish
│   ├── states.py             # FSM holatlari
│   ├── filters.py            # IsAdmin filtri
│   ├── utils.py               # narx formatlash va h.k.
│   ├── database/
│   │   ├── models.py          # Category, Product (SQLAlchemy)
│   │   ├── engine.py          # async engine/session, init_db
│   │   └── requests.py        # DB bilan ishlash funksiyalari
│   ├── keyboards/
│   │   ├── callbacks.py       # CallbackData klasslari
│   │   ├── user.py            # mijoz uchun tugmalar
│   │   └── admin.py           # admin uchun tugmalar
│   └── handlers/
│       ├── user.py            # katalog, qidiruv, buyurtma
│       └── admin.py           # CRUD, FSM formalar
├── api/
│   └── index.py               # Vercel uchun FastAPI webhook
├── scripts/
│   ├── set_webhook.py
│   └── delete_webhook.py
├── main.py                    # local polling
├── vercel.json
├── requirements.txt
└── .env.example
```

## 1. Local ishga tushirish (polling)

1. Python 3.11+ o'rnatilgan bo'lishi kerak.
2. Virtual muhit yarating va bog'liqliklarni o'rnating:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```

3. `.env.example` faylidan nusxa olib `.env` yarating:

   ```bash
   copy .env.example .env
   ```

4. `.env` faylida:
   - `BOT_TOKEN` — @BotFather'dan olingan token
   - `ADMIN_IDS` — sizning Telegram ID'ingiz (@userinfobot orqali bilib olishingiz mumkin)
   - Qolganlarini local uchun bo'sh qoldiring (default: SQLite + xotiradagi FSM)

5. Botni ishga tushiring:

   ```bash
   python main.py
   ```

6. Telegram'da botga `/start` yozing. Admin sifatida `/admin` buyrug'ini yuboring — admin panel
   ochiladi (faqat `ADMIN_IDS` ichidagi ID'lar uchun ishlaydi).

Ma'lumotlar bazasi avtomatik yaratiladi: `phone_bot.db` (SQLite fayli).

## 2. Vercel'da production (webhook)

Vercel'ning serverless funksiyalari **statsiz** ishlaydi: har bir so'rov alohida (ba'zan yangi)
jarayonda ishlashi, va lokal fayl tizimi doimiy saqlanmasligi mumkin. Shu sababli productionda:

- **Ma'lumotlar bazasi**: SQLite ishlatib bo'lmaydi — tashqi Postgres kerak. Bepul variant:
  [Neon](https://neon.tech) yoki [Supabase](https://supabase.com). Ular bergan connection
  string'ni shu ko'rinishga o'tkazing va `DATABASE_URL`ga qo'ying:

  ```
  postgresql+asyncpg://USER:PASSWORD@HOST/DBNAME
  ```

- **Admin formalar holati (FSM)**: xotirada saqlab bo'lmaydi (har chaqiriqda yo'qolishi mumkin).
  Bepul [Upstash Redis](https://upstash.com) oling va uning `REDIS_URL`sini (`rediss://...`)
  `.env`/Vercel Environment Variables ichiga qo'ying. Agar `REDIS_URL` bo'sh bo'lsa, bot avtomatik
  xotiradagi (MemoryStorage) rejimga o'tadi — bu faqat local polling uchun yaroqli.

- **Rasmlar**: alohida fayl serveriga hojat yo'q — bot Telegram yuborgan rasmning `file_id`sini
  saqlaydi, Telegram CDN'idan o'zi ko'rsatadi.

### Deploy qadamlari

1. Loyihani GitHub'ga push qiling.
2. [vercel.com](https://vercel.com) da "New Project" → shu repo'ni tanlang. Framework avtomatik
   aniqlanadi (Python/FastAPI).
3. Environment Variables bo'limida quyidagilarni qo'shing:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `DATABASE_URL` (Postgres, yuqoridagi format)
   - `REDIS_URL` (Upstash)
   - `WEBHOOK_URL` = `https://<loyiha-nomi>.vercel.app/api/webhook`
   - `WEBHOOK_SECRET` (o'zingiz o'ylab topgan istalgan tasodifiy satr — xavfsizlik uchun)
4. Deploy tugagach, local kompyuteringizda (`.env` faylida ham xuddi shu qiymatlar bilan)
   quyidagini bir marta ishga tushiring — bu Telegram'ga "endi shu URL'ga xabar yuborib tur" deb
   aytadi:

   ```bash
   python -m scripts.set_webhook
   ```

5. Botga `/start` yozib tekshiring. Agar qaytadan local polling rejimiga o'tmoqchi bo'lsangiz:

   ```bash
   python -m scripts.delete_webhook
   ```

## Eslatma

Bu — mustaqil demo/na'muna loyiha. Haqiqiy do'kon uchun to'lov tizimi (Payme/Click), buyurtmalar
tarixi jadvali, statistik hisobotlar kabi qo'shimcha funksiyalarni xohishga qarab ustiga qurish
mumkin.
