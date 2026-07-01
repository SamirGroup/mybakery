from sqlalchemy import func, select

from bot.database.engine import async_session
from bot.database.models import Category, Product


async def get_categories(page: int = 0, limit: int = 8) -> tuple[list[Category], int]:
    async with async_session() as session:
        total = await session.scalar(select(func.count()).select_from(Category)) or 0
        result = await session.scalars(
            select(Category).order_by(Category.name).offset(page * limit).limit(limit)
        )
        return list(result.all()), total


async def get_all_categories() -> list[Category]:
    async with async_session() as session:
        result = await session.scalars(select(Category).order_by(Category.name))
        return list(result.all())


async def get_category(category_id: int) -> Category | None:
    async with async_session() as session:
        return await session.get(Category, category_id)


async def add_category(name: str) -> Category | None:
    async with async_session() as session:
        existing = await session.scalar(select(Category).where(Category.name == name))
        if existing:
            return None
        category = Category(name=name)
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category


async def delete_category(category_id: int) -> bool:
    async with async_session() as session:
        category = await session.get(Category, category_id)
        if category is None:
            return False
        await session.delete(category)
        await session.commit()
        return True


async def get_products(
    category_id: int, page: int = 0, limit: int = 6
) -> tuple[list[Product], int]:
    async with async_session() as session:
        base = select(Product).where(
            Product.category_id == category_id, Product.is_active.is_(True)
        )
        total = await session.scalar(
            select(func.count()).select_from(base.subquery())
        ) or 0
        result = await session.scalars(
            base.order_by(Product.name).offset(page * limit).limit(limit)
        )
        return list(result.all()), total


async def get_all_products_by_category(
    category_id: int, page: int = 0, limit: int = 6
) -> tuple[list[Product], int]:
    """Same as get_products but includes inactive items (for admin management)."""
    async with async_session() as session:
        base = select(Product).where(Product.category_id == category_id)
        total = await session.scalar(
            select(func.count()).select_from(base.subquery())
        ) or 0
        result = await session.scalars(
            base.order_by(Product.name).offset(page * limit).limit(limit)
        )
        return list(result.all()), total


async def get_product(product_id: int) -> Product | None:
    async with async_session() as session:
        return await session.get(Product, product_id)


async def search_products(query: str, page: int = 0, limit: int = 6) -> tuple[list[Product], int]:
    async with async_session() as session:
        pattern = f"%{query}%"
        base = select(Product).where(
            Product.name.ilike(pattern), Product.is_active.is_(True)
        )
        total = await session.scalar(
            select(func.count()).select_from(base.subquery())
        ) or 0
        result = await session.scalars(
            base.order_by(Product.name).offset(page * limit).limit(limit)
        )
        return list(result.all()), total


async def add_product(
    category_id: int,
    name: str,
    price: int,
    quantity: int,
    description: str | None = None,
    photo_file_id: str | None = None,
) -> Product:
    async with async_session() as session:
        product = Product(
            category_id=category_id,
            name=name,
            price=price,
            quantity=quantity,
            description=description,
            photo_file_id=photo_file_id,
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product


async def update_product_field(product_id: int, field: str, value) -> bool:
    async with async_session() as session:
        product = await session.get(Product, product_id)
        if product is None:
            return False
        setattr(product, field, value)
        await session.commit()
        return True


async def delete_product(product_id: int) -> bool:
    async with async_session() as session:
        product = await session.get(Product, product_id)
        if product is None:
            return False
        await session.delete(product)
        await session.commit()
        return True


async def count_products(category_id: int | None = None) -> int:
    async with async_session() as session:
        stmt = select(func.count()).select_from(Product)
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        return await session.scalar(stmt) or 0
