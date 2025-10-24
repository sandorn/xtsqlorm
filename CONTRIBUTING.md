# 贡献指南

感谢您考虑为 xtsqlorm 做出贡献！

## 🤝 如何贡献

### 报告 Bug

如果您发现了 Bug，请通过以下方式报告：

1. 在 [Issues](https://gitee.com/sandorn/xtsqlorm/issues) 页面创建新 Issue
2. 使用清晰的标题描述问题
3. 提供详细的复现步骤
4. 说明预期行为和实际行为
5. 附上相关的错误信息和日志
6. 注明您的环境信息（Python 版本、操作系统等）

**Bug 报告模板**:

````markdown
## 问题描述

简要描述遇到的问题

## 复现步骤

1. 第一步
2. 第二步
3. ...

## 预期行为

描述您期望发生的行为

## 实际行为

描述实际发生的行为

## 环境信息

-   Python 版本: 3.10
-   xtsqlorm 版本: 0.1.0
-   操作系统: Windows 10
-   数据库: MySQL 8.0

## 错误信息

```python
Traceback...
```
````

````

---

### 提出新功能

如果您有新功能的想法，请：

1. 先在 Issues 中讨论您的想法
2. 说明功能的用途和价值
3. 描述实现方案（如有）
4. 等待维护者反馈

**功能请求模板**:

```markdown
## 功能描述
简要描述您想要的新功能

## 使用场景
描述这个功能解决什么问题

## 实现建议
（可选）您对实现方式的建议

## 替代方案
（可选）其他可能的解决方案
````

---

### 提交代码

#### 1. 准备开发环境

```bash
# Fork 并克隆仓库
git clone https://gitee.com/your-username/xtsqlorm.git
cd xtsqlorm

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 或使用 uv (推荐)
uv sync
```

#### 2. 创建分支

```bash
# 创建新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

分支命名规范：

-   `feature/*` - 新功能
-   `fix/*` - Bug 修复
-   `docs/*` - 文档更新
-   `refactor/*` - 代码重构
-   `test/*` - 测试相关
-   `chore/*` - 构建/工具相关

#### 3. 编写代码

请遵循以下规范：

**代码风格**:

-   使用 Ruff 进行代码检查和格式化
-   遵循 PEP 8 规范
-   使用半角标点符号
-   添加必要的类型注解

**文档字符串**:

-   所有公共函数/类必须有 docstring
-   使用 Google 风格的 docstring
-   包含参数说明、返回值、异常信息
-   添加使用示例

**示例**:

```python
def create_user(
    username: str,
    email: str,
    *,
    phone: str | None = None
) -> User:
    """创建新用户

    此函数创建一个新用户并保存到数据库。如果用户名已存在,
    将抛出 ValueError 异常。

    Args:
        username: 用户名, 必须唯一
        email: 电子邮箱地址
        phone: 电话号码, 可选

    Returns:
        User: 创建的用户对象

    Raises:
        ValueError: 用户名已存在时抛出
        ValidationError: 数据验证失败时抛出

    Example:
        >>> user = create_user('john', 'john@example.com')
        >>> print(user.username)
        'john'
    """
    # 实现代码
    ...
```

**测试**:

-   为新功能添加测试
-   确保所有测试通过
-   测试覆盖率应 ≥ 80%

#### 4. 运行检查

提交前请运行以下检查：

```bash
# 代码风格检查
ruff check xtsqlorm/ examples/

# 代码格式化
ruff format xtsqlorm/ examples/

# 类型检查
basedpyright xtsqlorm/

# 运行测试（如有）
pytest

# 运行示例代码
uv run python examples/example_01_basic_sync.py
```

#### 5. 提交更改

```bash
# 添加更改
git add .

# 提交 (使用清晰的提交信息)
git commit -m "feat: add user authentication feature"

# 推送到您的 Fork
git push origin feature/your-feature-name
```

**提交信息规范**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**:

-   `feat`: 新功能
-   `fix`: Bug 修复
-   `docs`: 文档更新
-   `style`: 代码格式修改
-   `refactor`: 代码重构
-   `test`: 测试相关
-   `chore`: 构建/工具相关
-   `perf`: 性能优化

**示例**:

```
feat(repository): add batch update method

- 实现批量更新功能
- 优化性能,使用 bulk_update_mappings
- 添加相关测试

Closes #123
```

#### 6. 创建 Pull Request

1. 访问您的 Fork 页面
2. 点击 "Pull Request" 按钮
3. 选择目标分支（通常是 `main`）
4. 填写 PR 描述：
    - 说明更改的内容和原因
    - 引用相关 Issue
    - 列出测试情况
    - 添加截图（如适用）

**PR 模板**:

```markdown
## 更改说明

描述此 PR 的主要更改

## 相关 Issue

Closes #123

## 更改类型

-   [ ] Bug 修复
-   [ ] 新功能
-   [ ] 文档更新
-   [ ] 代码重构
-   [ ] 性能优化

## 测试

-   [ ] 已添加测试
-   [ ] 所有测试通过
-   [ ] 已运行示例代码

## 检查清单

-   [ ] 代码符合项目规范
-   [ ] 已更新文档
-   [ ] 已运行 Ruff 检查
-   [ ] 已运行类型检查
-   [ ] 提交信息清晰明确
```

---

## 📝 代码规范

### Python 代码风格

-   **缩进**: 4 个空格
-   **行长度**: 最大 120 字符
-   **引号**: 单引号优先
-   **导入顺序**: 标准库 → 第三方库 → 本地模块

### 命名规范

-   **模块/包**: `lowercase_with_underscores`
-   **类**: `CamelCase`
-   **函数/变量**: `lowercase_with_underscores`
-   **常量**: `UPPERCASE_WITH_UNDERSCORES`
-   **私有属性**: `_leading_underscore`

### 类型注解

所有公共 API 必须有类型注解：

```python
from typing import Optional, List, Dict, Any

def get_users(
    limit: int = 10,
    offset: int = 0,
    *,
    active_only: bool = True
) -> List[User]:
    ...
```

### 异常处理

```python
# 使用具体的异常类型
try:
    result = risky_operation()
except ValueError as e:
    log.error(f'Invalid value: {e}')
    raise
except DatabaseError as e:
    log.error(f'Database error: {e}')
    return None

# 避免裸 except
# ❌ 不好
try:
    ...
except:
    pass

# ✅ 好
try:
    ...
except Exception as e:
    log.error(f'Unexpected error: {e}')
    raise
```

---

## 🧪 测试指南

### 编写测试

```python
import pytest
from xtsqlorm import create_repository
from tests.models import User

class TestUserRepository:
    """用户仓储测试"""

    @pytest.fixture
    def user_repo(self):
        """创建用户仓储"""
        return create_repository(User, db_key='test')

    def test_create_user(self, user_repo):
        """测试创建用户"""
        user = user_repo.create({
            'username': 'test_user',
            'email': 'test@example.com'
        })

        assert user.id is not None
        assert user.username == 'test_user'

    def test_get_by_id(self, user_repo):
        """测试根据 ID 获取用户"""
        user = user_repo.create({
            'username': 'test_user',
            'email': 'test@example.com'
        })

        found = user_repo.get_by_id(user.id)
        assert found is not None
        assert found.id == user.id
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_repository.py

# 运行特定测试类
pytest tests/test_repository.py::TestUserRepository

# 运行特定测试方法
pytest tests/test_repository.py::TestUserRepository::test_create_user

# 显示详细输出
pytest -v

# 显示覆盖率
pytest --cov=xtsqlorm --cov-report=html
```

---

## 📚 文档贡献

### 文档类型

1. **API 文档**: 通过 docstring 自动生成
2. **用户指南**: `docs/` 目录下的 Markdown 文件
3. **示例代码**: `examples/` 目录
4. **README**: 项目主页文档

### 文档规范

-   使用清晰简洁的语言
-   提供实际可运行的示例
-   保持文档与代码同步
-   使用正确的 Markdown 格式
-   添加必要的链接和引用

---

## 🔍 代码审查

Pull Request 将经过以下审查：

1. **功能审查**: 确保功能正确实现
2. **代码质量**: 检查代码风格和规范
3. **测试覆盖**: 验证测试完整性
4. **文档完整**: 检查文档是否完善
5. **性能影响**: 评估性能影响
6. **安全性**: 检查潜在安全问题

---

## 🎯 贡献建议

### 适合新手的任务

-   修复文档中的拼写错误
-   改进错误信息
-   添加代码示例
-   完善单元测试
-   翻译文档

查找 [good first issue](https://gitee.com/sandorn/xtsqlorm/issues?labels=good%20first%20issue) 标签。

### 高级任务

-   实现新功能
-   性能优化
-   架构改进
-   复杂 Bug 修复

---

## 📞 获取帮助

如果您在贡献过程中遇到问题：

1. 查看现有的 [Issues](https://gitee.com/sandorn/xtsqlorm/issues)
2. 阅读 [文档](docs/)
3. 在 Issue 中提问
4. 联系维护者: sandorn@live.cn

---

## 📜 行为准则

### 我们的承诺

为了营造开放和友好的环境,我们承诺:

-   尊重不同的观点和经验
-   接受建设性的批评
-   关注对社区最有利的事情
-   对其他社区成员表示同理心

### 不可接受的行为

-   使用性别化的语言或图像
-   发表侮辱/贬损性评论
-   人身攻击
-   骚扰行为
-   发布他人的私人信息

### 执行

违反行为准则的行为可能导致:

1. 警告
2. 临时禁止参与
3. 永久禁止参与

---

## 🎉 认可贡献者

我们会在以下位置认可贡献者:

-   README.md 致谢部分
-   CHANGELOG.md 版本说明
-   项目文档中

---

感谢您为 xtsqlorm 做出贡献！🎉

**维护者**: sandorn <sandorn@live.cn>  
**最后更新**: 2025-10-25
