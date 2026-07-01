from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import PAGE_SIZE
from bot.database import requests as db
from bot.filters import IsAdmin
from bot.keyboards.admin import (
    admin_categories_kb,
    admin_category_delete_confirm_kb,
    admin_menu_kb,
    admin_product_delete_confirm_kb,
    admin_product_edit_menu_kb,
    admin_products_kb,
    cancel_kb,
    category_pick_kb,
    skip_kb,
)
from bot.keyboards.callbacks import (
    AdminCategoryDeleteCallback,
    AdminCategoryDeleteConfirmCallback,
    AdminCategoryManageCallback,
    AdminCategoryPageCallback,
    AdminCategoryPickCallback,
    AdminProductDeleteCallback,
    AdminProductDeleteConfirmCallback,
    AdminProductEditCallback,
    AdminProductManageCallback,
    AdminProductPageCallback,
    AdminProductToggleCallback,
)
from bot.states import AddCategory, AddProduct, EditProduct
from bot.utils import format_price, total_pages

router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


async def _render(callback: CallbackQuery, text: str, kb) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        await callback.message.delete()
        await callback.message.answer(text, reply_markup=kb)


def _product_card_text(product) -> str:
    return (
        f"📱 <b>{product.name}</b>\n"
        f"{product.description or '-'}\n\n"
        f"💵 Narxi: {format_price(product.price)}\n"
        f"🔢 Soni: {product.quantity}\n"
        f"Holati: {'✅ Faol' if product.is_active else '🚫 Nofaol'}"
    )


async def _show_admin_categories(message: Message | None, callback: CallbackQuery | None, page: int) -> None:
    categories, total = await db.get_categories(page=page, limit=8)
    pages = total_pages(total, 8)
    text = "📂 Kategoriyalar:" if categories else "Hozircha kategoriya yo'q. Avval kategoriya qo'shing."
    kb = admin_categories_kb(categories, page, pages)
    if callback is not None:
        await _render(callback, text, kb)
    else:
        await message.answer(text, reply_markup=kb)


async def _show_admin_products(callback: CallbackQuery, category_id: int, page: int) -> None:
    category = await db.get_category(category_id)
    if category is None:
        await callback.answer("Kategoriya topilmadi", show_alert=True)
        return
    products, total = await db.get_all_products_by_category(category_id, page=page, limit=PAGE_SIZE)
    pages = total_pages(total, PAGE_SIZE)
    text = (
        f"📂 {category.name}\n\nMahsulotni tanlang:"
        if products
        else f"📂 {category.name}\n\nBu kategoriyada mahsulot yo'q."
    )
    kb = admin_products_kb(products, category_id, page, pages)
    await _render(callback, text, kb)


# --- Entry / exit ---


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🛠 Admin panel", reply_markup=admin_menu_kb())


@router.message(F.text == "⬅️ Foydalanuvchi rejimiga qaytish")
async def exit_admin(message: Message, state: FSMContext) -> None:
    from bot.keyboards.user import main_menu_kb

    await state.clear()
    await message.answer("Foydalanuvchi rejimiga qaytdingiz.", reply_markup=main_menu_kb())


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Bekor qilindi.", reply_markup=admin_menu_kb())
    await callback.answer()


# --- Add category ---


@router.message(F.text == "➕ Kategoriya qo'shish")
async def add_category_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AddCategory.name)
    await message.answer("Yangi kategoriya nomini kiriting:", reply_markup=cancel_kb())


@router.message(StateFilter(AddCategory.name), F.text)
async def add_category_finish(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    await state.clear()
    category = await db.add_category(name)
    if category is None:
        await message.answer(f"⚠️ '{name}' nomli kategoriya allaqachon mavjud.", reply_markup=admin_menu_kb())
        return
    await message.answer(f"✅ '{category.name}' kategoriyasi qo'shildi.", reply_markup=admin_menu_kb())


# --- Manage categories ---


@router.message(F.text == "📂 Kategoriyalarni boshqarish")
async def manage_categories(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _show_admin_categories(message, None, page=0)


@router.callback_query(AdminCategoryPageCallback.filter())
async def admin_paginate_categories(callback: CallbackQuery, callback_data: AdminCategoryPageCallback) -> None:
    await _show_admin_categories(None, callback, page=callback_data.page)
    await callback.answer()


@router.callback_query(AdminCategoryDeleteCallback.filter())
async def admin_delete_category_confirm(callback: CallbackQuery, callback_data: AdminCategoryDeleteCallback) -> None:
    category = await db.get_category(callback_data.id)
    if category is None:
        await callback.answer("Topilmadi", show_alert=True)
        return
    count = await db.count_products(category.id)
    text = (
        f"⚠️ '{category.name}' kategoriyasini o'chirmoqchimisiz?\n"
        f"Bunga tegishli {count} ta mahsulot ham butunlay o'chib ketadi!"
    )
    kb = admin_category_delete_confirm_kb(category.id, callback_data.page)
    await _render(callback, text, kb)
    await callback.answer()


@router.callback_query(AdminCategoryDeleteConfirmCallback.filter())
async def admin_delete_category(callback: CallbackQuery, callback_data: AdminCategoryDeleteConfirmCallback) -> None:
    await db.delete_category(callback_data.id)
    await callback.answer("O'chirildi", show_alert=True)
    await _show_admin_categories(None, callback, page=0)


@router.callback_query(AdminCategoryManageCallback.filter())
async def admin_open_category(callback: CallbackQuery, callback_data: AdminCategoryManageCallback) -> None:
    await _show_admin_products(callback, callback_data.id, page=0)
    await callback.answer()


@router.callback_query(AdminProductPageCallback.filter())
async def admin_paginate_products(callback: CallbackQuery, callback_data: AdminProductPageCallback) -> None:
    await _show_admin_products(callback, callback_data.category_id, page=callback_data.page)
    await callback.answer()


# --- Manage single product ---


@router.callback_query(AdminProductManageCallback.filter())
async def admin_manage_product(callback: CallbackQuery, callback_data: AdminProductManageCallback) -> None:
    product = await db.get_product(callback_data.id)
    if product is None:
        await callback.answer("Topilmadi", show_alert=True)
        return
    kb = admin_product_edit_menu_kb(product, callback_data.category_id, callback_data.page)
    await _render(callback, _product_card_text(product), kb)
    await callback.answer()


@router.callback_query(AdminProductToggleCallback.filter())
async def admin_toggle_product(callback: CallbackQuery, callback_data: AdminProductToggleCallback) -> None:
    product = await db.get_product(callback_data.id)
    if product is None:
        await callback.answer("Topilmadi", show_alert=True)
        return
    await db.update_product_field(product.id, "is_active", not product.is_active)
    product = await db.get_product(product.id)
    kb = admin_product_edit_menu_kb(product, callback_data.category_id, callback_data.page)
    await _render(callback, _product_card_text(product), kb)
    await callback.answer("Holat o'zgartirildi")


@router.callback_query(AdminProductDeleteCallback.filter())
async def admin_delete_product_confirm(callback: CallbackQuery, callback_data: AdminProductDeleteCallback) -> None:
    product = await db.get_product(callback_data.id)
    if product is None:
        await callback.answer("Topilmadi", show_alert=True)
        return
    text = f"⚠️ '{product.name}' mahsulotini butunlay o'chirmoqchimisiz?"
    kb = admin_product_delete_confirm_kb(product.id, callback_data.category_id, callback_data.page)
    await _render(callback, text, kb)
    await callback.answer()


@router.callback_query(AdminProductDeleteConfirmCallback.filter())
async def admin_delete_product(callback: CallbackQuery, callback_data: AdminProductDeleteConfirmCallback) -> None:
    await db.delete_product(callback_data.id)
    await callback.answer("O'chirildi", show_alert=True)
    await _show_admin_products(callback, callback_data.category_id, page=callback_data.page)


@router.callback_query(AdminProductEditCallback.filter())
async def admin_edit_product_field(callback: CallbackQuery, callback_data: AdminProductEditCallback, state: FSMContext) -> None:
    await state.set_state(EditProduct.value)
    await state.update_data(
        edit_product_id=callback_data.id,
        edit_field=callback_data.field,
        edit_category_id=callback_data.category_id,
        edit_page=callback_data.page,
    )
    prompts = {
        "name": "Yangi nomini kiriting:",
        "description": "Yangi tavsifini kiriting:",
        "price": "Yangi narxini kiriting (faqat son, masalan 5000000):",
        "quantity": "Yangi sonini kiriting (faqat son):",
        "photo": "Yangi rasmni yuboring (surat sifatida):",
    }
    await callback.message.answer(prompts[callback_data.field], reply_markup=cancel_kb())
    await callback.answer()


async def _apply_edit(message: Message, state: FSMContext, data: dict, value) -> None:
    field_map = {"photo": "photo_file_id"}
    db_field = field_map.get(data["edit_field"], data["edit_field"])
    await db.update_product_field(data["edit_product_id"], db_field, value)
    await state.clear()
    await message.answer("✅ Yangilandi.", reply_markup=admin_menu_kb())


@router.message(StateFilter(EditProduct.value), F.photo)
async def admin_edit_product_photo(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("edit_field") != "photo":
        await message.answer("Iltimos, matn shaklida javob yozing.")
        return
    await _apply_edit(message, state, data, message.photo[-1].file_id)


@router.message(StateFilter(EditProduct.value), F.text)
async def admin_edit_product_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    field = data.get("edit_field")
    if field == "photo":
        await message.answer("Iltimos, rasm (surat) yuboring.")
        return

    raw = message.text.strip()
    if field in ("price", "quantity"):
        if not raw.isdigit():
            await message.answer("⚠️ Faqat son kiriting. Qaytadan urinib ko'ring:")
            return
        value = int(raw)
    else:
        value = raw
    await _apply_edit(message, state, data, value)


# --- Add product ---


@router.message(F.text == "➕ Telefon qo'shish")
async def add_product_start(message: Message, state: FSMContext) -> None:
    categories = await db.get_all_categories()
    if not categories:
        await message.answer("⚠️ Avval kamida bitta kategoriya qo'shing.", reply_markup=admin_menu_kb())
        return
    await state.set_state(AddProduct.category)
    await message.answer("Kategoriyani tanlang:", reply_markup=category_pick_kb(categories))


@router.callback_query(StateFilter(AddProduct.category), AdminCategoryPickCallback.filter())
async def add_product_category(callback: CallbackQuery, callback_data: AdminCategoryPickCallback, state: FSMContext) -> None:
    await state.update_data(new_category_id=callback_data.id)
    await state.set_state(AddProduct.name)
    await callback.message.answer("Telefon nomini kiriting (masalan: iPhone 15 Pro 256GB):", reply_markup=cancel_kb())
    await callback.answer()


@router.message(StateFilter(AddProduct.name), F.text)
async def add_product_name(message: Message, state: FSMContext) -> None:
    await state.update_data(new_name=message.text.strip())
    await state.set_state(AddProduct.description)
    await message.answer("Tavsifini kiriting (rang, xotira hajmi va h.k.):", reply_markup=skip_kb())


@router.message(StateFilter(AddProduct.description), F.text)
async def add_product_description(message: Message, state: FSMContext) -> None:
    await state.update_data(new_description=message.text.strip())
    await state.set_state(AddProduct.price)
    await message.answer("Narxini kiriting (faqat son, so'mda, masalan 12000000):", reply_markup=cancel_kb())


@router.callback_query(StateFilter(AddProduct.description), F.data == "admin_skip")
async def add_product_skip_description(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(new_description=None)
    await state.set_state(AddProduct.price)
    await callback.message.answer("Narxini kiriting (faqat son, so'mda, masalan 12000000):", reply_markup=cancel_kb())
    await callback.answer()


@router.message(StateFilter(AddProduct.price), F.text)
async def add_product_price(message: Message, state: FSMContext) -> None:
    raw = message.text.strip()
    if not raw.isdigit():
        await message.answer("⚠️ Narxni faqat son sifatida kiriting. Qaytadan urinib ko'ring:")
        return
    await state.update_data(new_price=int(raw))
    await state.set_state(AddProduct.quantity)
    await message.answer("Omborda nechta dona borligini kiriting (son):", reply_markup=cancel_kb())


@router.message(StateFilter(AddProduct.quantity), F.text)
async def add_product_quantity(message: Message, state: FSMContext) -> None:
    raw = message.text.strip()
    if not raw.isdigit():
        await message.answer("⚠️ Sonini faqat son sifatida kiriting. Qaytadan urinib ko'ring:")
        return
    await state.update_data(new_quantity=int(raw))
    await state.set_state(AddProduct.photo)
    await message.answer("Telefon rasmini yuboring:", reply_markup=skip_kb())


@router.message(StateFilter(AddProduct.photo), F.photo)
async def add_product_photo(message: Message, state: FSMContext) -> None:
    await _finish_add_product(message, state, message.photo[-1].file_id)


@router.message(StateFilter(AddProduct.photo), F.text)
async def add_product_photo_wrong(message: Message) -> None:
    await message.answer("Iltimos, rasm yuboring yoki 'O'tkazib yuborish' tugmasini bosing.")


@router.callback_query(StateFilter(AddProduct.photo), F.data == "admin_skip")
async def add_product_skip_photo(callback: CallbackQuery, state: FSMContext) -> None:
    await _finish_add_product(callback.message, state, None)
    await callback.answer()


async def _finish_add_product(message: Message, state: FSMContext, photo_file_id: str | None) -> None:
    data = await state.get_data()
    await state.clear()
    product = await db.add_product(
        category_id=data["new_category_id"],
        name=data["new_name"],
        price=data["new_price"],
        quantity=data["new_quantity"],
        description=data.get("new_description"),
        photo_file_id=photo_file_id,
    )
    text = (
        f"✅ Yangi telefon qo'shildi!\n\n"
        f"📱 {product.name}\n"
        f"💵 {format_price(product.price)}\n"
        f"🔢 Soni: {product.quantity}"
    )
    if photo_file_id:
        await message.answer_photo(photo_file_id, caption=text, reply_markup=admin_menu_kb())
    else:
        await message.answer(text, reply_markup=admin_menu_kb())
