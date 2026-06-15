import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory_core import add_product_db, get_products


def test_add_product():
    add_product_db(
        name="Test Product",
        price=9.99,
        quantity=5,
        reorder_level=2
    )

    products = get_products()

    assert len(products) > 0