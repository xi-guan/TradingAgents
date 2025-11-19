#!/usr/bin/env python3
"""从 config/local.yaml 生成 .env 文件

功能：
1. 读取 config/local.yaml
2. 将嵌套配置转换为环境变量格式
3. 生成 backend/.env 文件
"""

import sys
from pathlib import Path
from typing import Any

import yaml


# 环境变量名称映射
ENV_MAPPING = {
    'app.name': 'APP_NAME',
    'app.version': 'APP_VERSION',
    'app.debug': 'DEBUG',
    'app.secret_key': 'SECRET_KEY',
    'database.url': 'DATABASE_URL',
    'database.echo': 'DATABASE_ECHO',
    'redis.url': 'REDIS_URL',
    'redis.password': 'REDIS_PASSWORD',
    'qdrant.url': 'QDRANT_URL',
    'qdrant.api_key': 'QDRANT_API_KEY',
    'jwt.secret_key': 'JWT_SECRET_KEY',
    'jwt.algorithm': 'JWT_ALGORITHM',
    'jwt.access_token_expire_minutes': 'ACCESS_TOKEN_EXPIRE_MINUTES',
    'jwt.refresh_token_expire_days': 'REFRESH_TOKEN_EXPIRE_DAYS',
    'cors.origins': 'CORS_ORIGINS',
    'openai.api_key': 'OPENAI_API_KEY',
    'openai.base_url': 'OPENAI_BASE_URL',
    'alpha_vantage.api_key': 'ALPHA_VANTAGE_API_KEY',
    'tushare.token': 'TUSHARE_TOKEN',
    'celery.broker_url': 'CELERY_BROKER_URL',
    'celery.result_backend': 'CELERY_RESULT_BACKEND',
    'log.level': 'LOG_LEVEL',
    'log.file': 'LOG_FILE',
    'data.dir': 'DATA_DIR',
    'i18n.default_language': 'DEFAULT_LANGUAGE',
    'rate_limit.enabled': 'RATE_LIMIT_ENABLED',
    'rate_limit.per_minute': 'RATE_LIMIT_PER_MINUTE',
}


def get_nested_value(data: dict, path: str, default: Any = None) -> Any:
    """获取嵌套字典的值"""
    keys = path.split('.')
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def format_env_value(value: Any) -> str:
    """格式化环境变量值"""
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # 如果包含特殊字符，需要引号
        if any(c in value for c in [' ', '$', '"', "'"]):
            # 转义双引号
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'
        return value
    else:
        return str(value)


def generate_env(config_file: Path, output_file: Path) -> None:
    """生成 .env 文件"""

    # 读取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if not config:
        print(f"❌ 错误: 配置文件为空")
        sys.exit(1)

    # 生成环境变量
    env_lines = [
        "# TradingAgents Environment Variables",
        "# 自动生成 - 请勿手动编辑此文件",
        "# 编辑 config/local.yaml 后运行 ./scripts/setup.sh 重新生成",
        "",
    ]

    # 按分类组织
    sections = {
        '应用配置': ['app.name', 'app.version', 'app.debug', 'app.secret_key'],
        '数据库配置': ['database.url', 'database.echo'],
        'Redis 配置': ['redis.url', 'redis.password'],
        'Qdrant 配置': ['qdrant.url', 'qdrant.api_key'],
        'JWT 配置': ['jwt.secret_key', 'jwt.algorithm', 'jwt.access_token_expire_minutes', 'jwt.refresh_token_expire_days'],
        'CORS 配置': ['cors.origins'],
        'OpenAI API': ['openai.api_key', 'openai.base_url'],
        'Alpha Vantage API': ['alpha_vantage.api_key'],
        'Tushare API': ['tushare.token'],
        'Celery 配置': ['celery.broker_url', 'celery.result_backend'],
        '日志配置': ['log.level', 'log.file'],
        '数据目录': ['data.dir'],
        '语言配置': ['i18n.default_language'],
        '速率限制': ['rate_limit.enabled', 'rate_limit.per_minute'],
    }

    for section_name, keys in sections.items():
        env_lines.append(f"# {section_name}")
        for key in keys:
            value = get_nested_value(config, key)
            if value is not None:
                env_name = ENV_MAPPING.get(key, key.upper().replace('.', '_'))
                env_value = format_env_value(value)
                env_lines.append(f"{env_name}={env_value}")
        env_lines.append("")

    # 写入文件
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_lines))

    print(f"✓ .env 文件已生成: {output_file}")


def main():
    """主函数"""
    # 确定项目根目录
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    config_file = project_root / 'config' / 'local.yaml'
    output_file = project_root / 'backend' / '.env'

    if not config_file.exists():
        print(f"❌ 错误: 找不到配置文件: {config_file}")
        print(f"请先运行: python scripts/lib/generate_from_schema.py")
        sys.exit(1)

    print(f"📖 读取配置文件: {config_file}")
    generate_env(config_file, output_file)


if __name__ == '__main__':
    main()
