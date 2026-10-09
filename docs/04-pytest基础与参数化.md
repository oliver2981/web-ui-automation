# 04 pytest 基础与参数化

> 这篇讲测试框架 pytest:测试函数怎么写、断言是什么、fixture 是什么,以及本项目的参数化登录用例。看完之后,你应该能看懂 `tests/` 和 `conftest.py` 里的一切。

---

## 一、pytest 是什么?

**pytest 是 Python 里最流行的测试框架。** 它负责:找到你的测试、运行它们、报告哪些通过哪些失败。

它有几个特别贴心的地方:

- **找到测试的方式很简单**:文件夹/文件名叫 `test_*.py` 或 `*_test.py`,函数名以 `test_` 开头,pytest 就自动认得它是测试。
- **断言直接用 Python 自带的 `assert`**,不用学一套新的 API。
- **fixture 机制**帮你做测试前的准备(比如"先登录")。

本项目 `pytest.ini` 里配置了"测试都放在 `tests/`":

```ini
[pytest]
addopts = -v --alluredir=allure-results
testpaths = tests
```

---

## 二、测试函数与断言

**测试函数**:名字以 `test_` 开头、里面写检查逻辑的函数。看本项目最小的一个,`tests/test_smoke.py`:

```python
# 最小的冒烟测试:确认项目配置能被正常导入
from config.settings import BASE_URL


def test_base_url_is_configured():
    assert BASE_URL == "https://www.saucedemo.com/"
```

- `def test_base_url_is_configured():` —— 一个测试函数。名字必须以 `test_` 开头。
- `assert BASE_URL == "https://www.saucedemo.com/"` —— **断言**。

**断言(assert)是什么?** 一句话:**"我断定这里应该是这样,如果不是,就让测试失败。"**

- `assert` 后面的表达式结果为 `True`,测试**通过**。
- 结果为 `False`,测试**失败**,pytest 会告诉你这一行出错了。

上例就是在断言"配置里的站点地址确实是对的那个网址"。这个测试看着没啥业务价值,它的作用是**冒烟测试**——确认项目的基本配置能被正常导入,环境没坏。

再看一个真实的业务断言,`tests/test_cart.py`:

```python
def test_added_item_appears_in_cart(logged_in):
    """加入购物车后,购物车里应能看到这件商品。"""
    products = ProductsPage(logged_in)
    products.add_backpack_to_cart()
    products.go_to_cart()

    cart = CartPage(logged_in)
    assert cart.get_item_count() == 1
    assert "Sauce Labs Backpack" in cart.get_item_names()
```

- `assert cart.get_item_count() == 1` —— 断言购物车里的商品数量等于 1。
- `assert "Sauce Labs Backpack" in cart.get_item_names()` —— 断言商品列表里包含 "Sauce Labs Backpack"。`in` 是 Python 判断"某个东西在不在里面"的写法。

一个测试函数可以有多条断言,任何一条不满足就会失败。

---

## 三、fixture 是什么?

**fixture(夹具)= 测试前的"准备工作",可以复用。**

打个比方:你要测"登录后能不能加购",每个这种用例都需要"先登录好"。难道每个用例都写一遍登录步骤?太笨了。fixture 就是把这些重复的准备工作抽出来,谁需要谁就用。

**怎么用 fixture?** 把 fixture 的名字写成测试函数的**参数**就行了。pytest 看到参数名,会去找同名的 fixture,先执行它,再把结果传进函数。

### 本项目的 `logged_in` fixture

打开 `conftest.py`:

```python
# pytest 的公共配置与 fixture 都放这里。
import re
from datetime import datetime
from pathlib import Path

import pytest

from config.settings import BASE_URL, STANDARD_USER, STANDARD_PASSWORD
from pages.login_page import LoginPage


@pytest.fixture
def logged_in(page):
    """打开站点并以 standard_user 登录,返回已登录的 page。"""
    page.goto(BASE_URL)
    LoginPage(page).login(STANDARD_USER, STANDARD_PASSWORD)
    return page
```

逐行看:

- `@pytest.fixture` —— **装饰器**,写在函数头上,告诉 pytest"这个函数是一个 fixture"。(装饰器 = 给函数贴的一个标签。)
- `def logged_in(page):` —— fixture 本身也可以有参数!它要一个 `page`。这个 `page` 是 `pytest-playwright` 插件提供的,不需要我们自己创建。
- `page.goto(BASE_URL)` —— 打开网站首页。
- `LoginPage(page).login(STANDARD_USER, STANDARD_PASSWORD)` —— 这里一行做了两件事:`LoginPage(page)` 创建登录页对象,`.login(...)` 调用登录。用 `config/settings.py` 里的常量作为账号密码。
- `return page` —— **把已经登录好的 `page` 返回出去**。谁用了这个 fixture,谁拿到的就是"已经登录"的页面。

> **`conftest.py` 是什么?** 名字固定,放在项目根目录,pytest 会**自动加载**。放公共 fixture 和钩子最合适——放在这里的东西,整个项目都能用,不用 import。

### 用例怎么用 `logged_in`?

看 `tests/test_products.py`:

```python
from pages.products_page import ProductsPage


def test_products_title_after_login(logged_in):
    """登录后应进入商品页。"""
    assert ProductsPage(logged_in).get_title() == "Products"
```

注意测试函数括号里的 `logged_in`。因为名字匹配,pytest 会:

1. 发现这个测试需要 `logged_in`;
2. 执行 `logged_in` fixture(它会拿到一个 `page`,打开网站、登录好,再返回 `page`);
3. 把返回的 `page` 传给测试函数,函数里用 `logged_in` 这个名字接收(其实就是那个登录好的 page)。

于是测试函数**一上来就是"已登录"状态**,可以直接干活。而登录那一堆步骤,一个字都没出现在测试里。

**对比 `tests/test_login.py`**:登录相关用例**不能**用 `logged_in`(因为要测的就是登录本身),所以它接收的是原始的 `page`,自己决定输什么账号:

```python
def test_login_success(page):
    """标准用户应成功登录并进入商品页。"""
    login = LoginPage(page)
    login.goto()
    login.login(USERS["standard"]["username"], USERS["standard"]["password"])
    products = ProductsPage(page)
    assert products.get_title() == "Products"
```

这体现了 fixture 的灵活:**该复用时复用,不该复用时就用原始 `page`。**

---

## 四、参数化:`@pytest.mark.parametrize`

### 问题:同样的逻辑,想测多组数据

"登录失败"这个逻辑,我们想测两种情况:**锁定用户**和**密码错误**。这两个用例的**步骤一模一样**,只是输入和期望的报错不同。

难道复制两份函数?不。用**参数化**:写一个函数,喂给它多组数据,它自动跑多遍。

### 参数化 + 数据文件

先看数据 `data/users.json`:

```json
{
  "standard": { "username": "standard_user", "password": "secret_sauce" },
  "locked": { "username": "locked_out_user", "password": "secret_sauce" },
  "wrong_password": { "username": "standard_user", "password": "wrong_password" }
}
```

这是 JSON 格式:`{}` 是"字典"(键值对),里面每个键(如 `locked`)对应一组账号信息。

再看 `tests/test_login.py` 怎么读它、怎么参数化:

```python
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
```

拆解:

**读数据文件:**

- `DATA_FILE = Path(__file__).parent.parent / "data" / "users.json"` —— 拼出数据文件的路径。
  - `Path(__file__)` 是"当前这个测试文件"的路径(即 `tests/test_login.py`)。
  - `.parent` 是它的上一级文件夹(即 `tests/`);再 `.parent` 又上一级(项目根)。
  - `/ "data" / "users.json"` 再往后拼。合起来就是 `<项目根>/data/users.json`。用这种写法,**不管你在哪个目录下跑 pytest,都能找到文件**。
- `USERS = json.loads(DATA_FILE.read_text(encoding="utf-8"))` —— 读文件内容并转成 Python 字典。
  - `read_text(encoding="utf-8")` 把文件读成一段文本(指定 UTF-8 编码,避免中文乱码)。
  - `json.loads(...)` 把这段 JSON 文本变成 Python 的字典。
  - 之后就能用 `USERS["standard"]["username"]` 这样取值了。

**参数化:**

```python
@pytest.mark.parametrize(
    "case_key, expected_word",
    [
        ("locked", "locked out"),
        ("wrong_password", "do not match"),
    ],
)
def test_login_failure(page, case_key, expected_word):
```

- `@pytest.mark.parametrize(...)` —— 参数化装饰器。它的意思是:**这个测试函数,按下面这份"数据表"跑多遍,每行跑一次。**
- 第一个参数 `"case_key, expected_word"` —— 声明两列的名字(字符串,用逗号分隔,叫 **参数名**)。
- 第二个参数是一个列表,**列表里每一行(每个元组)就是一组参数**:
  - 第一行 `("locked", "locked out")`:第一遍跑时,`case_key="locked"`、`expected_word="locked out"`。
  - 第二行 `("wrong_password", "do not match")`:第二遍跑时,`case_key="wrong_password"`、`expected_word="do not match"`。
- 于是**一个函数自动跑出两个测试**,而且 pytest 报告里会分开显示(比如 `test_login_failure[locked-locked out]` 和 `test_login_failure[wrong_password-do not match]`)。

**函数体:**

```python
    login = LoginPage(page)
    login.goto()
    login.login(USERS[case_key]["username"], USERS[case_key]["password"])
    assert expected_word in login.get_error_message().lower()
```

- `login.login(USERS[case_key]["username"], ...)` —— 用 `case_key` 从 `USERS` 里取账号。第一次跑时 `case_key` 是 `"locked"`,就取到 `locked_out_user`;第二次跑就是 `wrong_password` 那组。
- `assert expected_word in login.get_error_message().lower()` —— 断言期望的那个词出现在报错信息里。
  - `login.get_error_message()` 拿到页面上的报错文字。
  - `.lower()` 把文字全转成小写,这样不区分大小写,更稳。
  - `expected_word in ...` 判断期望词是不是包含在里面。
  - 第一次期望报错里有 "locked out"(被锁定);第二次期望有 "do not match"(密码不匹配)。

**参数化的好处**:加法式扩展。以后想再加一种"空用户名"的情况,只要往列表里加一行 `("empty", "Username is required")`,再往 `users.json` 里加一组账号,**函数体一个字都不用改**。这就是"一份逻辑,多组数据"。

> **注意**:本项目只做了这一处参数化,并且数据放在 `data/users.json` 里,没有用外部的 CSV/Excel。数据驱动的方式可以更复杂,但当前项目就到此为止——够用就好。

---

## 五、pytest 运行时的几个常用命令

```bash
pytest                       # 跑全部用例
pytest tests/test_login.py   # 只跑登录用例文件
pytest -k login              # 只跑名字里含 "login" 的用例
pytest -v                    # 详细输出(本项目已在 pytest.ini 里默认开启)
pytest --headed              # 打开浏览器窗口跑(来自 pytest-playwright)
```

`pytest.ini` 的 `addopts` 已经默认带了 `-v` 和 `--alluredir=allure-results`,所以直接 `pytest` 就会自动输出结果文件,供后面生成报告。

---

## 六、小结

- **测试函数**:`test_` 开头;pytest 自动发现并运行。
- **断言**:用 `assert`,断定某事为真;为假则测试失败。
- **fixture**:可复用的"准备工作"(`conftest.py` 里的 `logged_in`),把 fixture 名写成函数参数即可使用。
- **参数化**:`@pytest.mark.parametrize` 让一份逻辑跑多组数据;本项目用它覆盖"锁定用户/密码错误"两种登录失败,数据来自 `data/users.json`。

下一篇《05 元素定位与断言》专门讲"怎么找元素最稳"和"断言怎么写得更清楚"。
