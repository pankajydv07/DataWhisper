import os
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from faker import Faker

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

USER_ID = os.getenv("SEED_USER_ID", "local-user")
OUTPUT_PATH = Path(__file__).parent / "sample_seed.sql"

CATEGORIES = {
    "Electronics": ["Phones", "Laptops", "Accessories"],
    "Clothing": ["Shirts", "Shoes", "Outerwear"],
    "Home": ["Kitchen", "Furniture", "Decor"],
    "Beauty": ["Skincare", "Haircare", "Fragrance"],
    "Sports": ["Fitness", "Outdoor", "Footwear"],
}
REGIONS = ["North", "South", "East", "West"]
SEGMENTS = ["Consumer", "Corporate", "SMB"]
STATUSES = ["completed", "completed", "completed", "pending", "cancelled"]


def make_id() -> str:
    return str(uuid.uuid4())


def random_date(start: date, end: date) -> date:
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def sql_quote(value: object) -> str:
    if value is None:
        return "NULL"
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def insert_statement(table: str, columns: list[str], rows: list[dict[str, object]]) -> str:
    values = []
    for row in rows:
        values.append(
            "(" + ", ".join(sql_quote(row[column]) for column in columns) + ")"
        )

    return (
        f"INSERT INTO {table} ({', '.join(columns)})\nVALUES\n"
        + ",\n".join(values)
        + ";\n"
    )


def build_seed_data() -> dict[str, list[dict[str, object]]]:
    customers: list[dict[str, object]] = []
    products: list[dict[str, object]] = []
    orders: list[dict[str, object]] = []
    order_items: list[dict[str, object]] = []

    for _ in range(80):
        customers.append(
            {
                "customer_id": make_id(),
                "user_id": USER_ID,
                "name": fake.name(),
                "region": random.choice(REGIONS),
                "segment": random.choice(SEGMENTS),
                "join_date": random_date(date(2023, 1, 1), date(2025, 12, 31)),
            }
        )

    for category, sub_categories in CATEGORIES.items():
        for sub_category in sub_categories:
            for _ in range(4):
                products.append(
                    {
                        "product_id": make_id(),
                        "user_id": USER_ID,
                        "name": f"{fake.word().title()} {sub_category}",
                        "category": category,
                        "sub_category": sub_category,
                        "unit_price": Decimal(random.randint(300, 85000)),
                    }
                )

    for _ in range(420):
        order_id = make_id()
        customer = random.choice(customers)
        orders.append(
            {
                "order_id": order_id,
                "user_id": USER_ID,
                "customer_id": customer["customer_id"],
                "order_date": random_date(date(2024, 1, 1), date(2026, 3, 31)),
                "status": random.choice(STATUSES),
            }
        )

        for _ in range(random.randint(1, 4)):
            product = random.choice(products)
            order_items.append(
                {
                    "item_id": make_id(),
                    "order_id": order_id,
                    "user_id": USER_ID,
                    "product_id": product["product_id"],
                    "quantity": random.randint(1, 6),
                    "discount": Decimal(random.choice([0, 0.05, 0.1, 0.15, 0.2])),
                }
            )

    return {
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
    }


def main() -> None:
    data = build_seed_data()
    statements = [
        "-- DataWhisper synthetic retail seed data\n",
        insert_statement(
            "customers",
            ["customer_id", "user_id", "name", "region", "segment", "join_date"],
            data["customers"],
        ),
        insert_statement(
            "products",
            ["product_id", "user_id", "name", "category", "sub_category", "unit_price"],
            data["products"],
        ),
        insert_statement(
            "orders",
            ["order_id", "user_id", "customer_id", "order_date", "status"],
            data["orders"],
        ),
        insert_statement(
            "order_items",
            ["item_id", "order_id", "user_id", "product_id", "quantity", "discount"],
            data["order_items"],
        ),
    ]
    OUTPUT_PATH.write_text("\n".join(statements), encoding="utf-8")
    print(
        f"Wrote {OUTPUT_PATH} with "
        f"{len(data['customers'])} customers, {len(data['products'])} products, "
        f"{len(data['orders'])} orders, and {len(data['order_items'])} order items."
    )


if __name__ == "__main__":
    main()
