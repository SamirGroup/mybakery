from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models import Category, Product
from bot.keyboards.callbacks import (
    CategoryCallback,
    CategoryPageCallback,
    OrderCallback,
    ProductCallback,
    ProductPageCallback,
    SearchPageCallback,
)
from bot.utils import format_price


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Katalog")],
            [KeyboardButton(text="🔍 Qidirish"), KeyboardButton(text="ℹ️ Yordam")],
        ],
        resize_keyboard=True,
    )


def categories_kb(categories: list[Category], page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.row(
            InlineKeyboardButton(
                text=category.name, callback_data=CategoryCallback(id=category.id).pack()
            )
        )
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️", callback_data=CategoryPageCallback(page=page - 1).pack()
            )
        )
    if pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️", callback_data=CategoryPageCallback(page=page + 1).pack()
            )
        )
    if nav_row:
        builder.row(*nav_row)
    return builder.as_markup()


def products_kb(
    products: list[Product], category_id: int, page: int, pages: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.row(
            InlineKeyboardButton(
                text=f"{product.name} — {format_price(product.price)}",
                callback_data=ProductCallback(id=product.id, category_id=category_id).pack(),
            )
        )
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=ProductPageCallback(category_id=category_id, page=page - 1).pack(),
            )
        )
    if pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav_row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=ProductPageCallback(category_id=category_id, page=page + 1).pack(),
            )
        )
    if nav_row:
        builder.row(*nav_row)
    builder.row(
        InlineKeyboardButton(text="⬅️ Kategoriyalarga qaytish", callback_data="back_to_categories")
    )
    return builder.as_markup()


def search_results_kb(products: list[Product], query: str, page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.row(
            InlineKeyboardButton(
                text=f"{product.name} — {format_price(product.price)}",
                callback_data=ProductCallback(
                    id=product.id, category_id=product.category_id
                ).pack(),
            )
        )
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton(text="⬅️", callback_data=SearchPageCallback(page=page - 1).pack())
        )
    if pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop"))
    if page < pages - 1:
        nav_row.append(
            InlineKeyboardButton(text="➡️", callback_data=SearchPageCallback(page=page + 1).pack())
        )
    if nav_row:
        builder.row(*nav_row)
    return builder.as_markup()


def product_card_kb(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🛒 Buyurtma berish", callback_data=OrderCallback(product_id=product_id).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Ro'yxatga qaytish",
            callback_data=ProductPageCallback(category_id=category_id, page=0).pack(),
        )
    )
    return builder.as_markup()
