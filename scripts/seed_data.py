import asyncio
import sys

from bot.database import requests as db
from bot.database.engine import init_db

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

CATEGORIES: dict[str, list[dict]] = {
    "Apple": [
        dict(name="iPhone 13 128GB", price=8_500_000, quantity=5, description="Qora, oq, pushti ranglarda mavjud. Batareya holati 100%."),
        dict(name="iPhone 14 128GB", price=10_200_000, quantity=4, description="Barcha ranglarda. Rasmiy Apple kafolati."),
        dict(name="iPhone 15 128GB", price=13_800_000, quantity=3, description="USB-C, Dynamic Island. Yangi, qutida."),
        dict(name="iPhone 15 Pro Max 256GB", price=19_500_000, quantity=2, description="Titan korpus, A17 Pro chip. Yangi, qutida."),
    ],
    "Samsung": [
        dict(name="Samsung Galaxy A54 128GB", price=4_900_000, quantity=10, description="6.4\" Super AMOLED, 5000mAh batareya."),
        dict(name="Samsung Galaxy S23 256GB", price=11_300_000, quantity=4, description="Snapdragon 8 Gen 2, 50MP kamera."),
        dict(name="Samsung Galaxy Z Flip5 256GB", price=15_700_000, quantity=2, description="Buklanuvchi ekran, flex rejim."),
    ],
    "Xiaomi": [
        dict(name="Xiaomi Redmi 13C 128GB", price=1_950_000, quantity=20, description="Eng ommabop byudjet model, 108MP kamera."),
        dict(name="Xiaomi Redmi Note 13 128GB", price=2_800_000, quantity=15, description="AMOLED ekran, tezkor zaryadlash 33W."),
        dict(name="Xiaomi 14 256GB", price=9_600_000, quantity=3, description="Leica optikasi, Snapdragon 8 Gen 3."),
    ],
}


async def main() -> None:
    await init_db()

    existing = await db.count_products()
    if existing > 0:
        print(f"Bazada allaqachon {existing} ta mahsulot bor — seed o'tkazib yuborildi.")
        return

    total_products = 0
    for category_name, products in CATEGORIES.items():
        category = await db.add_category(category_name)
        if category is None:
            existing_categories = await db.get_all_categories()
            category = next(c for c in existing_categories if c.name == category_name)

        for product in products:
            await db.add_product(category_id=category.id, **product)
            total_products += 1

        print(f"✅ {category_name}: {len(products)} ta mahsulot qo'shildi")

    print(f"\nJami: {len(CATEGORIES)} ta kategoriya, {total_products} ta mahsulot bazaga yozildi.")


if __name__ == "__main__":
    asyncio.run(main())
