from smartstock.database.products import (
    add_product,
    get_all_products,
    update_product,
    delete_product
)

def list_products():
    return get_all_products()

def create_product(name, price, quantity, supplier_id=None):
    return add_product(name, price, quantity, supplier_id)

def modify_product(product_id, name=None, price=None, quantity=None):
    return update_product(product_id, name, price, quantity)

def remove_product(product_id):
    return delete_product(product_id)
