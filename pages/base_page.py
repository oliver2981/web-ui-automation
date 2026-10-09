# 所有页面对象的基类:把"点击/输入/取文本"这些公共操作集中在一处
from playwright.sync_api import Page

from utils.logger import get_logger


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.log = get_logger(self.__class__.__name__)

    def open(self, url: str) -> None:
        """打开指定网址。"""
        self.log.info(f"打开页面: {url}")
        self.page.goto(url)

    def click(self, locator: str) -> None:
        """点击元素。"""
        self.log.info(f"点击: {locator}")
        self.page.locator(locator).click()

    def fill(self, locator: str, text: str) -> None:
        """在输入框里填入文本。"""
        self.log.info(f"输入 {text} -> {locator}")
        self.page.locator(locator).fill(text)

    def text_of(self, locator: str) -> str:
        """取元素上的可见文本。"""
        return self.page.locator(locator).inner_text()

    def is_visible(self, locator: str) -> bool:
        """元素当前是否可见。"""
        return self.page.locator(locator).is_visible()
