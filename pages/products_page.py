# 商品页:登录成功后进入的页面
from pages.base_page import BasePage


class ProductsPage(BasePage):
    TITLE = "[data-test='title']"

    def get_title(self) -> str:
        """返回页面标题(登录成功时是 'Products')。"""
        return self.text_of(self.TITLE)
