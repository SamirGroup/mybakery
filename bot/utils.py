from bot.config import CURRENCY


def format_price(amount: int) -> str:
    return f"{amount:,}".replace(",", " ") + f" {CURRENCY}"


def total_pages(total_items: int, page_size: int) -> int:
    if total_items <= 0:
        return 1
    return (total_items + page_size - 1) // page_size
