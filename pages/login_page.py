# 登录页:负责登录页的元素定位和登录动作
from config.settings import BASE_URL
from pages.base_page import BasePage


class LoginPage(BasePage):
    # 元素定位(用站点自带的 data-test 属性,最稳定)
    USERNAME_INPUT = "[data-test='username']"
    PASSWORD_INPUT = "[data-test='password']"
    LOGIN_BUTTON = "[data-test='login-button']"
    ERROR_MESSAGE = "[data-test='error']"

    def goto(self) -> None:
        """打开登录页。"""
        self.open(BASE_URL)

    def login(self, username: str, password: str) -> None:
        """输入账号密码并点击登录。"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        """返回登录失败时的错误提示文本。"""
        return self.text_of(self.ERROR_MESSAGE)
