# pytest 的公共配置与 fixture 都放这里。
import pytest

from config.settings import BASE_URL, STANDARD_USER, STANDARD_PASSWORD
from pages.login_page import LoginPage


@pytest.fixture
def logged_in(page):
    """打开站点并以 standard_user 登录,返回已登录的 page。"""
    page.goto(BASE_URL)
    LoginPage(page).login(STANDARD_USER, STANDARD_PASSWORD)
    return page
