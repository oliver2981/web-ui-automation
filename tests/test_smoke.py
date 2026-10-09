# 最小的冒烟测试:确认项目配置能被正常导入
from config.settings import BASE_URL


def test_base_url_is_configured():
    assert BASE_URL == "https://www.saucedemo.com/"
