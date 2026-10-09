import json
from pathlib import Path

import pytest

from pages.login_page import LoginPage
from pages.products_page import ProductsPage

# 读取参数化数据
DATA_FILE = Path(__file__).parent.parent / "data" / "users.json"
USERS = json.loads(DATA_FILE.read_text(encoding="utf-8"))


def test_login_success(page):
    """标准用户应成功登录并进入商品页。"""
    login = LoginPage(page)
    login.goto()
    login.login(USERS["standard"]["username"], USERS["standard"]["password"])
    products = ProductsPage(page)
    assert products.get_title() == "Products"


@pytest.mark.parametrize(
    "case_key, expected_word",
    [
        ("locked", "locked out"),
        ("wrong_password", "do not match"),
    ],
)
def test_login_failure(page, case_key, expected_word):
    """锁定用户 / 错误密码应登录失败并给出对应报错。"""
    login = LoginPage(page)
    login.goto()
    login.login(USERS[case_key]["username"], USERS[case_key]["password"])
    assert expected_word in login.get_error_message().lower()
