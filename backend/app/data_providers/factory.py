"""数据提供者工厂"""

from typing import Literal

from app.data_providers.akshare_provider import AkShareProvider
from app.data_providers.base import BaseDataProvider
from app.data_providers.tushare_provider import TushareProvider
from app.data_providers.yfinance_provider import YFinanceProvider

MarketType = Literal["CN", "HK", "US"]


class DataProviderFactory:
    """数据提供者工厂"""

    # 单例实例
    _tushare: TushareProvider | None = None
    _akshare: AkShareProvider | None = None
    _yfinance: YFinanceProvider | None = None

    @classmethod
    def get_tushare(cls) -> TushareProvider:
        """获取 Tushare 提供者"""
        if cls._tushare is None:
            cls._tushare = TushareProvider()
        return cls._tushare

    @classmethod
    def get_akshare(cls) -> AkShareProvider:
        """获取 AkShare 提供者"""
        if cls._akshare is None:
            cls._akshare = AkShareProvider()
        return cls._akshare

    @classmethod
    def get_yfinance(cls) -> YFinanceProvider:
        """获取 YFinance 提供者"""
        if cls._yfinance is None:
            cls._yfinance = YFinanceProvider()
        return cls._yfinance

    @classmethod
    def get_provider(
        cls, market: MarketType, prefer_tushare: bool = True
    ) -> BaseDataProvider:
        """
        根据市场类型获取数据提供者

        Args:
            market: 市场类型 (CN/HK/US)
            prefer_tushare: 对于 A 股，优先使用 Tushare（需要 token）

        Returns:
            数据提供者实例
        """
        if market == "CN":
            # A 股优先使用 Tushare，如果不可用则使用 AkShare
            if prefer_tushare:
                tushare = cls.get_tushare()
                if tushare._check_available():
                    return tushare

            # 降级到 AkShare
            return cls.get_akshare()

        elif market == "HK":
            # 港股使用 YFinance（AkShare 也支持，但 YFinance 更稳定）
            return cls.get_yfinance()

        else:
            # 美股和其他国际股票使用 YFinance
            return cls.get_yfinance()

    @classmethod
    def get_all_cn_providers(cls) -> list[BaseDataProvider]:
        """获取所有可用的 A 股数据提供者"""
        providers = []

        tushare = cls.get_tushare()
        if tushare._check_available():
            providers.append(tushare)

        akshare = cls.get_akshare()
        if akshare._check_available():
            providers.append(akshare)

        return providers
