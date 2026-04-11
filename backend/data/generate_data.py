import os
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from faker import Faker

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

USER_ID = os.getenv("SEED_USER_ID", "local-user")
OUTPUT_PATH = Path(__file__).parent / "sample_seed.sql"
DATABASE_URL = os.getenv("SUPABASE_DB_URL", "")

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


def create_schema(connection: psycopg.Connection) -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS customers (
      customer_id uuid PRIMARY KEY,
      user_id text NOT NULL,
      name text NOT NULL,
      region text NOT NULL,
      segment text NOT NULL,
      join_date date NOT NULL
    );

    CREATE TABLE IF NOT EXISTS products (
      product_id uuid PRIMARY KEY,
      user_id text NOT NULL,
      name text NOT NULL,
      category text NOT NULL,
      sub_category text NOT NULL,
      unit_price numeric NOT NULL
    );

    CREATE TABLE IF NOT EXISTS orders (
      order_id uuid PRIMARY KEY,
      user_id text NOT NULL,
      customer_id uuid NOT NULL REFERENCES customers(customer_id),
      order_date date NOT NULL,
      status text NOT NULL
    );

    CREATE TABLE IF NOT EXISTS order_items (
      item_id uuid PRIMARY KEY,
      order_id uuid NOT NULL REFERENCES orders(order_id),
      user_id text NOT NULL,
      product_id uuid NOT NULL REFERENCES products(product_id),
      quantity integer NOT NULL,
      discount numeric NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);
    CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id);
    CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
    CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
    CREATE INDEX IF NOT EXISTS idx_order_items_user_id ON order_items(user_id);
    """

    with connection.cursor() as cursor:
        cursor.execute(ddl)


def replace_user_data(
    connection: psycopg.Connection, user_id: str, data: dict[str, list[dict[str, object]]]
) -> None:
    # Delete in dependency order, then insert in parent-first order.
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM order_items WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM orders WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM products WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM customers WHERE user_id = %s", (user_id,))

        cursor.executemany(
            """
            INSERT INTO customers
              (customer_id, user_id, name, region, segment, join_date)
            VALUES
              (%(customer_id)s, %(user_id)s, %(name)s, %(region)s, %(segment)s, %(join_date)s)
            """,
            data["customers"],
        )
        cursor.executemany(
            """
            INSERT INTO products
              (product_id, user_id, name, category, sub_category, unit_price)
            VALUES
              (%(product_id)s, %(user_id)s, %(name)s, %(category)s, %(sub_category)s, %(unit_price)s)
            """,
            data["products"],
        )
        cursor.executemany(
            """
            INSERT INTO orders
              (order_id, user_id, customer_id, order_date, status)
            VALUES
              (%(order_id)s, %(user_id)s, %(customer_id)s, %(order_date)s, %(status)s)
            """,
            data["orders"],
        )
        cursor.executemany(
            """
            INSERT INTO order_items
              (item_id, order_id, user_id, product_id, quantity, discount)
            VALUES
              (%(item_id)s, %(order_id)s, %(user_id)s, %(product_id)s, %(quantity)s, %(discount)s)
            """,
            data["order_items"],
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

    if not DATABASE_URL:
        raise RuntimeError("SUPABASE_DB_URL is not configured.")

    with psycopg.connect(DATABASE_URL, connect_timeout=15) as connection:
        create_schema(connection)
        replace_user_data(connection, USER_ID, data)
        connection.commit()

    print(
        f"Seeded Supabase for user_id={USER_ID!r} and wrote {OUTPUT_PATH} with "
        f"{len(data['customers'])} customers, {len(data['products'])} products, "
        f"{len(data['orders'])} orders, and {len(data['order_items'])} order items."
    )


if __name__ == "__main__":
    main()
