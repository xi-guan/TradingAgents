"""市场工具函数"""

import re
from typing import Literal, Tuple

MarketType = Literal["CN", "HK", "US"]


def normalize_symbol(symbol: str) -> Tuple[str, MarketType]:
    """
    标准化股票代码

    Args:
        symbol: 股票代码

    Returns:
        (标准化代码, 市场类型)

    Examples:
        >>> normalize_symbol("000001")
        ("000001.SZ", "CN")
        >>> normalize_symbol("600000")
        ("600000.SH", "CN")
        >>> normalize_symbol("00700")
        ("00700.HK", "HK")
        >>> normalize_symbol("AAPL")
        ("AAPL", "US")
    """
    symbol = symbol.strip().upper()

    # A股（6位数字）
    if re.match(r'^\d{6}$', symbol):
        # 上交所：6、5开头
        if symbol.startswith(('6', '5')):
            return f"{symbol}.SH", "CN"
        # 深交所：0、3开头
        else:
            return f"{symbol}.SZ", "CN"

    # 已带后缀的 A股
    if re.match(r'^\d{6}\.(SH|SZ)$', symbol):
        return symbol, "CN"

    # 港股（4-5位数字）
    if re.match(r'^\d{4,5}$', symbol):
        # 补齐到5位
        symbol = symbol.zfill(5)
        return f"{symbol}.HK", "HK"

    # 已带后缀的港股
    if re.match(r'^\d{4,5}\.HK$', symbol):
        code = symbol.split('.')[0].zfill(5)
        return f"{code}.HK", "HK"

    # 美股（字母）
    return symbol, "US"


def check_limit_status(
    symbol: str,
    current_price: float,
    prev_close: float
) -> Tuple[bool, str]:
    """
    检测涨跌停状态

    Args:
        symbol: 股票代码
        current_price: 当前价格
        prev_close: 昨收价

    Returns:
        (是否涨跌停, 状态描述)
    """
    if prev_close == 0:
        return False, "正常"

    change_pct = (current_price - prev_close) / prev_close * 100

    # ST股票 5% 限制
    if symbol.startswith(('*ST', 'ST')):
        if change_pct >= 4.95:
            return True, "涨停"
        elif change_pct <= -4.95:
            return True, "跌停"

    # 普通股票 10% 限制
    else:
        if change_pct >= 9.95:
            return True, "涨停"
        elif change_pct <= -9.95:
            return True, "跌停"

    return False, "正常"


def get_market_currency(market: MarketType) -> str:
    """
    获取市场对应的货币

    Args:
        market: 市场类型

    Returns:
        货币代码
    """
    currency_map = {
        "CN": "CNY",
        "HK": "HKD",
        "US": "USD",
    }
    return currency_map.get(market, "USD")


def get_market_timezone(market: MarketType) -> str:
    """
    获取市场对应的时区

    Args:
        market: 市场类型

    Returns:
        时区名称
    """
    timezone_map = {
        "CN": "Asia/Shanghai",
        "HK": "Asia/Hong_Kong",
        "US": "America/New_York",
    }
    return timezone_map.get(market, "UTC")


def normalize_tushare_symbol(symbol: str) -> str:
    """
    转换为 Tushare 格式的股票代码

    Args:
        symbol: 股票代码

    Returns:
        Tushare 格式代码 (如: 000001.SZ, 600000.SH)

    Examples:
        >>> normalize_tushare_symbol("000001")
        "000001.SZ"
        >>> normalize_tushare_symbol("600000.SH")
        "600000.SH"
    """
    normalized, market = normalize_symbol(symbol)

    # Tushare 格式已经是标准格式
    if market == "CN":
        return normalized

    # 非 A 股不支持
    return symbol
