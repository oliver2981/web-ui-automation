# 03 Page Object 模式详解

> 这篇讲本项目最核心的设计——**Page Object**(页面对象模式)。看完之后,你应该能解释"为什么要把页面封装成类"以及"继承是怎么回事"。

---

## 一、先看个"不封装"的反例

假设你**不用** Page Object,直接在测试里操作元素。登录用例可能长这样:

```python
def test_login_success(page):
    page.goto("https://www.saucedemo.com/")
    page.locator("[data-test='username']").fill("standard_user")
    page.locator("[data-test='password']").fill("secret_sauce")
    page.locator("[data-test='login-button']").click()
    assert page.locator("[data-test='title']").inner_text() == "Products"


def test_another_login(page):
    page.goto("https://www.saucedemo.com/")
    page.locator("[data-test='username']").fill("standard_user")
    page.locator("[data-test='password']").fill("secret_sauce")
    page.locator("[data-test='login-button']").click()
    assert page.locator("[data-test='title']").inner_text() == "Inventory"
```

看出来问题了吗?

1. **`"[data-test='username']"` 这个字符串,到处复制粘贴**。哪天网站改版,用户名输入框的属性变了,你得在**每一个**测试里改,漏一个就挂。
2. **测试里混着一堆"页面细节"**。读用例的人得先看懂一堆选择器,才明白"哦这是登录"。
3. **"登录"这一步重复写**。十个用例要登录,就写十遍。

**Page Object 模式就是为了解决这三个问题。**

---

## 二、Page Object 的核心思想

一句话:**把每个网页封装成一个类。类里放两样东西——(1)这个页面上的元素怎么找;(2)能对这个页面做什么操作。测试用例只调方法,不碰元素。**

好处正是反例的三个痛点的反面:

- **改一处、到处生效**:选择器只写一次,网站变了只改一个文件。
- **测试用例变干净**:`login.login(...)` 一眼看懂,没有选择器干扰。
- **操作可复用**:登录动作写一次,所有用例都能调。

本项目里,`pages/login_page.py` 就是"登录页"这个类,`pages/products_page.py` 是"商品页",以此类推。

---

## 三、逐行讲解 `BasePage`

`BasePage` 是所有页面对象的**基类(父类)**。它把"点击、输入、取文本"这些**每个页面都会用到**的操作集中在一处,避免每个页面各写一遍。

看 `pages/base_page.py`:

```python
# 所有页面对象的基类:把"点击/输入/取文本"这些公共操作集中在一处
from playwright.sync_api import Page

from utils.logger import get_logger


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.log = get_logger(self.__class__.__name__)
```

逐行看:

- `from playwright.sync_api import Page` —— 从 Playwright 导入 `Page` 类型,用于类型提示。
- `from utils.logger import get_logger` —— 导入本项目自己的日志工具。
- `class BasePage:` —— 定义基类。
- `def __init__(self, page)` —— **构造方法**,创建这个类时会自动执行。它接收一个 `page`(浏览器标签页)。
- `self.page = page` —— 把传进来的 `page` 存到对象自己身上(`self` 指"这个对象自己")。这样类里其他方法就能通过 `self.page` 用到它。
- `self.log = get_logger(self.__class__.__name__)` —— 创建这个对象专属的日志器。`self.__class__.__name__` 是"当前类的名字",所以 `LoginPage` 实例的日志会带上 `LoginPage` 字样,一眼看出日志来自哪个页面。

接着是几个公共方法:

```python
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
```

- `open(url)`:打开网页。先记日志再 `page.goto(url)`。
- `click(locator)`:点击。先记日志再 `page.locator(locator).click()`。
- `fill(locator, text)`:填文本。先记日志再 `.fill(text)`。
- `text_of(locator)`:返回元素的可见文字。直接 `return`,不记日志。
- `is_visible(locator)`:返回"元素是否可见"(True/False)。

注意 `-> None` 和 `-> str`:那是**类型提示**,标出"这个方法返回什么"。`None` 表示"不返回东西,只执行动作";`str` 表示"返回一个字符串"。类型提示不影响运行,但让代码更好读、IDE 能帮你检查。

**小结 BasePage 的价值**:把 5 个最常用的浏览器操作包成统一的方法,顺便统一加日志。所有页面类继承它之后,就自动拥有这 5 个方法。

---

## 四、`LoginPage` 如何继承 `BasePage`

打开 `pages/login_page.py`:

```python
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
```

关键的一行是:

```python
class LoginPage(BasePage):
```

括号里的 `BasePage` 就是**继承**。意思是:`LoginPage` 是 `BasePage` 的"子类",它**自动拥有** `BasePage` 的全部方法(`open`、`click`、`fill`、`text_of`、`is_visible`),不需要重写。

所以 `login()` 里可以直接写 `self.fill(...)`、`self.click(...)` —— 这两个方法 `LoginPage` 自己没定义,是从父类 `BasePage` **继承**来的。

`LoginPage` 自己新增的东西:

- **类属性**:4 个定位字符串。它们只属于登录页,所以放在这里而不是基类。
- **`goto()`**:打开登录页。它调用了父类的 `self.open(BASE_URL)`。注意 `BASE_URL` 来自 `config/settings.py`,体现了"配置集中管理"。
- **`login(username, password)`**:登录动作。
- **`get_error_message()`**:取登录报错的文字。它调用父类的 `self.text_of(...)`。

**一句话理解继承**:`BasePage` 提供"通用操作",子类只写"这个页面独有的元素和动作"。这叫"公共的抽到父类,独有的放子类"。

---

## 五、对比:不封装 vs. Page Object

同一个"加背包进购物车"的操作,两种写法:

**不封装写法**(直接在测试里):

```python
def test_add_backpack(page):
    page.goto("https://www.saucedemo.com/")
    page.locator("[data-test='username']").fill("standard_user")
    page.locator("[data-test='password']").fill("secret_sauce")
    page.locator("[data-test='login-button']").click()
    page.locator("[data-test='add-to-cart-sauce-labs-backpack']").click()
    assert page.locator("[data-test='shopping-cart-badge']").inner_text() == "1"
```

**Page Object 写法**(本项目实际的样子,`tests/test_products.py`):

```python
from pages.products_page import ProductsPage


def test_add_backpack_updates_cart_badge(logged_in):
    """把背包加入购物车,购物车角标应显示 1。"""
    products = ProductsPage(logged_in)
    products.add_backpack_to_cart()
    assert products.get_cart_count() == "1"
```

**差别一眼可见:**

| 对比项 | 不封装 | Page Object |
|---|---|---|
| 选择器写在哪 | 散落在每个测试里 | 集中在页面类里 |
| 网站改版要改几处 | 每个用例都要改 | 只改页面类一处 |
| 测试用例读起来 | 一堆选择器,看不出业务 | `products.add_backpack_to_cart()`,像读句子 |
| 操作能否复用 | 不能,只能复制粘贴 | 能,方法一调即可 |
| 登录等重复步骤 | 每个用例重复写 | 用 `logged_in` fixture 一次搞定(见第 04 篇) |

**再强调一遍核心价值**:Page Object 把"页面长什么样"和"我们要测什么"分开了。以后网站改版,你只需要改 `pages/` 里的选择器,`tests/` 一行不用动。

---

## 六、本项目的页面类一览

| 页面类 | 文件 | 负责 |
|---|---|---|
| `BasePage` | `pages/base_page.py` | 通用操作(点击/输入/取文本等),被其他类继承 |
| `LoginPage` | `pages/login_page.py` | 登录页:输入账号密码、取报错 |
| `ProductsPage` | `pages/products_page.py` | 商品页:取标题、加购、取角标、进购物车、排序 |
| `CartPage` | `pages/cart_page.py` | 购物车页:数商品、取商品名、进结算 |
| `CheckoutPage` | `pages/checkout_page.py` | 结算页:填收货信息、继续、完成、取成功文案 |

它们**全部继承自 `BasePage`**,所以都自带 `click`、`fill`、`text_of` 这些方法。

---

## 七、小结

- Page Object = **把每个页面封装成类**,类里放"元素定位"和"页面操作"。
- 好处:**改一处、到处生效**;测试用例干净可读;操作可复用。
- `BasePage` 是父类,放通用操作;`LoginPage` 等子类通过 `class X(BasePage)` 继承,自动拥有父类方法,只写自己独有的东西。
- 判断该放哪一层:元素定位和"怎么点" → `pages/`;"要检查什么结果" → `tests/`。

下一篇《04 pytest 基础与参数化》讲测试框架本身:测试函数、断言、fixture、参数化。
