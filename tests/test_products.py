from pages.products_page import ProductsPage


def test_products_title_after_login(logged_in):
    """登录后应进入商品页。"""
    assert ProductsPage(logged_in).get_title() == "Products"


def test_add_backpack_updates_cart_badge(logged_in):
    """把背包加入购物车,购物车角标应显示 1。"""
    products = ProductsPage(logged_in)
    products.add_backpack_to_cart()
    assert products.get_cart_count() == "1"


def test_sort_by_price_low_to_high(logged_in):
    """按价格从低到高排序后,第一个商品应是最便宜的 'Sauce Labs Onesie'。"""
    products = ProductsPage(logged_in)
    # 默认按名称 A-Z 排序时,第一个是 'Sauce Labs Backpack'
    assert products.get_first_product_name() == "Sauce Labs Backpack"
    # 改成价格低到高,第一个应变成最便宜的 'Sauce Labs Onesie'
    products.sort_by("lohi")
    assert products.get_first_product_name() == "Sauce Labs Onesie"
