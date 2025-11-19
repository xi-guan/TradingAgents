"""基础数据提供者"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseDataProvider(ABC):
    """数据提供者基类"""

    @abstractmethod
    async def get_stock_info(self, symbol: str) -> dict[str, Any] | None:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            股票信息字典，包含 name, sector, industry 等字段
        """
        pass

    @abstractmethod
    async def get_realtime_quote(self, symbol: str) -> dict[str, Any] | None:
        """
        获取实时行情

        Args:
            symbol: 股票代码

        Returns:
            行情字典，包含 open, high, low, close, volume 等字段
        """
        pass

    @abstractmethod
    async def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> list[dict[str, Any]]:
        """
        获取历史数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            interval: 时间间隔 (1d, 1h, 5m, etc.)

        Returns:
            历史数据列表
        """
        pass

    @abstractmethod
    async def search_stocks(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        搜索股票

        Args:
            query: 搜索关键词
            limit: 返回数量限制

        Returns:
            股票列表
        """
        pass
