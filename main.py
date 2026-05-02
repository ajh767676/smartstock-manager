import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression

# ---------------- PRODUCTS ----------------

def view_products():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Products")
    rows = cursor.fetchall()

    print("\n--- Product List ---")
    print("------------------------------------------------")
    for row in rows:
        print(f"{row[0]:<3} | {row[1]:<15} | ${row[2]:<8} | Qty: {row[3]:<5} | RL: {row[4]}")
    print("------------------------------------------------")

    conn.close()


def add_product():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    name = input("Enter product name: ")
    price = float(input("Enter price: "))
    quantity = int(input("Enter quantity: "))
    reorder_level = int(input("Enter reorder level: "))
    image_url = st.text_input("Image URL (optional)")


    cursor.execute("""
        INSERT INTO Products (name, price, quantity, reorder_level)
        VALUES (?, ?, ?, ?)
    """, (name, price, quantity, reorder_level))

    conn.commit()
    conn.close()

    print("✅ Product added successfully!")


def update_product():
    product_id = input("Enter Product ID to update: ")
    new_price = input("Enter new price: ")
    new_quantity = input("Enter new quantity: ")

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Products
        SET price = ?, quantity = ?
        WHERE product_id = ?
    """, (new_price, new_quantity, product_id))

    conn.commit()

    if cursor.rowcount == 0:
        print("Product not found.")
    else:
        print("Product updated successfully!")

    conn.close()


def delete_product():
    product_id = input("Enter Product ID to delete: ")

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Products WHERE product_id = ?", (product_id,))
    conn.commit()

    if cursor.rowcount == 0:
        print("Product not found.")
    else:
        print("Product deleted successfully!")

    conn.close()


# ---------------- ORDERS ----------------

def create_order():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    print("\n--- Create Order ---")

    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    for p in products:
        print(f"ID: {p[0]} | {p[1]} | Price: ${p[2]} | Qty: {p[3]}")

    product_id = int(input("Enter Product ID: "))
    order_qty = int(input("Enter quantity: "))

    cursor.execute("SELECT quantity FROM Products WHERE product_id = ?", (product_id,))
    result = cursor.fetchone()

    if result is None:
        print("❌ Product not found.")
        conn.close()
        return

    stock = result[0]

    if order_qty > stock:
        print("❌ Not enough stock!")
        conn.close()
        return

    cursor.execute("INSERT INTO Orders DEFAULT VALUES")
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

    print(f"✅ Order {order_id} created successfully!")


def view_orders_with_total():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    print("\n--- Orders ---")
    print("------------------------------------------------")

    cursor.execute("""
        SELECT o.order_id, p.name, oi.quantity, p.price,
               (oi.quantity * p.price)
        FROM Orders o
        JOIN OrderItems oi ON o.order_id = oi.order_id
        JOIN Products p ON oi.product_id = p.product_id
    """)

    rows = cursor.fetchall()

    for row in rows:
        print(f"Order {row[0]} | {row[1]:<12} | Qty: {row[2]} | Total: ${row[4]:.2f}")

    print("------------------------------------------------")

    conn.close()


def delete_order():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    order_id = int(input("Enter Order ID to delete: "))

    cursor.execute("SELECT product_id, quantity FROM OrderItems WHERE order_id = ?", (order_id,))
    items = cursor.fetchall()

    if not items:
        print("Order not found.")
        conn.close()
        return

    for product_id, qty in items:
        cursor.execute("""
            UPDATE Products
            SET quantity = quantity + ?
            WHERE product_id = ?
        """, (qty, product_id))

    cursor.execute("DELETE FROM OrderItems WHERE order_id = ?", (order_id,))
    cursor.execute("DELETE FROM Orders WHERE order_id = ?", (order_id,))

    conn.commit()
    conn.close()

    print("✅ Order deleted and inventory restored!")


# ---------------- REPORTS ----------------

def low_stock_alert():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    print("\n--- Low Stock Alert ---")

    cursor.execute("""
        SELECT name, quantity
        FROM Products
        WHERE quantity <= reorder_level
    """)

    rows = cursor.fetchall()

    for row in rows:
        print(f"⚠ {row[0]} (Qty: {row[1]})")

    conn.close()


def system_report():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Products")
    product_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Orders")
    order_count = cursor.fetchone()[0]

    print(f"Total Products: {product_count}")
    print(f"Total Orders: {order_count}")

    conn.close()


def total_revenue():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(oi.quantity * p.price)
        FROM OrderItems oi
        JOIN Products p ON oi.product_id = p.product_id
    """)

    result = cursor.fetchone()[0]

    if result:
        print(f"💰 Total Revenue: ${result:.2f}")
    else:
        print("No revenue yet.")

    conn.close()


def best_selling_product():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.name, SUM(oi.quantity)
        FROM OrderItems oi
        JOIN Products p ON oi.product_id = p.product_id
        GROUP BY p.name
        ORDER BY SUM(oi.quantity) DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    if result:
        print(f"🏆 Best Seller: {result[0]} ({result[1]} sold)")
    else:
        print("No sales data.")

    conn.close()


def search_product():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    name = input("Search product: ")

    cursor.execute("SELECT * FROM Products WHERE name LIKE ?", ('%' + name + '%',))
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()


# ---------------- AI ----------------

def forecast_demand():
    conn = sqlite3.connect("inventory.db")

    print("\n--- AI Demand Forecast ---")

    df = pd.read_sql_query("""
        SELECT product_id, quantity
        FROM OrderItems
    """, conn)

    if df.empty:
        print("Not enough data.")
        conn.close()
        return

    forecasts = {}
    cursor = conn.cursor()

    # 🔥 KEY FIX: group by product FIRST
    for pid, group in df.groupby('product_id'):

        group = group.reset_index(drop=True)

        # need at least 2 data points
        if len(group) < 2:
            continue

        # create time index PER PRODUCT
        group['time'] = range(len(group))

        X = group[['time']]
        y = group['quantity']

        model = LinearRegression()
        model.fit(X, y)

        # predict next step
        next_time = pd.DataFrame({'time': [len(group)]})
        pred = model.predict(next_time)[0]

        forecasts[pid] = round(max(0, pred))

    # 🔥 DISPLAY RESULTS (clean + safe)
    if not forecasts:
        print("Not enough data for forecasting.")
    else:
        for pid, pred in forecasts.items():
            cursor.execute("SELECT name FROM Products WHERE product_id = ?", (pid,))
            result = cursor.fetchone()

            if result:
                print(f"🔮 {result[0]} → Predicted demand: {pred}")
            else:
                print(f"⚠ Product ID {pid} not found")

    conn.close()


# ---------------- STARTUP ----------------

def startup_low_stock_check():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, quantity
        FROM Products
        WHERE quantity <= reorder_level
    """)

    rows = cursor.fetchall()

    if rows:
        print("\n⚠ LOW STOCK WARNING ⚠")
        for r in rows:
            print(f"{r[0]} → Qty: {r[1]}")

    conn.close()

def reset_database():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM OrderItems")
    cursor.execute("DELETE FROM Orders")
    cursor.execute("DELETE FROM Products")

    conn.commit()
    conn.close()

    print("✅ Database reset complete.")


# ---------------- MAIN ----------------

def main():
    startup_low_stock_check()

    while True:
        print("\n========== INVENTORY SYSTEM ==========")
        print("1.  View Products")
        print("2.  Add Product")
        print("3.  Update Product")
        print("4.  Delete Product")
        print("5.  Create Order")
        print("6.  View Orders")
        print("7.  Low Stock Alert")
        print("8.  Delete Order")
        print("9.  System Report")
        print("10. Total Revenue")
        print("11. Best Selling Product")
        print("12. Search Product")
        print("13. AI Forecast")
        print("14. Exit")
        print("99. Reset Database")

        choice = input("Enter choice: ")

        if choice == "1":
            view_products()
        elif choice == "2":
            add_product()
        elif choice == "3":
            update_product()
        elif choice == "4":
            delete_product()
        elif choice == "5":
            create_order()
        elif choice == "6":
            view_orders_with_total()
        elif choice == "7":
            low_stock_alert()
        elif choice == "8":
            delete_order()
        elif choice == "9":
            system_report()
        elif choice == "10":
            total_revenue()
        elif choice == "11":
            best_selling_product()
        elif choice == "12":
            search_product()
        elif choice == "13":
            forecast_demand()
        elif choice == "14":
            break
        elif choice == "99":
            reset_database()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()    