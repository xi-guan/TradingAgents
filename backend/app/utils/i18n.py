"""国际化工具"""

import json
from typing import Dict
from pathlib import Path

class I18n:
    """国际化工具类"""

    def __init__(self):
        self.messages: Dict[str, Dict] = {}
        self._load_messages()

    def _load_messages(self):
        """加载翻译文件"""
        locales_dir = Path(__file__).parent.parent / "locales"

        for locale_dir in locales_dir.iterdir():
            if locale_dir.is_dir():
                locale = locale_dir.name
                messages_file = locale_dir / "messages.json"

                if messages_file.exists():
                    with open(messages_file, "r", encoding="utf-8") as f:
                        self.messages[locale] = json.load(f)

    def t(self, key: str, locale: str = "zh_CN", **kwargs) -> str:
        """
        翻译文本

        Args:
            key: 翻译键（支持点号分隔，如 "auth.login_success"）
            locale: 语言代码
            **kwargs: 格式化参数

        Returns:
            翻译后的文本
        """
        # 获取语言包
        messages = self.messages.get(locale, self.messages.get("zh_CN", {}))

        # 递归查找键值
        keys = key.split(".")
        value = messages

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                break

        # 如果找不到，返回原键
        if value is None or not isinstance(value, str):
            return key

        # 格式化参数
        return value.format(**kwargs) if kwargs else value


# 全局实例
i18n = I18n()
