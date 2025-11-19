#!/usr/bin/env python3
"""从 config.schema.yaml 生成 config/local.yaml

功能：
1. 读取 config.schema.yaml 中的字段定义
2. 为标记为 secret 的字段自动生成密钥
3. 深度合并现有的 local.yaml（保留所有现有值）
4. 生成/更新 config/local.yaml
"""

import os
import secrets
import string
import sys
from pathlib import Path
from typing import Any

import yaml


def generate_secret(length: int = 32) -> str:
    """生成安全的随机密钥"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def deep_merge(base: dict, updates: dict) -> dict:
    """深度合并字典（保留 base 中的现有值）"""
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        elif key not in result:
            result[key] = value
    return result


def set_nested_value(data: dict, path: str, value: Any) -> None:
    """设置嵌套字典的值（例如 'api.port' -> data['api']['port'] = value）"""
    keys = path.split('.')
    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def get_nested_value(data: dict, path: str, default: Any = None) -> Any:
    """获取嵌套字典的值"""
    keys = path.split('.')
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def generate_config(schema_file: Path, output_file: Path) -> None:
    """从 schema 生成配置文件"""

    # 读取 schema
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = yaml.safe_load(f)

    # 读取现有配置（如果存在）
    existing_config = {}
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_config = yaml.safe_load(f) or {}
        print(f"✓ 找到现有配置文件，将保留所有现有值")

    # 生成新配置
    new_config = {}
    generated_secrets = []

    for field in schema:
        section = field['section']

        # 检查是否已存在值
        existing_value = get_nested_value(existing_config, section)

        if existing_value is not None:
            # 保留现有值
            set_nested_value(new_config, section, existing_value)
            continue

        # 生成新值
        if field.get('type') == 'secret' and field.get('auto_generate'):
            # 自动生成密钥
            secret_value = generate_secret()
            set_nested_value(new_config, section, secret_value)
            generated_secrets.append(section)
        else:
            # 使用默认值
            default = field.get('default', '')
            set_nested_value(new_config, section, default)

    # 合并配置（确保不丢失任何现有值）
    final_config = deep_merge(existing_config, new_config)

    # 写入配置文件
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(
            final_config,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    print(f"✓ 配置文件已生成: {output_file}")

    if generated_secrets:
        print(f"\n🔐 自动生成了 {len(generated_secrets)} 个密钥:")
        for secret in generated_secrets:
            print(f"  - {secret}")

    print("\n📝 配置说明:")
    print(f"  1. 查看生成的配置: cat {output_file}")
    print(f"  2. 修改需要的值（如 API keys）")
    print(f"  3. 运行 ./scripts/setup.sh 生成 .env 文件")


def main():
    """主函数"""
    # 确定项目根目录
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    schema_file = project_root / 'config' / 'config.schema.yaml'
    output_file = project_root / 'config' / 'local.yaml'

    if not schema_file.exists():
        print(f"❌ 错误: 找不到 schema 文件: {schema_file}")
        sys.exit(1)

    print(f"📖 读取配置 schema: {schema_file}")
    generate_config(schema_file, output_file)


if __name__ == '__main__':
    main()
