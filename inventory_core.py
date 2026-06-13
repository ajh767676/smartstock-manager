import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime

DB_NAME = "inventory.db"


def get_connection():
    return sqlite3.connect(DB_NAME)



# ---------------- PRODUCTS ----------------

def get_products():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM Products", conn)
    conn.close()
    return df


def add_product_db(name, price, quantity, reorder_level, image_url=None):
    name = name.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()

    # 🔍 Check if product already exists
    cursor.execute(
        "SELECT product_id FROM Products WHERE LOWER(name) = LOWER(?)",
        (name,)
    )
    existing = cursor.fetchone()

    if existing:
        # ✅ UPDATE instead of INSERT
        product_id = existing[0]

        cursor.execute("""
            UPDATE Products
            SET quantity = quantity + ?
            WHERE product_id = ?
        """, (quantity, product_id))

        conn.commit()
        conn.close()

        return {"success": True, "message": f"{name} already exists — quantity updated"}

    else:
        # ✅ INSERT new product
        cursor.execute("""
            INSERT INTO Products (name, price, quantity, reorder_level, image_url)
            VALUES (?, ?, ?, ?, ?)
        """, (name, price, quantity, reorder_level, image_url))

        conn.commit()
        conn.close()

        return {"success": True, "message": f"{name} added successfully"}



def update_product_db(product_id, new_price, new_quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Products
        SET price = ?, quantity = ?
        WHERE product_id = ?
    """, (new_price, new_quantity, product_id))

    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated


def delete_product_db(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Products WHERE product_id = ?", (product_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted


def search_product_db(name):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM Products WHERE name LIKE ?",
        conn,
        params=('%' + name + '%',)
    )
    conn.close()
    return df


def get_low_stock_items():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT product_id, name, quantity, reorder_level
        FROM Products
        WHERE quantity <= reorder_level
    """, conn)
    conn.close()
    return df


# ---------------- ORDERS ----------------

def create_order_db(product_id, order_qty):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM Products WHERE product_id = ?", (product_id,))
    result = cursor.fetchone()

    if result is None:
        conn.close()
        return {"success": False, "message": "Product not found."}

    stock = result[0]

    if order_qty > stock:
        conn.close()
        return {"success": False, "message": "Not enough stock."}

    from datetime import timedelta
    import random

    order_date = (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO Orders (order_date)
    VALUES (?)
    """, (order_date,))

    order_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO OrderItems (order_id, product_id, quantity)
        VALUES (?, ?, ?)
    """, (order_id, product_id, order_qty))

    cursor.execute("""
        UPDATE Products
        SET quantity = quantity - ?
        WHERE product_id = ?
    """, (order_qty, product_id))

    conn.commit()
    conn.close()

    return {"success": True, "message": f"Order {order_id} created successfully!", "order_id": order_id}

def create_cart_order_db(cart_items):
    conn = get_connection()
    cursor = conn.cursor()

    # Check stock for every item before creating order
    for item in cart_items:
        product_id = item["product_id"]
        order_qty = int(item["quantity"])

        cursor.execute(
            "SELECT quantity FROM Products WHERE product_id = ?",
            (product_id,)
        )
        result = cursor.fetchone()

        if result is None:
            conn.close()
            return {"success": False, "message": f"Product not found: {item['name']}"}

        stock = result[0]

        if order_qty > stock:
            conn.close()
            return {
                "success": False,
                "message": f"Not enough stock for {item['name']}. Available: {stock}"
            }

    # Create one order
    order_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        INSERT INTO Orders (order_date)
        VALUES (?)
    """, (order_date,))

    order_id = cursor.lastrowid

    # Add each cart item to the order and reduce inventory
    for item in cart_items:
        product_id = item["product_id"]
        order_qty = int(item["quantity"])

        cursor.execute("""
            INSERT INTO OrderItems (order_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (order_id, product_id, order_qty))

        cursor.execute("""
            UPDATE Products
            SET quantity = quantity - ?
            WHERE product_id = ?
        """, (order_qty, product_id))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Order {order_id} created with {len(cart_items)} items!",
        "order_id": order_id
    }

def get_orders_with_total():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT o.order_id, p.product_id, p.name, oi.quantity, p.price,
               (oi.quantity * p.price) AS total_price
        FROM Orders o
        JOIN OrderItems oi ON o.order_id = oi.order_id
        JOIN Products p ON oi.product_id = p.product_id
        ORDER BY o.order_id
    """, conn)
    conn.close()
    return df



def delete_order_db(order_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Find all items in this order
    cursor.execute("""
        SELECT product_id, quantity
        FROM OrderItems
        WHERE order_id = ?
    """, (int(order_id),))

    items = cursor.fetchall()

    if not items:
        conn.close()
        return {"success": False, "message": "Order not found."}

    # Restore product quantities
    for product_id, qty in items:
        cursor.execute("""
            UPDATE Products
            SET quantity = quantity + ?
            WHERE product_id = ?
        """, (qty, product_id))

    # Delete order items first, then order
    cursor.execute("DELETE FROM OrderItems WHERE order_id = ?", (int(order_id),))
    cursor.execute("DELETE FROM Orders WHERE order_id = ?", (int(order_id),))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Order {order_id} cancelled and inventory restored."
    }


# ---------------- REPORTS ----------------

def get_system_report():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Products")
    product_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Orders")
    order_count = cursor.fetchone()[0]

    conn.close()

    return {
        "total_products": product_count,
        "total_orders": order_count
    }


def get_total_revenue():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(oi.quantity * p.price)
        FROM OrderItems oi
        JOIN Products p ON oi.product_id = p.product_id
    """)

    result = cursor.fetchone()[0]
    conn.close()
    return result or 0.0


def get_best_selling_product():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.name, SUM(oi.quantity) AS total_sold
        FROM OrderItems oi
        JOIN Products p ON oi.product_id = p.product_id
        GROUP BY p.name
        ORDER BY total_sold DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    if result:
        return {"name": result[0], "total_sold": result[1]}
    return None


def get_sales_by_product():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT p.name, SUM(oi.quantity) AS total_sold
        FROM OrderItems oi
        JOIN Products p ON oi.product_id = p.product_id
        GROUP BY p.name
        ORDER BY total_sold DESC
    """, conn)
    conn.close()
    return df

#######################################
# ---------------- AI ----------------
# LINEAR REGRESSION MODEL
#######################################

def forecast_demand_df():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT product_id, quantity
        FROM OrderItems
    """, conn)

    if df.empty:
        conn.close()
        return pd.DataFrame(columns=["product_id", "name", "predicted_demand"])

    forecasts = []
    cursor = conn.cursor()
    # look at past sales
    for pid, group in df.groupby("product_id"):
        group = group.reset_index(drop=True)
        # If not enough history use last known value
        if len(group) < 2:
            pred = int(group["quantity"].iloc[-1])
        else:
            group["time"] = range(len(group))
            X = group[["time"]]
            y = group["quantity"]
            # TRAIN THE MODEL
            ###########################
            model = LinearRegression()
            model.fit(X, y)
            ###########################
            next_time = pd.DataFrame({"time": [len(group)]})
            pred = round(max(0, model.predict(next_time)[0]))

        cursor.execute("SELECT name FROM Products WHERE product_id = ?", (pid,))
        result = cursor.fetchone()
        name = result[0] if result else f"Product {pid}"

        forecasts.append({
            "product_id": pid,
            "name": name,
            "predicted_demand": pred
        })

    conn.close()
    return pd.DataFrame(forecasts)

def reset_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM OrderItems")
    cursor.execute("DELETE FROM Orders")
    cursor.execute("DELETE FROM Products")

    cursor.execute("DELETE FROM sqlite_sequence WHERE name='OrderItems'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='Orders'")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='Products'")

    demo_products = [
        ("chips", 1.00, 50, 10, None),
        ("soda", 1.25, 40, 10, None),
        ("candy", 1.75, 30, 8, None),
        ("water", 0.50, 60, 15, None),
        ("energy drink", 3.25, 30, 5, None),
        ("protein bar", 2.25, 18, 6, None),
    ]

    cursor.executemany("""
        INSERT INTO Products (name, price, quantity, reorder_level, image_url)
        VALUES (?, ?, ?, ?, ?)
    """, demo_products)

    demo_orders = [
        ("2026-06-01", 1, 12),
        ("2026-06-02", 2, 8),
        ("2026-06-03", 3, 6),
        ("2026-06-04", 1, 10),
        ("2026-06-05", 4, 15),
        ("2026-06-06", 5, 7),
        ("2026-06-07", 6, 5),
        ("2026-06-08", 1, 9),
        ("2026-06-09", 5, 6),
        ("2026-06-10", 2, 10),
    ]

    for order_date, product_id, qty in demo_orders:
        cursor.execute("""
            INSERT INTO Orders (order_date)
            VALUES (?)
        """, (order_date,))

        order_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO OrderItems (order_id, product_id, quantity)
            VALUES (?, ?, ?)
        """, (order_id, product_id, qty))

        cursor.execute("""
            UPDATE Products
            SET quantity = quantity - ?
            WHERE product_id = ?
        """, (qty, product_id))

    conn.commit()
    conn.close()

# ---------------- DATABASE INIT ----------------

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            reorder_level INTEGER NOT NULL,
            image_url TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS OrderItems (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES Orders(order_id),
            FOREIGN KEY(product_id) REFERENCES Products(product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Password Handeling (Hashing, Creation, Login)
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Users (username, password_hash)
            VALUES (?, ?)
        """, (username, hash_password(password)))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success

def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT password_hash FROM Users WHERE username = ?
    """, (username,))
    result = cursor.fetchone()

    conn.close()

    if result is None:
        return False

    return result[0] == hash_password(password)


def get_revenue_over_time():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT o.order_date, SUM(oi.quantity * p.price) AS revenue
        FROM Orders o
        JOIN OrderItems oi ON o.order_id = oi.order_id
        JOIN Products p ON oi.product_id = p.product_id
        WHERE o.order_date IS NOT NULL
        GROUP BY o.order_date
        ORDER BY o.order_date
    """, conn)
    conn.close()
    return df

def update_product_quantity(product_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Products
        SET quantity = quantity + ?
        WHERE product_id = ?
    """, (amount, product_id))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Quantity updated successfully"}

def update_product(product_id, name, price, quantity, reorder_level):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Products
            SET name = ?, price = ?, quantity = ?, reorder_level = ?
            WHERE product_id = ?
        """, (name.strip().lower(), price, quantity, reorder_level, product_id))

        conn.commit()
        conn.close()

        return {"success": True, "message": "Product updated successfully"}

    except Exception as e:
        conn.close()
        return {"success": False, "message": str(e)}
    
def get_inventory_value():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(price * quantity)
        FROM Products
    """)

    result = cursor.fetchone()[0]
    conn.close()

    return result or 0.0

def smart_reorder_df():
    conn = get_connection()

    orders_df = pd.read_sql_query("""
        SELECT product_id, quantity
        FROM OrderItems
    """, conn)

    products_df = pd.read_sql_query("""
        SELECT product_id, name, quantity, reorder_level
        FROM Products
    """, conn)

    if products_df.empty:
        conn.close()
        return pd.DataFrame(columns=[
            "product_id", "name", "current_stock", "reorder_level",
            "predicted_demand", "suggested_reorder", "status"
        ])

    results = []

    for _, product in products_df.iterrows():
        pid = product["product_id"]
        name = product["name"]
        current_stock = product["quantity"]
        reorder_level = product["reorder_level"]

        product_orders = orders_df[orders_df["product_id"] == pid].reset_index(drop=True)

        if product_orders.empty:
            predicted_demand = 0
        elif len(product_orders) < 2:
            predicted_demand = int(product_orders["quantity"].iloc[-1])
        else:
            product_orders["time"] = range(len(product_orders))
            X = product_orders[["time"]]
            y = product_orders["quantity"]

            model = LinearRegression()
            model.fit(X, y)

            next_time = pd.DataFrame({"time": [len(product_orders)]})
            predicted_demand = round(max(0, model.predict(next_time)[0]))

        # Simple reorder rule:
        # target stock = reorder_level + predicted_demand
        target_stock = reorder_level + predicted_demand

        if current_stock < target_stock:
            suggested_reorder = target_stock - current_stock
            status = "REORDER"
        else:
            suggested_reorder = 0
            status = "OK"

        results.append({
            "product_id": pid,
            "name": name,
            "current_stock": current_stock,
            "reorder_level": reorder_level,
            "predicted_demand": predicted_demand,
            "suggested_reorder": suggested_reorder,
            "status": status
        })

    conn.close()
    return pd.DataFrame(results)

# Ensure database tables exist
init_database()
