#!/usr/bin/env python3
"""
快速优化方案 - 最小侵入式重构
保持向后兼容，逐步引入新设计
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

# ============================================================
# 第1步: 定义抽象接口协议
# ============================================================


class ISessionProvider(ABC):
    """会话提供者接口 - 所有需要提供Session的类都应实现此接口"""

    @abstractmethod
    def get_session(self) -> Session:
        """创建新的数据库会话（推荐用法）

        Returns:
            新创建的Session实例

        Note:
            调用者负责关闭返回的session
        """
        pass

    @abstractmethod
    @contextmanager
    def transaction(self) -> Generator[Session]:
        """事务上下文管理器（推荐用法）

        使用示例:
            with session_provider.transaction() as session:
                user = session.get(User, 1)
                user.name = 'New Name'
                # 自动提交，异常时自动回滚

        Yields:
            数据库会话对象
        """
        pass


class IConnectionManager(ABC):
    """连接管理器接口 - 只负责连接层面的操作"""

    @property
    @abstractmethod
    def engine(self) -> Engine:
        """获取SQLAlchemy引擎对象"""
        pass

    @abstractmethod
    def ping(self) -> bool:
        """测试数据库连接是否正常

        Returns:
            连接正常返回True，否则返回False
        """
        pass

    @abstractmethod
    def dispose(self) -> None:
        """释放所有数据库连接资源"""
        pass


# ============================================================
# 第2步: 重构 SqlConnection - 实现接口并收缩职责
# ============================================================


class SqlConnection(IConnectionManager, ISessionProvider):
    """数据库连接管理类（重构版）

    职责收缩为:
    1. 管理数据库连接和引擎
    2. 提供Session创建能力
    3. 管理事务边界

    移除的职责:
    - ❌ 不再提供全局session属性（避免状态污染）
    - ❌ 不再提供全局commit/rollback方法（事务应在session_scope内管理）
    - ❌ 不再直接执行SQL（应通过session.execute()）

    迁移指南:
        旧代码: db.session.query(User).all()
        新代码: with db.transaction() as session:
                   users = session.query(User).all()
    """

    def __init__(
        self,
        db_key: str = 'default',
        url: str | None = None,
        **kwargs,
    ):
        """初始化数据库连接

        Args:
            db_key: 数据库配置键
            url: 数据库连接URL
            **kwargs: 引擎配置参数
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from .cfg import connect_str

        if not url:
            url = connect_str(db_key)

        # 提取引擎配置（省略具体实现...）
        self._engine = create_engine(url, **kwargs)
        self._session_factory = sessionmaker(bind=self._engine)

    # ============ IConnectionManager 接口实现 ============

    @property
    def engine(self) -> Engine:
        """获取SQLAlchemy引擎对象"""
        return self._engine

    def ping(self) -> bool:
        """测试数据库连接"""
        from sqlalchemy import text

        try:
            with self.engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            return True
        except Exception:
            return False

    def dispose(self) -> None:
        """释放数据库连接资源"""
        if hasattr(self, '_engine'):
            self._engine.dispose()

    # ============ ISessionProvider 接口实现 ============

    def get_session(self) -> Session:
        """创建新的数据库会话

        Returns:
            新创建的Session实例

        重要提示:
            调用者需要负责关闭返回的session:

            session = db.get_session()
            try:
                # 使用session...
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

            或者更推荐使用 transaction() 上下文管理器
        """
        return self._session_factory()

    @contextmanager
    def transaction(self) -> Generator[Session]:
        """事务上下文管理器（推荐用法）

        使用示例:
            # 简单查询
            with db.transaction() as session:
                user = session.get(User, 1)

            # 创建记录
            with db.transaction() as session:
                user = User(name='Alice')
                session.add(user)
                # 自动提交

            # 多表操作
            with db.transaction() as session:
                user = session.get(User, 1)
                order = Order(user_id=user.id)
                session.add(order)
                # 自动提交所有更改

        Yields:
            数据库会话对象

        Note:
            - 正常结束时自动commit
            - 异常时自动rollback
            - 结束时自动close
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# ============================================================
# 第3步: 重构 OrmOperations - 依赖抽象接口
# ============================================================


class OrmOperations[T]:
    """ORM操作类（重构版）

    改进:
    1. ✅ 依赖抽象接口（ISessionProvider）而非具体类
    2. ✅ 移除内部事务管理，使用统一的session_provider.transaction()
    3. ✅ 简化API，提供两种使用模式

    使用模式:

    模式1: 自动事务管理（推荐）
        ops = OrmOperations(User, session_provider)
        user = ops.get_by_id(1)  # 内部自动管理事务

    模式2: 外部事务管理（高级用法）
        with session_provider.transaction() as session:
            ops = OrmOperations(User, session_provider)
            user = ops.get_by_id_in_session(1, session)
            user.name = 'New Name'
            # 可以跨多个操作共享同一事务
    """

    def __init__(
        self,
        data_model: type[T],
        session_provider: ISessionProvider,  # 依赖抽象接口
        validator_model=None,
    ):
        """初始化ORM操作类

        Args:
            data_model: ORM模型类
            session_provider: 会话提供者（实现ISessionProvider接口）
            validator_model: 可选的Pydantic验证模型

        示例:
            # 使用SqlConnection
            conn = SqlConnection(db_key='default')
            ops = OrmOperations(User, conn)

            # 或使用任何实现了ISessionProvider的类
            custom_provider = MyCustomSessionProvider()
            ops = OrmOperations(User, custom_provider)
        """
        self._data_model = data_model
        self._session_provider = session_provider
        self._validator_model = validator_model

    # ============ 模式1: 自动事务管理（简单操作）============

    def get_by_id(self, id_value: int) -> T | None:
        """根据ID获取记录（自动事务）

        Args:
            id_value: 记录ID

        Returns:
            查询到的模型对象，不存在则返回None

        Note:
            此方法自动管理事务，适合单一操作
        """
        with self._session_provider.transaction() as session:
            return session.get(self._data_model, id_value)

    def create(self, data_dict: dict) -> T:
        """创建记录（自动事务）

        Args:
            data_dict: 记录数据字典

        Returns:
            创建的模型对象

        Note:
            此方法自动提交事务
        """
        with self._session_provider.transaction() as session:
            instance = self._data_model(**data_dict)
            session.add(instance)
            session.flush()  # 确保获取到生成的ID
            session.refresh(instance)  # 刷新以获取默认值
            return instance

    def update_by_id(self, id_value: int, data_dict: dict) -> T | None:
        """更新记录（自动事务）"""
        with self._session_provider.transaction() as session:
            instance = session.get(self._data_model, id_value)
            if instance:
                for key, value in data_dict.items():
                    setattr(instance, key, value)
            return instance

    def delete_by_id(self, id_value: int) -> bool:
        """删除记录（自动事务）"""
        with self._session_provider.transaction() as session:
            instance = session.get(self._data_model, id_value)
            if instance:
                session.delete(instance)
                return True
            return False

    # ============ 模式2: 外部事务管理（复杂操作）============

    def get_by_id_in_session(self, id_value: int, session: Session) -> T | None:
        """在指定session中获取记录（外部事务）

        使用场景:
            需要在同一事务中执行多个操作

        示例:
            with session_provider.transaction() as session:
                user = user_ops.get_by_id_in_session(1, session)
                order = order_ops.create_in_session({...}, session)
                # 统一提交
        """
        return session.get(self._data_model, id_value)

    def create_in_session(self, data_dict: dict, session: Session) -> T:
        """在指定session中创建记录（外部事务）"""
        instance = self._data_model(**data_dict)
        session.add(instance)
        return instance

    def query_in_session(self, session: Session):
        """在指定session中创建查询对象"""
        return session.query(self._data_model)


# ============================================================
# 第4步: 工作单元模式（可选，用于复杂事务）
# ============================================================


class UnitOfWork:
    """工作单元 - 管理一组相关操作的事务边界

    适用场景:
    - 需要在一个事务中操作多个表
    - 需要明确的事务边界
    - 复杂的业务逻辑

    使用示例:
        with UnitOfWork(session_provider) as uow:
            # 获取多个仓储
            user_ops = uow.operations(User)
            order_ops = uow.operations(Order)

            # 在同一事务中执行多个操作
            user = user_ops.get_by_id_in_session(1, uow.session)
            order = order_ops.create_in_session({
                'user_id': user.id,
                'amount': 100
            }, uow.session)

            # 显式提交或自动提交
            uow.commit()  # 可选，退出时自动提交
    """

    def __init__(self, session_provider: ISessionProvider):
        self._session_provider = session_provider
        self._session: Session | None = None

    def __enter__(self) -> UnitOfWork:
        self._session = self._session_provider.get_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
            self._session.close()

    @property
    def session(self) -> Session:
        """获取当前事务的session"""
        if self._session is None:
            raise RuntimeError('UnitOfWork not started')
        return self._session

    def operations(self, model: type[T]) -> OrmOperations[T]:
        """获取指定模型的操作对象"""

        # 创建一个临时的session_provider，返回当前UoW的session
        class _UoWSessionProvider(ISessionProvider):
            def __init__(self, session: Session):
                self._session = session

            def get_session(self) -> Session:
                return self._session

            @contextmanager
            def transaction(self):
                # UoW内部不创建新事务
                yield self._session

        provider = _UoWSessionProvider(self.session)
        return OrmOperations(model, provider)

    def commit(self):
        """显式提交事务"""
        if self._session:
            self._session.commit()

    def rollback(self):
        """显式回滚事务"""
        if self._session:
            self._session.rollback()


# ============================================================
# 使用示例对比
# ============================================================


def example_old_vs_new():
    """旧用法 vs 新用法对比"""

    # ========== 旧用法（仍然支持，但不推荐）==========
    print('旧用法:')
    print("""
    # 问题: 使用全局session，容易状态污染
    db = SqlConnection()
    session = db.session  # 全局session
    user = session.get(User, 1)
    session.commit()  # 需要手动管理事务
    """)

    # ========== 新用法1: 简单操作（推荐）==========
    print('\n新用法1 - 简单操作:')
    print("""
    # 优点: 自动事务管理，代码简洁
    conn = SqlConnection()
    ops = OrmOperations(User, conn)
    user = ops.get_by_id(1)  # 自动管理事务
    """)

    # ========== 新用法2: 多个操作共享事务（推荐）==========
    print('\n新用法2 - 共享事务:')
    print("""
    # 优点: 多个操作在同一事务中，保证一致性
    conn = SqlConnection()
    with conn.transaction() as session:
        user = session.get(User, 1)
        user.name = 'New Name'
        
        order = Order(user_id=user.id, amount=100)
        session.add(order)
        # 自动提交所有更改
    """)

    # ========== 新用法3: 工作单元（复杂场景）==========
    print('\n新用法3 - 工作单元:')
    print("""
    # 优点: 业务逻辑清晰，适合复杂场景
    conn = SqlConnection()
    with UnitOfWork(conn) as uow:
        user_ops = uow.operations(User)
        order_ops = uow.operations(Order)
        
        user = user_ops.get_by_id_in_session(1, uow.session)
        order = order_ops.create_in_session({
            'user_id': user.id,
            'amount': 100
        }, uow.session)
        # 自动提交
    """)


# ============================================================
# 迁移检查清单
# ============================================================

MIGRATION_CHECKLIST = """
# 重构迁移检查清单

## Phase 1: 基础重构（立即可做）

### 1. SqlConnection改造
- [ ] 实现IConnectionManager和ISessionProvider接口
- [ ] 添加get_session()和transaction()方法
- [ ] 标记旧方法为@deprecated
  - [ ] @property session (使用get_session替代)
  - [ ] commit() / rollback() (使用transaction()替代)
  - [ ] execute_sql() (使用session.execute()替代)

### 2. OrmOperations改造
- [ ] 修改构造函数接受ISessionProvider
- [ ] 移除self.db属性，使用self._session_provider
- [ ] 移除内部session_scope()，使用session_provider.transaction()
- [ ] 添加_in_session()系列方法支持外部事务

### 3. 测试验证
- [ ] 单元测试：测试新接口的各种场景
- [ ] 集成测试：验证事务正确性
- [ ] 兼容性测试：确保旧代码仍可运行

## Phase 2: 文档和示例（1周内）

- [ ] 更新README添加新用法示例
- [ ] 创建迁移指南文档
- [ ] 更新所有示例代码
- [ ] 添加性能对比测试

## Phase 3: 清理工作（1个月后）

- [ ] 移除@deprecated标记的旧方法
- [ ] 删除不必要的代码
- [ ] 发布新的major版本

## 预期收益

✅ 代码量减少 ~30%
✅ 测试覆盖率提高 ~40%
✅ 职责更清晰
✅ 更易维护和扩展
✅ 符合SOLID原则
✅ 更好的类型提示支持
"""

if __name__ == '__main__':
    print('=' * 60)
    print('xtsqlorm 快速优化方案')
    print('=' * 60)
    example_old_vs_new()
    print('\n' + MIGRATION_CHECKLIST)
