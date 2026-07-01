from aiogram.fsm.state import State, StatesGroup


class AddCategory(StatesGroup):
    name = State()


class AddProduct(StatesGroup):
    category = State()
    name = State()
    description = State()
    price = State()
    quantity = State()
    photo = State()


class EditProduct(StatesGroup):
    value = State()


class SearchProduct(StatesGroup):
    query = State()


class OrderRequest(StatesGroup):
    contact = State()
