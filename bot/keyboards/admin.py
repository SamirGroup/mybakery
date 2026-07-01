from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Category, Product
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
from bot.utils import format_price


def admin_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Kategoriya qo'shish"), KeyboardButton(text="➕ Telefon qo'shish")],
            [KeyboardButton(text="📂 Kategoriyalarni boshqarish")],
            [KeyboardButton(text="⬅️ Foydalanuvchi rejimiga qaytish")],
        ],
        resize_keyboard=True,
    )


def cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel"))
    return builder.as_markup()


def skip_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⏭ O'tkazib yuborish", callback_data="admin_skip"))
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel"))
    return builder.as_markup()


def category_pick_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.row(
            InlineKeyboardButton(
                text=category.name, callback_data=AdminCategoryPickCallback(id=category.id).pack()
            )
        )
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel"))
    return builder.as_markup()


def admin_categories_kb(categories: list[Category], page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.row(
            InlineKeyboardButton(
                text=f"📂 {category.name}",
                callback_data=AdminCategoryManageCallback(id=category.id, page=0).pack(),
            ),
            InlineKeyboardButton(
                text="🗑", callback_data=AdminCategoryDeleteCallback(id=category.id, page=page).pack()
            ),
        )
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=AdminCategoryPageCallback(page=page - 1).pack())
        )
    if pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav_row.append(
            InlineKeyboardButton(text="➡️", callback_data=AdminCategoryPageCallback(page=page + 1).pack())
        )
    if nav_row:
        builder.row(*nav_row)
    return builder.as_markup()


def admin_category_delete_confirm_kb(category_id: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Ha, o'chirish",
            callback_data=AdminCategoryDeleteConfirmCallback(id=category_id, page=page).pack(),
        ),
        InlineKeyboardButton(
            text="❌ Yo'q", callback_data=AdminCategoryPageCallback(page=page).pack()
        ),
    )
    return builder.as_markup()


def admin_products_kb(products: list[Product], category_id: int, page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        status = "✅" if product.is_active else "🚫"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {product.name} — {format_price(product.price)} (soni: {product.quantity})",
                callback_data=AdminProductManageCallback(
                    id=product.id, category_id=category_id, page=page
                ).pack(),
            )
        )
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=AdminProductPageCallback(category_id=category_id, page=page - 1).pack(),
            )
        )
    if pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=AdminProductPageCallback(category_id=category_id, page=page + 1).pack(),
            )
        )
    if nav_row:
        builder.row(*nav_row)
    builder.row(
        InlineKeyboardButton(text="⬅️ Kategoriyalar ro'yxati", callback_data=AdminCategoryPageCallback(page=0).pack())
    )
    return builder.as_markup()


def admin_product_edit_menu_kb(product: Product, category_id: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✏️ Nomi",
            callback_data=AdminProductEditCallback(
                id=product.id, field="name", category_id=category_id, page=page
            ).pack(),
        ),
        InlineKeyboardButton(
            text="📝 Tavsif",
            callback_data=AdminProductEditCallback(
                id=product.id, field="description", category_id=category_id, page=page
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="💵 Narxi",
            callback_data=AdminProductEditCallback(
                id=product.id, field="price", category_id=category_id, page=page
            ).pack(),
        ),
        InlineKeyboardButton(
            text="🔢 Soni",
            callback_data=AdminProductEditCallback(
                id=product.id, field="quantity", category_id=category_id, page=page
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🖼 Rasm",
            callback_data=AdminProductEditCallback(
                id=product.id, field="photo", category_id=category_id, page=page
            ).pack(),
        ),
        InlineKeyboardButton(
            text="🚫 Faolligini o'zgartirish" if product.is_active else "✅ Faollashtirish",
            callback_data=AdminProductToggleCallback(
                id=product.id, category_id=category_id, page=page
            ).pack(),
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🗑 O'chirish",
            callback_data=AdminProductDeleteCallback(
                id=product.id, category_id=category_id, page=page
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Ro'yxatga qaytish",
            callback_data=AdminProductPageCallback(category_id=category_id, page=page).pack(),
        )
    )
    return builder.as_markup()


def admin_product_delete_confirm_kb(product_id: int, category_id: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Ha, o'chirish",
            callback_data=AdminProductDeleteConfirmCallback(
                id=product_id, category_id=category_id, page=page
            ).pack(),
        ),
        InlineKeyboardButton(
            text="❌ Yo'q",
            callback_data=AdminProductManageCallback(
                id=product_id, category_id=category_id, page=page
            ).pack(),
        ),
    )
    return builder.as_markup()
