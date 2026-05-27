from smartstock.database.connection import get_connection

def create_order(product_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Orders (product_id, quantity)
        VALUES (?, ?)
    """, (product_id, quantity))

    # Reduce product stock
    cursor.execute("""
        UPDATE Products
        SET quantity = quantity - ?
        WHERE id = ?
    """, (quantity, product_id))

    conn.commit()
    conn.close()


def get_all_orders():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Orders.id, Products.name, Orders.quantity, Orders.created_at
        FROM Orders
        JOIN Products ON Orders.product_id = Products.id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows
