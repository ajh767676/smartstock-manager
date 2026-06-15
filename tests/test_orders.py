import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory_core import (
    add_product_db,
    get_products,
    create_order_db
)


def test_order_reduces_inventory():

    add_product_db(
        "Inventory Test",
        5.00,
        10,
        2
    )

    products = get_products()

    product = products[
        products["name"] == "inventory test"
    ].iloc[-1]

    product_id = int(product["product_id"])
    starting_quantity = int(product["quantity"])

    result = create_order_db(product_id, 2)

    assert result["success"] == True

    products = get_products()

    updated_product = products[
        products["product_id"] == product_id
    ].iloc[0]

    ending_quantity = int(updated_product["quantity"])

    assert ending_quantity == starting_quantity - 2