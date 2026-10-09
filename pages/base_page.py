# 所有页面对象的基类:把"点击/输入/取文本"这些公共操作集中在一处
from playwright.sync_api import Error, Page

from config.settings import DEFAULT_TIMEOUT_MS, NAVIGATION_TIMEOUT_MS
from utils.logger import get_logger


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.log = get_logger(self.__class__.__name__)
        # 元素操作的默认等待时间,用配置里的值
        self.page.set_default_timeout(DEFAULT_TIMEOUT_MS)
        # 导航单独放宽:导航比元素等待慢,给足 30s 以上,避免更严格
        self.page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)

    def open(self, url: str) -> None:
        """打开指定网址;首次超时则重试一次。"""
        self.log.info(f"打开页面: {url}")
        try:
            self.page.goto(url)
        except Error:
            self.log.warning(f"打开页面超时,重试一次: {url}")
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
