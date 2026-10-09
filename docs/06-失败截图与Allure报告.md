# 06 失败截图与 Allure 报告

> 这篇讲两件"提高排错效率"的事:**用例失败时自动截图**,以及**把结果变成一份好看好用的 Allure 报告**。看完之后,你应该能解释 `conftest.py` 里那段钩子代码,并会用 `allure serve`。

---

## 一、为什么要"失败自动截图"?

UI 自动化的痛点是:**测试跑的时候你不在旁边看**。上一秒还好好的,下一秒某个断言失败了,你只看到一句 `AssertionError`,却不知道**失败那一刻页面长什么样**——是弹了个广告挡住了?是页面上文案变了?还是根本没加载出来?

如果能自动存一张**失败瞬间的截图**,排错就快多了。本项目就做了这件事。

---

## 二、`pytest_runtest_makereport` 钩子

**钩子(hook)是什么?** 一句话:**在测试运行的某个"固定时机",pytest 会自动调用你写的某个函数。** 你只要把函数按规定的名字定义好,pytest 到点就会喊它。

`pytest_runtest_makereport` 就是这样一个钩子,它在 pytest **"生成某一步的测试报告"**的时候被调用。看 `conftest.py` 里的完整实现:

```python
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
```

逐行拆解:

- `SCREENSHOT_DIR = Path("screenshots")` —— 截图保存的文件夹,定为项目根目录下的 `screenshots/`。(`.gitignore` 里已忽略它,说明"截图是跑出来的产物,不进 git"。)
- `@pytest.hookimpl(hookwrapper=True, tryfirst=True)` —— 装饰器,告诉 pytest:"这是一个钩子包装器"
  - `hookwrapper=True`:表示这个函数是"包在钩子外面"的,可以用 `yield` 把控制权**先交出去**,等真正的报告生成完了再回来继续(这样我们才能读到报告结果)。
  - `tryfirst=True`:让它尽量**早点**执行。
- `def pytest_runtest_makereport(item, call):` —— 钩子函数。名字是 pytest **规定死的**,不能改。
  - `item`:代表"当前这个测试项"(里面带着测试函数的信息)。
  - `call`:代表"当前运行到哪个阶段"。
- `outcome = yield` —— 把控制权交给 pytest(它去真正生成报告),`outcome` 最终装着结果。
- `report = outcome.get_result()` —— 从结果里取出**报告对象** `report`。报告里记着"通过还是失败""在哪个阶段"等。
- `if report.when == "call" and report.failed:` —— **只在两条件都满足时截图**:
  - `report.when == "call"`:pytest 跑一个测试分三个阶段 `setup`(准备)、`call`(执行测试体)、`teardown`(清理)。我们**只关心 `call` 阶段**——也就是测试函数**本身**失败了。如果是 fixture 准备阶段就挂了(setup 失败),截图的时机和页面状态不一定有意义,所以不截。
  - `report.failed`:这一阶段**确实失败了**。通过的用例不截图。
- `page = item.funcargs.get("page")` —— 从当前测试用到的参数(`funcargs`)里,找有没有叫 `page` 的。用 `.get("page")` 而不是 `item.funcargs["page"]`,是怕万一这个测试没有 `page` 参数会报错;`.get` 找不到就返回 `None`。
- `if page is not None:` —— 只有真拿到了 `page` 才继续(截图得靠它)。
- `SCREENSHOT_DIR.mkdir(exist_ok=True)` —— 创建 `screenshots/` 文件夹。`exist_ok=True` 意思是"如果已经有了就别报错",避免重复运行时因为文件夹已存在而失败。
- `safe_name = re.sub(r"[^\w\-]", "_", item.nodeid)` —— 把测试的 ID(`item.nodeid`,形如 `tests/test_login.py::test_login_success`)里的"不适合当文件名的字符"替换成下划线 `_`,做成一个安全的文件名(`re.sub` 是正则替换)。
- `path = SCREENSHOT_DIR / f"{safe_name}_{datetime.now():%Y%m%d_%H%M%S}.png"` —— 拼出截图路径,文件名带上**时间戳**(精确到秒),这样同一个用例失败多次也不会互相覆盖。
- `page.screenshot(path=str(path))` —— **真正截图**,存到那个路径。
- 最后一段 `try ... except ImportError: pass`:
  - `import allure` + `allure.attach.file(...)`:把刚截的图**附到 Allure 报告**里,起名"失败截图",类型标为 PNG。
  - 万一没装 allure 库(比如别人只跑了 pytest),`import allure` 会抛 `ImportError`,`except` 就悄悄跳过——**截图照存,报告附加这一步优雅跳过**,不会因为没装 allure 就把整个测试搞崩。

**一句话总结这个钩子**:pytest 每次生成报告时都会喊它;它只在"测试体失败"且"有 page"时,截一张带时间戳的图存到 `screenshots/`,并(如果装了 allure)把图塞进报告。

---

## 三、Allure 报告:安装与查看

**Allure 是什么?** 一个专门看测试报告的工具,能把 pytest 的结果变成一份**网页版、可展开、带截图**的漂亮报告。

### 1. 生成结果:靠 pytest 自动完成

看 `pytest.ini`:

```ini
[pytest]
addopts = -v --alluredir=allure-results
testpaths = tests
```

`--alluredir=allure-results` 表示:**每跑一次 pytest,就把原始结果写进 `allure-results/` 文件夹**。所以你只要跑一次 `pytest`,结果文件就自动有了,不用额外命令。

```bash
pytest
```

跑完,项目里会出现 `allure-results/` 文件夹(里头的是一堆数据文件,不是给人直接看的)。

### 2. 查看报告:先装 Allure 命令行工具

**注意**:`allure` 这个"打开报告"的命令**不是 pip 装的**,它要单独装一个命令行程序:

- 需要先装 **Java**(Allure 依赖 Java 运行)。
- 然后下载 Allure 命令行工具并把它加进 PATH(Windows 上常见做法是用包管理器 `scoop install allure`,或手动下载解压后配置环境变量)。

装好后,命令行敲:

```bash
allure --version
```

能打出版本号,就说明装好了。

> **常见报错**:`allure: command not found` —— 说明 Allure 命令行没装或没进 PATH(注意:光 `pip install allure-pytest` **只会生成结果** `allure-results/`,不会给你 `allure` 这个命令)。`ERROR: JAVA_HOME is not set` 之类的,说明 Java 没装好。

### 3. 打开报告

最简单的方式——**直接生成并打开一个临时网页**:

```bash
allure serve allure-results
```

这条命令会:读取 `allure-results/` 里的原始数据 → 起一个本地小服务器 → **自动在浏览器里弹出报告页面**。看完关掉即可。

另一种是先落盘成静态报告,再用浏览器打开:

```bash
allure generate allure-results -o allure-report --clean
```

- `allure-results`:数据来源。
- `-o allure-report`:把生成的报告输出到 `allure-report/`。
- `--clean`:每次重新生成前先清空旧报告。

> 本项目 `.gitignore` 里已经忽略了 `allure-results/` 和 `allure-report/`,所以这些"跑出来的东西"都不会被提交到 git。

---

## 四、报告里怎么看失败截图

1. 运行 `pytest`(有意让某个用例失败,或等它真的失败之后)。
2. 运行 `allure serve allure-results` 打开报告。
3. 在报告首页会看到**用例总数、通过/失败数**等统计。
4. 点开左侧导航里**标红(失败)**的那个用例。
5. 在用例详情里,**失败截图作为附件(名字叫"失败截图")出现在下方**,点开就能看到失败那一刻的页面。

**这样你就能直接看到**:失败时页面停在哪个界面、有没有报错弹窗、元素是不是根本没出现……比起对着一句 `AssertionError` 干瞪眼,效率高得多。

---

## 五、小结

- **失败自动截图**:靠 `conftest.py` 里的 `pytest_runtest_makereport` 钩子;它只在"测试体(call 阶段)失败"时截图,存到 `screenshots/`,并附加到 Allure。
- **钩子** `hookwrapper=True` 让你能在 pytest 生成报告的前后"插一脚"。
- **Allure**:`pytest.ini` 里的 `--alluredir=allure-results` 负责产出结果;**`allure` 命令行要单独装**;用 `allure serve allure-results` 打开报告;失败用例的详情里能看到"失败截图"附件。

下一篇《07 项目复盘与面试话术》把整个项目用 STAR 讲一遍,并给出面试高频问答。
