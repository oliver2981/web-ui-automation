# pytest 的公共配置与 fixture 都放这里。
import re
from datetime import datetime
from pathlib import Path

import pytest

from config.settings import STANDARD_USER, STANDARD_PASSWORD
from pages.login_page import LoginPage


@pytest.fixture
def logged_in(page):
    """打开站点并以 standard_user 登录,返回已登录的 page。"""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login(STANDARD_USER, STANDARD_PASSWORD)
    return page


SCREENSHOT_DIR = Path("screenshots")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """用例失败时自动截图,并附加到 Allure 报告。"""
    outcome = yield
    report = outcome.get_result()

    # 只在"测试体"这一阶段失败时截图
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None:
            SCREENSHOT_DIR.mkdir(exist_ok=True)
            safe_name = re.sub(r"[^\w\-]", "_", item.nodeid)
            path = SCREENSHOT_DIR / f"{safe_name}_{datetime.now():%Y%m%d_%H%M%S}.png"
            page.screenshot(path=str(path))
            try:
                import allure
                allure.attach.file(
                    str(path),
                    name="失败截图",
                    attachment_type=allure.attachment_type.PNG,
                )
            except ImportError:
                pass
