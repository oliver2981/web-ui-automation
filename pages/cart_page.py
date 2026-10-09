# 购物车页:查看已选商品、进入结算
from pages.base_page import BasePage


class CartPage(BasePage):
    CART_ITEMS = ".cart_item"          # 购物车里的每一行
    ITEM_NAME = ".inventory_item_name"  # 每行里的商品名
    CHECKOUT_BUTTON = "[data-test='checkout']"

    def get_item_count(self) -> int:
        """返回购物车里的商品行数。"""
        self._wait_until_loaded()
        return self.page.locator(self.CART_ITEMS).count()

    def get_item_names(self) -> list[str]:
        """返回购物车里所有商品的名字。"""
        self._wait_until_loaded()
        return self.page.locator(self.ITEM_NAME).all_inner_texts()

    def go_to_checkout(self) -> None:
        """点击结算按钮,进入填写信息页。"""
        self.click(self.CHECKOUT_BUTTON)

    def _wait_until_loaded(self) -> None:
        """等购物车页渲染完成:结算按钮出现,就说明页面加载好了。"""
        self.page.locator(self.CHECKOUT_BUTTON).wait_for()
