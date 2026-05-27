from smartstock.database.connection import get_connection

def add_product(name, price, quantity, supplier_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Products (name, price, quantity, supplier_id)
        VALUES (?, ?, ?, ?)
    """, (name, price, quantity, supplier_id))

    conn.commit()
    conn.close()


def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Products")
    rows = cursor.fetchall()

    conn.close()
    return rows


def update_product(product_id, name=None, price=None, quantity=None):
    conn = get_connection()
    cursor = conn.cursor()

    if name:
        cursor.execute("UPDATE Products SET name = ? WHERE id = ?", (name, product_id))
    if price:
        cursor.execute("UPDATE Products SET price = ? WHERE id = ?", (price, product_id))
    if quantity:
        cursor.execute("UPDATE Products SET quantity = ? WHERE id = ?", (quantity, product_id))

    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
