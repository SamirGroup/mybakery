from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import ADMIN_IDS, PAGE_SIZE
from bot.database import requests as db
from bot.keyboards.callbacks import (
    CategoryCallback,
    CategoryPageCallback,
    OrderCallback,
    ProductCallback,
    ProductPageCallback,
    SearchPageCallback,
)
from bot.keyboards.user import (
    categories_kb,
    main_menu_kb,
    product_card_kb,
    products_kb,
    search_results_kb,
)
from bot.states import OrderRequest, SearchProduct
from bot.utils import format_price, total_pages

router = Router(name="user")

WELCOME_TEXT = (
    "👋 Assalomu alaykum!\n\n"
    "Bu bot orqali telefonlar katalogi bilan tanishishingiz, narxlari va "
    "mavjudligi haqida ma'lumot olishingiz mumkin.\n\n"
    "📱 <b>Katalog</b> — kategoriyalar bo'yicha telefonlarni ko'rish\n"
    "🔍 <b>Qidirish</b> — model nomi bo'yicha qidirish"
)

HELP_TEXT = (
    "ℹ️ <b>Botdan foydalanish</b>\n\n"
    "📱 Katalog — telefonlarni kategoriyalar bo'yicha ko'rasiz\n"
    "🔍 Qidirish — telefon nomini yozib qidirasiz\n"
    "Har bir telefon kartochkasida narx, tavsif va soni ko'rsatiladi.\n"
    "🛒 Buyurtma berish tugmasi orqali operator bilan bog'lanishingiz mumkin."
)


async def _render(callback: CallbackQuery, text: str, kb) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=kb)


async def _show_categories(callback: CallbackQuery | None, message: Message | None, page: int = 0) -> None:
    categories, total = await db.get_categories(page=page, limit=8)
    pages = total_pages(total, 8)
    if not categories:
        text = "Hozircha kategoriyalar mavjud emas. Keyinroq qayta urinib ko'ring."
    else:
        text = "📱 Kategoriyani tanlang:"
    kb = categories_kb(categories, page, pages)

    if callback is not None:
        await _render(callback, text, kb)
    elif message is not None:
        await message.answer(text, reply_markup=kb)


async def _show_products(callback: CallbackQuery, category_id: int, page: int) -> None:
    category = await db.get_category(category_id)
    if category is None:
        await callback.answer("Kategoriya topilmadi", show_alert=True)
        return
    products, total = await db.get_products(category_id, page=page, limit=PAGE_SIZE)
    pages = total_pages(total, PAGE_SIZE)
    if not products:
        text = f"📂 {category.name}\n\nBu kategoriyada hozircha telefon yo'q."
    else:
        text = f"📂 {category.name}\n\nTelefonni tanlang:"
    kb = products_kb(products, category_id, page, pages)
    await _render(callback, text, kb)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Yordam")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_kb())


@router.message(F.text == "📱 Katalog")
async def show_catalog(message: Message) -> None:
    await _show_categories(None, message, page=0)


@router.callback_query(CategoryPageCallback.filter())
async def paginate_categories(callback: CallbackQuery, callback_data: CategoryPageCallback) -> None:
    await _show_categories(callback, None, page=callback_data.page)
    await callback.answer()


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery) -> None:
    await _show_categories(callback, None, page=0)
    await callback.answer()


@router.callback_query(CategoryCallback.filter())
async def open_category(callback: CallbackQuery, callback_data: CategoryCallback) -> None:
    await _show_products(callback, callback_data.id, page=0)
    await callback.answer()


@router.callback_query(ProductPageCallback.filter())
async def paginate_products(callback: CallbackQuery, callback_data: ProductPageCallback) -> None:
    await _show_products(callback, callback_data.category_id, page=callback_data.page)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(ProductCallback.filter())
async def open_product(callback: CallbackQuery, callback_data: ProductCallback) -> None:
    product = await db.get_product(callback_data.id)
    if product is None or not product.is_active:
        await callback.answer("Bu mahsulot mavjud emas", show_alert=True)
        return

    caption = (
        f"📱 <b>{product.name}</b>\n\n"
        f"{product.description or ''}\n\n"
        f"💵 Narxi: <b>{format_price(product.price)}</b>\n"
        f"📦 Mavjud: {'bor, ' + str(product.quantity) + ' dona' if product.quantity > 0 else 'sotuvda yo`q'}"
    ).strip()

    kb = product_card_kb(product.id, callback_data.category_id)
    if product.photo_file_id:
        await callback.message.answer_photo(product.photo_file_id, caption=caption, reply_markup=kb)
    else:
        await callback.message.answer(caption, reply_markup=kb)
    await callback.answer()


@router.message(F.text == "🔍 Qidirish")
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchProduct.query)
    await message.answer("🔍 Qidirmoqchi bo'lgan telefon nomini yozing:")


@router.message(StateFilter(SearchProduct.query), F.text)
async def do_search(message: Message, state: FSMContext) -> None:
    query = message.text.strip()
    await state.set_state(None)
    await state.update_data(last_query=query)
    await _send_search_results(message, query, page=0)


async def _send_search_results(message: Message, query: str, page: int) -> None:
    products, total = await db.search_products(query, page=page, limit=PAGE_SIZE)
    pages = total_pages(total, PAGE_SIZE)
    if not products:
        await message.answer(f"'{query}' bo'yicha hech narsa topilmadi.", reply_markup=main_menu_kb())
        return
    kb = search_results_kb(products, query, page, pages)
    await message.answer(f"🔍 '{query}' bo'yicha natijalar:", reply_markup=kb)


@router.callback_query(SearchPageCallback.filter())
async def paginate_search(callback: CallbackQuery, callback_data: SearchPageCallback, state: FSMContext) -> None:
    data = await state.get_data()
    query = data.get("last_query", "")
    if not query:
        await callback.answer("Qidiruv muddati tugagan, qaytadan qidiring", show_alert=True)
        return
    products, total = await db.search_products(query, page=callback_data.page, limit=PAGE_SIZE)
    pages = total_pages(total, PAGE_SIZE)
    kb = search_results_kb(products, query, callback_data.page, pages)
    await _render(callback, f"🔍 '{query}' bo'yicha natijalar:", kb)
    await callback.answer()


@router.callback_query(OrderCallback.filter())
async def start_order(callback: CallbackQuery, callback_data: OrderCallback, state: FSMContext) -> None:
    product = await db.get_product(callback_data.product_id)
    if product is None or not product.is_active:
        await callback.answer("Bu mahsulot mavjud emas", show_alert=True)
        return
    await state.set_state(OrderRequest.contact)
    await state.update_data(order_product_id=product.id)
    await callback.message.answer(
        f"🛒 <b>{product.name}</b> uchun buyurtma.\n\n"
        "Ismingiz va telefon raqamingizni yozing (masalan: Ali, +998901234567), "
        "operatorimiz siz bilan tez orada bog'lanadi."
    )
    await callback.answer()


@router.message(StateFilter(OrderRequest.contact), F.text)
async def finish_order(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    product_id = data.get("order_product_id")
    product = await db.get_product(product_id) if product_id else None
    await state.clear()

    if product is None:
        await message.answer("Kechirasiz, mahsulot topilmadi.", reply_markup=main_menu_kb())
        return

    await message.answer(
        "✅ Buyurtmangiz qabul qilindi! Operatorimiz tez orada siz bilan bog'lanadi.",
        reply_markup=main_menu_kb(),
    )

    buyer = message.from_user
    username = f"@{buyer.username}" if buyer and buyer.username else "username yo'q"
    notify_text = (
        "🛒 <b>Yangi buyurtma so'rovi!</b>\n\n"
        f"📱 Mahsulot: {product.name} — {format_price(product.price)}\n"
        f"👤 Mijoz: {buyer.full_name if buyer else 'noma`lum'} ({username})\n"
        f"🆔 ID: {buyer.id if buyer else '-'}\n"
        f"✍️ Xabar: {message.text}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, notify_text)
        except TelegramBadRequest:
            continue
