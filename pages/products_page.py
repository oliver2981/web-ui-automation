# 商品页:负责商品列表、加购、排序、进入购物车
from pages.base_page import BasePage


class ProductsPage(BasePage):
    TITLE = "[data-test='title']"
    CART_BADGE = "[data-test='shopping-cart-badge']"
    CART_LINK = "[data-test='shopping-cart-link']"
    SORT_DROPDOWN = "[data-test='product-sort-container']"
    # 商品列表里每个商品的名称
    PRODUCT_NAME = "[data-test='inventory-item-name']"
    # 把"Sauce Labs Backpack"加入购物车的按钮
    ADD_BACKPACK = "[data-test='add-to-cart-sauce-labs-backpack']"

    def get_title(self) -> str:
        """返回页面标题(登录成功时是 'Products')。"""
        return self.text_of(self.TITLE)

    def get_first_product_name(self) -> str:
        """返回商品列表里第一个商品的名称。"""
        # 商品名有多个,取第一个即可
        return self.page.locator(self.PRODUCT_NAME).first.inner_text()

    def add_backpack_to_cart(self) -> None:
        """把背包加入购物车。"""
        self.click(self.ADD_BACKPACK)

    def get_cart_count(self) -> str:
        """返回购物车角标上的数字(没有商品时角标不存在)。"""
        return self.text_of(self.CART_BADGE)

    def go_to_cart(self) -> None:
        """进入购物车页面。"""
        self.click(self.CART_LINK)

    def sort_by(self, option: str) -> None:
        """按指定选项排序,如 'lohi'(价格低到高)、'hilo'(价格高到低)。"""
        self.log.info(f"按 {option} 排序")
        self.page.locator(self.SORT_DROPDOWN).select_option(option)
