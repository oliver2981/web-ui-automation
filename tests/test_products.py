from pages.products_page import ProductsPage


def test_products_title_after_login(logged_in):
    """登录后应进入商品页。"""
    assert ProductsPage(logged_in).get_title() == "Products"


def test_add_backpack_updates_cart_badge(logged_in):
    """把背包加入购物车,购物车角标应显示 1。"""
    products = ProductsPage(logged_in)
    products.add_backpack_to_cart()
    assert products.get_cart_count() == "1"
