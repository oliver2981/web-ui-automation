# 02 Playwright 快速上手

> 这篇带你认识 Playwright:它是什么、核心概念是什么、本项目怎么用它。看完之后,你应该能看懂 `pages/login_page.py` 里那段登录代码。

---

## 一、Playwright 是什么?

**Playwright 是一个"能用代码操纵浏览器"的工具库**(由微软出品)。你写 `page.fill(...)`,它就去网页上真的把字打进去;你写 `page.click(...)`,它就真的去点一下。

它和 Selenium(另一个很有名的同类工具)的区别,一句话概括:

> **Playwright 内置了"自动等待",你写元素操作时不用自己加 `sleep` / 显式等待,它自己会等元素出现再操作;Selenium 默认不会,经常需要你手动写等待。**

这一点对新手特别友好——**90% 的 UI 自动化翻车都是"没等页面加载完就去点,结果点了个空的"**,Playwright 帮你把这个坑填了一大半。

---

## 二、三个核心概念:page、locator、自动等待

### 1. `page` —— 一个浏览器标签页

`page` 就是"一个打开着的网页标签"。你的几乎所有操作,都是在 `page` 上进行的:打开网址、找元素、点击。

在本项目里,`page` **不需要你自己创建**。`pytest-playwright` 这个插件会自动帮你准备好一个 `page` 并传进测试函数。比如 `tests/test_login.py`:

```python
def test_login_success(page):
    """标准用户应成功登录并进入商品页。"""
    login = LoginPage(page)
    ...
```

看到没?测试函数有个参数 `page`,这就是插件送进来的、现成的浏览器标签页。你要做的只是把它交给页面对象。

### 2. `locator` —— "怎么找到那个元素"

网页上有一堆按钮、输入框。`locator` 就是**一把"定位钥匙"**,告诉 Playwright:"我要找的是这个元素。"

本项目统一定位长这样:

```python
USERNAME_INPUT = "[data-test='username']"
```

这是一条 CSS 选择器,意思是"找到那个 `data-test` 属性等于 `username` 的元素"(也就是用户名输入框)。第 05 篇会专门讲定位。

创建 locator 的写法是 `page.locator("选择器")`,比如:

```python
self.page.locator(locator).click()
```

### 3. 自动等待 —— Playwright 最省心的地方

当你写:

```python
page.locator("[data-test='login-button']").click()
```

Playwright 在真正点击前,会**自动等这个按钮变为"可点击"状态**(存在、可见、没被别的元素盖住)。如果等了 10 秒还没出现,它才报错。

这省掉了传统做法里那一堆 `time.sleep(3)` 或等待条件。**结论:本项目几乎不写 `sleep`**,靠的就是自动等待。

---

## 三、用本项目的 `login()` 举例

打开 `pages/login_page.py`,看这段:

```python
class LoginPage(BasePage):
    # 元素定位(用站点自带的 data-test 属性,最稳定)
    USERNAME_INPUT = "[data-test='username']"
    PASSWORD_INPUT = "[data-test='password']"
    LOGIN_BUTTON = "[data-test='login-button']"
    ERROR_MESSAGE = "[data-test='error']"

    def login(self, username: str, password: str) -> None:
        """输入账号密码并点击登录。"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
```

逐行拆:

- `USERNAME_INPUT = "[data-test='username']"` 这几行是**类属性**,把"定位钥匙"存起来,后面重复用。写一次,到处用。
- `def login(self, username, password)` —— 定义一个"登录"动作,需要传入用户名和密码两个字符串(`: str` 是类型提示,告诉读者"这里应该是字符串")。
- `self.fill(self.USERNAME_INPUT, username)` —— 调 `BasePage` 里的 `fill` 方法,在用户名输入框里填 `username`。
- `self.fill(self.PASSWORD_INPUT, password)` —— 同理,填密码。
- `self.click(self.LOGIN_BUTTON)` —— 点击登录按钮。

**`fill` 和 `click` 具体干了什么?** 它们定义在 `pages/base_page.py` 里:

```python
def click(self, locator: str) -> None:
    """点击元素。"""
    self.log.info(f"点击: {locator}")
    self.page.locator(locator).click()

def fill(self, locator: str, text: str) -> None:
    """在输入框里填入文本。"""
    self.log.info(f"输入 {text} -> {locator}")
    self.page.locator(locator).fill(text)
```

- `click` 里先记一条日志(`self.log.info(...)`,方便排查问题时看到"我点到哪了"),然后 `self.page.locator(locator).click()` —— 找到元素并点击。
- `fill` 里先记日志,然后 `.fill(text)` —— 找到输入框并把文本填进去。注意 `fill` 会**先清空**输入框再填,比手动按键盘更干净。

所以整个 `login()` 的实质就是:**填用户名 → 填密码 → 点登录按钮**,而这三个动作背后都是 Playwright 在操作真浏览器。

---

## 四、最小可运行示例

下面这段不需要放进本项目,复制到任意一个 `.py` 文件里就能单独跑,**用来感受 Playwright**:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 启动 Chromium 浏览器(默认无头,想看到界面就加 headless=False)
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # 打开登录页
    page.goto("https://www.saucedemo.com/")

    # 填账号密码并登录
    page.locator("[data-test='username']").fill("standard_user")
    page.locator("[data-test='password']").fill("secret_sauce")
    page.locator("[data-test='login-button']").click()

    # 打印登录后的页面标题,应该看到 Products
    print(page.locator("[data-test='title']").inner_text())

    browser.close()
```

逐行说明:

- `with sync_playwright() as p:` —— 打开 Playwright 的"同步模式"(代码一行行顺序执行,好懂)。`with ... as` 是一种写法,保证用完自动清理。
- `p.chromium.launch(headless=False)` —— 启动 Chromium 浏览器。`headless=False` 表示"我要看见窗口"。
- `browser.new_page()` —— 开一个新标签页。
- `page.goto(...)` —— 打开网址。
- `page.locator(...).fill(...)` / `.click()` —— 和我们项目里一模一样的操作。
- `page.locator(...).inner_text()` —— 读元素的文字内容。
- `browser.close()` —— 关掉浏览器。

> **对比**:在实际项目里,上面这些"启动浏览器、关浏览器"的活儿由 `pytest-playwright` 插件自动做了。所以我们写测试时,只要在函数参数里写个 `page`,别的都不用管。这也是为什么本项目的 `pages/base_page.py` 直接从 `page` 开始,而不管浏览器怎么来的。

补充一个概念:`page.locator(...)` 返回的 locator 还可以做更多事,本项目用到的有:

| 方法 | 作用 | 本项目出处 |
|---|---|---|
| `.fill(text)` | 填入文本 | `pages/base_page.py` |
| `.click()` | 点击 | `pages/base_page.py` |
| `.inner_text()` | 取可见文本 | `pages/base_page.py` 的 `text_of` |
| `.is_visible()` | 是否可见 | `pages/base_page.py` |
| `.count()` | 符合条件的元素有几个 | `pages/cart_page.py` |
| `.all_inner_texts()` | 取所有匹配元素的文本,返回列表 | `pages/cart_page.py` |
| `.wait_for()` | 等元素出现 | `pages/cart_page.py` |
| `.select_option(...)` | 下拉框选一项 | `pages/products_page.py` |

这些你不用背,知道"Playwright 都能干"就行,用到了再查。

---

## 五、小结

- Playwright 是操纵浏览器的库,**内置自动等待**,不用自己写 sleep,这是它相对 Selenium 最大的省心点。
- 三个核心:`page`(标签页)、`locator`(定位钥匙)、自动等待(等元素就绪再操作)。
- 本项目里 `page` 由 pytest 插件自动提供,我们只管用。
- `login()` 的实质:填用户名 → 填密码 → 点按钮,底层是 Playwright 的 `fill` 和 `click`。

下一篇《03 Page Object 模式详解》讲:为什么要专门写 `pages/` 里那些类,而不是直接在测试里点来点去。
