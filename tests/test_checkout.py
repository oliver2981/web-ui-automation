from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.products_page import ProductsPage


def test_checkout_flow_completes(logged_in):
    """完整走一遍:加购 -> 进购物车 -> 结算 -> 填写信息 -> 下单成功。"""
    products = ProductsPage(logged_in)
    products.add_backpack_to_cart()
    products.go_to_cart()

    cart = CartPage(logged_in)
    cart.go_to_checkout()

    checkout = CheckoutPage(logged_in)
    checkout.fill_info("Test", "User", "610000")
    checkout.continue_to_overview()
    checkout.finish()

    assert checkout.get_complete_message() == "Thank you for your order!"
