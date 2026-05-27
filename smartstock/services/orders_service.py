from smartstock.database.orders import (
    create_order,
    get_all_orders
)

def place_order(product_id, quantity):
    return create_order(product_id, quantity)

def list_orders():
    return get_all_orders()
