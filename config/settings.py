# 项目全局配置:所有"改一处、到处生效"的常量都放这里

# 被测站点首页
BASE_URL = "https://www.saucedemo.com/"

# 站点自带的公开测试账号(密码对所有账号都相同)
STANDARD_USER = "standard_user"
STANDARD_PASSWORD = "secret_sauce"

# 元素等待超时(毫秒)
DEFAULT_TIMEOUT_MS = 10000

# 页面导航超时(毫秒)。导航比元素等待更慢,单独给足时间,避免比 Playwright 默认的 30s 更严格
NAVIGATION_TIMEOUT_MS = 45000
