from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="cat"):
    id: int


class CategoryPageCallback(CallbackData, prefix="catpage"):
    page: int


class ProductCallback(CallbackData, prefix="prod"):
    id: int
    category_id: int


class ProductPageCallback(CallbackData, prefix="prodpage"):
    category_id: int
    page: int


class SearchPageCallback(CallbackData, prefix="searchpage"):
    page: int


class OrderCallback(CallbackData, prefix="order"):
    product_id: int


# --- Admin ---


class AdminCategoryPickCallback(CallbackData, prefix="a_catpick"):
    id: int


class AdminCategoryManageCallback(CallbackData, prefix="a_catmng"):
    id: int
    page: int


class AdminCategoryPageCallback(CallbackData, prefix="a_catpage"):
    page: int


class AdminCategoryDeleteCallback(CallbackData, prefix="a_catdel"):
    id: int
    page: int


class AdminCategoryDeleteConfirmCallback(CallbackData, prefix="a_catdelok"):
    id: int
    page: int


class AdminProductManageCallback(CallbackData, prefix="a_prodmng"):
    id: int
    category_id: int
    page: int


class AdminProductPageCallback(CallbackData, prefix="a_prodpage"):
    category_id: int
    page: int


class AdminProductEditCallback(CallbackData, prefix="a_prodedit"):
    id: int
    field: str
    category_id: int
    page: int


class AdminProductDeleteCallback(CallbackData, prefix="a_proddel"):
    id: int
    category_id: int
    page: int


class AdminProductDeleteConfirmCallback(CallbackData, prefix="a_proddelok"):
    id: int
    category_id: int
    page: int


class AdminProductToggleCallback(CallbackData, prefix="a_prodtoggle"):
    id: int
    category_id: int
    page: int
