# 结算页:填写收货信息、确认订单、下单完成
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    FIRST_NAME = "[data-test='firstName']"
    LAST_NAME = "[data-test='lastName']"
    POSTAL_CODE = "[data-test='postalCode']"
    CONTINUE_BUTTON = "[data-test='continue']"
    FINISH_BUTTON = "[data-test='finish']"
    COMPLETE_HEADER = "[data-test='complete-header']"

    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        """填写收货人信息。"""
        self.fill(self.FIRST_NAME, first_name)
        self.fill(self.LAST_NAME, last_name)
        self.fill(self.POSTAL_CODE, postal_code)

    def continue_to_overview(self) -> None:
        """点击继续,进入订单确认页。"""
        self.click(self.CONTINUE_BUTTON)

    def finish(self) -> None:
        """点击完成,提交订单。"""
        self.click(self.FINISH_BUTTON)

    def get_complete_message(self) -> str:
        """返回下单成功页的标题文字。"""
        return self.text_of(self.COMPLETE_HEADER)
