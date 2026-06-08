import sqlite3

# Connect to database
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# Create Products table
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

# Insert a sample product
cursor.execute("""
INSERT INTO Products (name, price, quantity, reorder_level)
VALUES (?, ?, ?, ?)
""", ("Laptop", 899.99, 10, 3))

# Retrieve and display products
cursor.execute("SELECT * FROM Products")
products = cursor.fetchall()

print("Current Inventory:")
for product in products:
    print(product)

# Save and close
conn.commit()
conn.close()
