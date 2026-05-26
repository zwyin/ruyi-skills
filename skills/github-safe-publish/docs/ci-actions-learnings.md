# CI & GitHub Actions 实战经验

来源：claude-session-watchdog 项目 CI 配置实践，2026-05-25

---

## 1. Workflow 模板

### 基础模板（适用于大多数项目）

```yaml
name: Test

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]
  workflow_dispatch:

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.12"]

    env:
      PYTHONUTF8: "1"

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -e ".[dev]"  # 或 pip install pytest
      - name: Run tests
        run: pytest tests/ -q
```

### bash/tmux 项目模板（无 Windows）

```yaml
name: Test

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]
  workflow_dispatch:

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.12"]

    env:
      PYTHONUTF8: "1"

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install system deps (macOS)
        if: runner.os == 'macOS'
        run: brew install tmux
      - name: Start tmux session
        run: tmux new-session -d -s test-session
      - name: Install pytest
        run: pip install pytest
      - name: Run tests
        run: pytest tests/ -q
```

---

## 2. 平台选择决策树

```
项目是否有 bash/tmux/系统工具依赖？
├─ 是 → 只用 Ubuntu + macOS
│        （macOS 需 brew install 系统依赖）
└─ 否 → 项目有 GUI/跨平台需求？
         ├─ 是 → Ubuntu + macOS + Windows
         └─ 否 → 看测试代码是否处理了路径/编码问题
                  ├─ 是 → 三平台
                  └─ 否 → 先只上 Ubuntu + macOS，Windows 后续加
```

---

## 3. 踩过的坑（按严重程度排序）

### P0: Windows 路径转义导致测试全面崩溃

**现象**：Windows 上所有使用 `subprocess(["python3", "-c", f"...'{PATH}'..."])` 的测试失败。

**根因**：Windows 路径使用反斜杠（`D:\a\project\scripts\file.json`），嵌入 Python `-c` 字符串时反斜杠被解释为转义字符：
- `\a` → bell 字符 (0x07)
- `\n` → 换行符
- `\c` → SyntaxWarning

**解决方案**：
```python
# 方案 1：路径中反斜杠替换为正斜杠（Python 接受两种）
path = path.replace('\\', '/')

# 方案 2：使用 repr() 避免转义
f"... {repr(path)} ..."

# 方案 3：全局 UTF-8 模式（只解决编码，不解决路径转义）
# 在 workflow 中设 PYTHONUTF8: "1"
```

### P1: Windows 编码问题（cp1252 vs UTF-8）

**现象**：`UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d`

**根因**：Windows Python 默认编码是 cp1252，不是 UTF-8。`open('file.json', 'r')` 在 Windows 上用 cp1252 解码含中文的 UTF-8 文件。

**解决方案**：
```yaml
# workflow 级别（推荐，一劳永逸）
env:
  PYTHONUTF8: "1"

# 或代码级别
with open('file.json', 'r', encoding='utf-8') as f:
```

### P1: macOS CI 没有 tmux

**现象**：`Process completed with exit code 127`（command not found）

**根因**：macOS-latest runner 不预装 tmux。Ubuntu-latest 预装。

**解决方案**：
```yaml
- name: Install system deps (macOS)
  if: runner.os == 'macOS'
  run: brew install tmux
```

### P2: PR 分支与目标无共同祖先

**现象**：`gh pr create` 报 `GraphQL: The branch has no history in common with master`

**根因**：PR 分支从一个与目标分支没有共同祖先的分支创建（如从 public 分支创建 PR 到 master，但 public 是独立历史）。

**解决方案**：
```bash
# 创建 PR 分支前检查
git merge-base HEAD target-branch
# 无输出 = 无共同祖先，需从目标分支重新创建

git checkout -b ci/fix-xxx target-branch  # 从目标分支创建
```

---

## 4. actions 版本注意

Node.js 20 actions 将在 2026-06-02 起被强制使用 Node.js 24。当前 `actions/checkout@v4` 和 `actions/setup-python@v5` 会触发 deprecation 警告。关注后续 v5/v6 版本发布。

---

## 5. 建议纳入 skill 的 Step

在 `publish-github` skill 的 Step 7（验证）之后，新增：

### Step 8: CI 工作流生成（可选）

推送成功后，检查项目是否有 `.github/workflows/test.yml`。如果没有，询问用户是否需要自动生成 CI 工作流。

生成逻辑：
1. 检测项目类型（Python 包 / bash 脚本 / Node.js / 混合）
2. 检测测试框架（pytest / unittest / jest / 无测试）
3. 检测系统依赖（grep 代码中的 tmux/bash/selenium 等）
4. 根据检测结果选择平台矩阵和安装步骤
5. 生成 workflow 文件，提交并推送

### Step 9: Branch Protection 建议（可选）

推送成功后，建议用户开启 master 分支保护：
```bash
gh api repos/OWNER/REPO/branches/master/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["test"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}'
```
