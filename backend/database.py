import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "refunds.db"

# Name, item, price in USD, days since purchase, final sale
CUSTOMERS = [
    ("Ada Okafor", "Wireless headphones", 80, 5, 0),
    ("Chidi Nwosu", "Running shoes", 120, 12, 1),
    ("Amina Bello", "Laptop", 720, 7, 0),
    ("Tunde Adebayo", "Coffee maker", 65, 45, 0),
    ("Zainab Musa", "Jacket", 95, 15, 0),
    ("Emeka Obi", "Monitor", 480, 28, 0),
    ("Ngozi Eze", "Blender", 55, 8, 0),
    ("Femi Adeyemi", "Tablet", 550, 4, 0),
    ("Fatima Usman", "Travel bag", 70, 31, 0),
    ("Kunle Ajayi", "Smartwatch", 230, 1, 1),
    ("Ifeoma Okeke", "Keyboard", 45, 20, 0),
    ("Ibrahim Lawal", "Office chair", 300, 42, 0),
    ("Sade Williams", "Book set", 40, 3, 0),
    ("Yusuf Abdullahi", "Projector", 520, 11, 0),
    ("Grace Johnson", "Phone charger", 30, 6, 0),
]


def connect_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_db():
    connection = connect_db()

    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                item TEXT NOT NULL,
                amount REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                final_sale INTEGER NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );

            CREATE TABLE IF NOT EXISTS refund_requests (
                id INTEGER PRIMARY KEY,
                order_id TEXT NOT NULL,
                message TEXT NOT NULL,
                issue TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            );
        """)

        count = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        if count == 0:
            extra_items = ("Phone case", "USB cable", "Notebook")

            for number, (name, item, amount, days_old, final_sale) in enumerate(
                CUSTOMERS, start=1
            ):
                email = name.lower().replace(" ", ".") + "@example.com" #gmail 

                cursor = connection.execute(
                    "INSERT INTO customers (name, email) VALUES (?, ?)",
                    (name, email),
                )
                customer_id = cursor.lastrowid

                connection.execute(
                    """INSERT INTO orders
                       (id, customer_id, item, amount, purchase_date, final_sale)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        f"WN-{1000 + number}",
                        customer_id,
                        item,
                        amount,
                        (date.today() - timedelta(days=days_old)).isoformat(),
                        final_sale,
                    ),
                )

                connection.execute(
                    """INSERT INTO orders
                       (id, customer_id, item, amount, purchase_date, final_sale)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        f"WN-{2000 + number}",
                        customer_id,
                        extra_items[number % len(extra_items)],
                        15 + number,
                        (date.today() - timedelta(days=35 + number)).isoformat(),
                        0,
                    ),
                )

            connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_db()
    connection = connect_db()

    try:
        customers = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]
        orders = connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

        print(f"Customers: {customers}")
        print(f"Orders: {orders}")
    finally:
        connection.close()