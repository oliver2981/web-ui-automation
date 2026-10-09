from pages.cart_page import CartPage
from pages.products_page import ProductsPage


def test_added_item_appears_in_cart(logged_in):
    """加入购物车后,购物车里应能看到这件商品。"""
    products = ProductsPage(logged_in)
    products.add_backpack_to_cart()
    products.go_to_cart()

    cart = CartPage(logged_in)
    assert cart.get_item_count() == 1
    assert "Sauce Labs Backpack" in cart.get_item_names()
