"""交易时间工具函数"""

from datetime import datetime, time as dtime, timedelta
from typing import Literal
import pytz

# 时区定义
CN_TIMEZONE = pytz.timezone('Asia/Shanghai')
HK_TIMEZONE = pytz.timezone('Asia/Hong_Kong')
US_TIMEZONE = pytz.timezone('America/New_York')

MarketType = Literal["CN", "HK", "US"]


def is_cn_trading_time(dt: datetime = None) -> bool:
    """
    判断是否在 A股交易时间

    Args:
        dt: 时间（默认为当前时间）

    Returns:
        是否在交易时间
    """
    if dt is None:
        dt = datetime.now(CN_TIMEZONE)
    elif dt.tzinfo is None:
        dt = CN_TIMEZONE.localize(dt)
    else:
        dt = dt.astimezone(CN_TIMEZONE)

    # 周末不交易
    if dt.weekday() >= 5:
        return False

    # 交易时间段
    morning_start = dtime(9, 30)
    noon_end = dtime(11, 30)
    afternoon_start = dtime(13, 0)
    close_end = dtime(15, 0)

    t = dt.time()
    return (morning_start <= t <= noon_end) or (afternoon_start <= t <= close_end)


def is_hk_trading_time(dt: datetime = None) -> bool:
    """
    判断是否在港股交易时间

    Args:
        dt: 时间（默认为当前时间）

    Returns:
        是否在交易时间
    """
    if dt is None:
        dt = datetime.now(HK_TIMEZONE)
    elif dt.tzinfo is None:
        dt = HK_TIMEZONE.localize(dt)
    else:
        dt = dt.astimezone(HK_TIMEZONE)

    # 周末不交易
    if dt.weekday() >= 5:
        return False

    # 交易时间段
    morning_start = dtime(9, 30)
    noon_end = dtime(12, 0)
    afternoon_start = dtime(13, 0)
    close_end = dtime(16, 0)

    t = dt.time()
    return (morning_start <= t <= noon_end) or (afternoon_start <= t <= close_end)


def is_us_trading_time(dt: datetime = None) -> bool:
    """
    判断是否在美股交易时间

    Args:
        dt: 时间（默认为当前时间）

    Returns:
        是否在交易时间
    """
    if dt is None:
        dt = datetime.now(US_TIMEZONE)
    elif dt.tzinfo is None:
        dt = US_TIMEZONE.localize(dt)
    else:
        dt = dt.astimezone(US_TIMEZONE)

    # 周末不交易
    if dt.weekday() >= 5:
        return False

    # 交易时间段（9:30 - 16:00）
    trading_start = dtime(9, 30)
    trading_end = dtime(16, 0)

    t = dt.time()
    return trading_start <= t <= trading_end


def is_trading_time(market: MarketType, dt: datetime = None) -> bool:
    """
    判断是否在交易时间

    Args:
        market: 市场类型
        dt: 时间（默认为当前时间）

    Returns:
        是否在交易时间
    """
    if market == "CN":
        return is_cn_trading_time(dt)
    elif market == "HK":
        return is_hk_trading_time(dt)
    else:  # US
        return is_us_trading_time(dt)


def get_latest_trading_day(market: MarketType = "CN") -> datetime:
    """
    获取最近交易日

    Args:
        market: 市场类型

    Returns:
        最近交易日
    """
    if market == "CN":
        tz = CN_TIMEZONE
    elif market == "HK":
        tz = HK_TIMEZONE
    else:
        tz = US_TIMEZONE

    today = datetime.now(tz).date()

    # 如果是周末，回退到周五
    while today.weekday() >= 5:
        today -= timedelta(days=1)

    return datetime.combine(today, dtime(0, 0), tzinfo=tz)


def get_trading_status(market: MarketType) -> str:
    """
    获取当前交易状态

    Args:
        market: 市场类型

    Returns:
        交易状态（"交易中", "休市", "盘前", "盘后"）
    """
    if market == "CN":
        tz = CN_TIMEZONE
        morning_start = dtime(9, 30)
        noon_end = dtime(11, 30)
        afternoon_start = dtime(13, 0)
        close_end = dtime(15, 0)
        pre_market_start = dtime(9, 0)
    elif market == "HK":
        tz = HK_TIMEZONE
        morning_start = dtime(9, 30)
        noon_end = dtime(12, 0)
        afternoon_start = dtime(13, 0)
        close_end = dtime(16, 0)
        pre_market_start = dtime(9, 0)
    else:  # US
        tz = US_TIMEZONE
        morning_start = dtime(9, 30)
        noon_end = None
        afternoon_start = None
        close_end = dtime(16, 0)
        pre_market_start = dtime(4, 0)

    now = datetime.now(tz)

    # 周末
    if now.weekday() >= 5:
        return "休市"

    t = now.time()

    # 盘前
    if pre_market_start <= t < morning_start:
        return "盘前"

    # 交易中
    if is_trading_time(market, now):
        return "交易中"

    # 盘后
    if market in ["CN", "HK"]:
        if t > close_end or (noon_end and noon_end < t < afternoon_start):
            return "盘后"
    else:  # US
        if t > close_end:
            return "盘后"

    return "休市"
