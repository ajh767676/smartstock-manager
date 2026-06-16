import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory_core import (
    add_product_db,
    get_products,
    create_order_db,
    delete_order_db
)


def test_cancel_order_restores_inventory():

    add_product_db(
        "Cancel Test Product",
        4.99,
        10,
        2
    )

    products = get_products()

    product = products[
        products["name"] == "cancel test product"
    ].iloc[-1]

    product_id = int(product["product_id"])
    starting_quantity = int(product["quantity"])

    order_result = create_order_db(product_id, 2)

    assert order_result["success"] == True

    order_id = order_result["order_id"]

    cancel_result = delete_order_db(order_id)

    assert cancel_result["success"] == True

    products = get_products()

    updated_product = products[
        products["product_id"] == product_id
    ].iloc[0]

    ending_quantity = int(updated_product["quantity"])

    assert ending_quantity == starting_quantity