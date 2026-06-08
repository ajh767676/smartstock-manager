from smartstock.database.connection import get_connection
import pandas as pd

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
    df = pd.read_sql_query("""
        SELECT SUM(oi.quantity * p.price) AS revenue
        FROM OrderItems oi
        JOIN Products p ON oi.product_id = p.product_id
    """, conn)
    conn.close()
    return df.iloc[0]["revenue"] or 0.0
