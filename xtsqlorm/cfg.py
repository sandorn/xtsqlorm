# !/usr/bin/env python
"""
==============================================================
Description  : 数据库配置模块 - 提供统一的数据库连接配置管理功能
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-23 15:00:00
Github       : https://github.com/sandorn/xtsqlorm

本模块提供以下核心功能:
- DB_CFG: 数据库连接配置枚举类,集中管理所有数据库连接信息
- Driver_Map: 数据库驱动映射枚举类,管理不同数据库类型的驱动配置
- connect_str: 生成数据库连接字符串的工具函数

主要特性:
- 集中式配置管理,便于统一维护和修改数据库连接信息
- 支持多种数据库类型(MySQL、PostgreSQL、Oracle等)
- 支持多种数据库驱动选择
- 统一的连接字符串生成机制
- 完整的类型注解,支持Python 3.10+现代语法规范
==============================================================
"""

from __future__ import annotations

from enum import Enum


class DB_CFG(Enum):  # noqa
    """数据库配置枚举类,集中管理所有数据库连接配置"""

    TXbook = (
        {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'user': 'sandorn',
            'password': '123456',
            'db': 'biqukan',
            'charset': 'utf8mb4',
        },
    )
    TXbx = (
        {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'user': 'sandorn',
            'password': '123456',
            'db': 'bxflb',
            'charset': 'utf8mb4',
        },
    )
    redis = ({'type': 'redis', 'host': 'localhost', 'port': 6379, 'db': 4},)
    Jkdoc = (
        {
            'type': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'user': 'sandorn',
            'password': '123456',
            'db': 'Jkdoc',
            'charset': 'utf8mb4',
        },
    )

    default = TXbx


class Driver_Map(Enum):  # noqa
    """数据库驱动映射枚举类,管理不同数据库类型的驱动配置"""

    mysql = (
        {
            'async': 'mysql+aiomysql',
            'OurSQL': 'mysql+oursql',
            'pymysql': 'mysql+pymysql',
            'mysql': 'mysql+pymysql',
            'mysqlconnector': 'mysql+mysqlconnector',
        },
    )
    PostgreSQL = (
        {
            'pg8000': 'postgresql+pg8000',
            'psycopg2': 'postgresql+psycopg2',
            'postgresql': 'postgresql+psycopg2',
            'async': 'postgresql+asyncpg',
        },
    )
    Oracle = ({'oracle': 'oracle', 'cx': 'oracle+cx_oracle'},)
    SQLServer = (
        {
            'pyodbc': 'mssql+pyodbc',
            'pymssql': 'mssql+pymssql',
            'sqlserver': 'mssql+pymssql',
        },
    )
    SQLite = ({'sqlite': 'sqlite', 'async': 'sqlite+aiosqlite'},)
    access = ({'access': 'access+pyodbc'},)
    monetdb = ({'monetdb': 'monetdb', 'lite': 'monetdb+lite'},)


def connect_str(key: str = 'default', odbc: str | None = None) -> str:
    """生成数据库连接字符串的工具函数

    Args:
        key: 数据库配置键名,对应DB_CFG中的配置项
        odbc: 可选,指定数据库驱动类型,默认使用配置中的数据库类型

    Returns:
        str: 格式化的数据库连接字符串

    Raises:
        ValueError: 当配置键不存在时抛出
        KeyError: 当配置中缺少必要字段时抛出

    Example:
        >>> # 1. 使用默认驱动
        >>> conn_str = connect_str('TXbook')
        >>> # 返回: mysql://sandorn:123456@localhost:3306/biqukan?charset=utf8mb4
        >>> # 2. 指定驱动
        >>> conn_str = connect_str('TXbook', 'connector')
        >>> # 返回: mysql+mysqlconnector://sandorn:123456@localhost:3306/biqukan?charset=utf8mb4
        >>> # 3. 使用默认配置
        >>> conn_str = connect_str('default')
        >>> # 返回: mysql://sandorn:123456@localhost:3306/bxflb?charset=utf8mb4
    """
    if not hasattr(DB_CFG, key):
        raise ValueError(f'错误提示:检查数据库配置:{key}')

    # 从枚举中获取配置字典(枚举值是包含字典的元组,需要取第一个元素)
    cfg = DB_CFG[key].value[0]
    db_types = cfg['type']
    odbc = db_types if odbc is None else odbc

    # 构建连接字符串基础部分
    try:
        link_str = f'{cfg["user"]}:{cfg["password"]}@{cfg["host"]}:{cfg["port"]}/{cfg["db"]}?charset={cfg["charset"]}'
    except KeyError as e:
        raise KeyError(f'配置中缺少必要字段: {e}') from e

    # 获取驱动字符串(枚举值是包含字典的元组,需要取第一个元素)
    try:
        tmp_map = Driver_Map[db_types].value[0]
        drivers_str = tmp_map.get(odbc, tmp_map.get(db_types))
    except KeyError as e:
        raise KeyError(f'不支持的数据库类型: {db_types}') from e

    return f'{drivers_str}://{link_str}'


if __name__ == '__main__':
    """示例代码,展示connect_str函数的使用方式"""
    # 使用默认驱动
    print(connect_str())

    # 指定特定驱动
    connector2 = connect_str('TXbook', 'pymysql')
    print(connector2)

    # 使用默认配置
    print(connect_str('default', odbc='async'))
