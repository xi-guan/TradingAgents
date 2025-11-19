"""YFinance 数据提供者"""

import asyncio
from datetime import datetime
from typing import Any

import pandas as pd

from app.data_providers.base import BaseDataProvider


class YFinanceProvider(BaseDataProvider):
    """YFinance 数据提供者（美股/港股/国际股票）"""

    def __init__(self):
        """初始化 YFinance"""
        try:
            import yfinance as yf

            self.yf = yf
        except ImportError:
            self.yf = None

    def _check_available(self) -> bool:
        """检查 YFinance 是否可用"""
        return self.yf is not None

    async def get_stock_info(self, symbol: str) -> dict[str, Any] | None:
        """获取股票基本信息"""
        if not self._check_available():
            return None

        try:
            ticker = self.yf.Ticker(symbol)

            # 在线程池中运行同步函数
            info = await asyncio.to_thread(lambda: ticker.info)

            if not info:
                return None

            return {
                "symbol": symbol,
                "name": info.get("longName", info.get("shortName", "")),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market": "US" if not symbol.endswith(".HK") else "HK",
                "description": info.get("longBusinessSummary", ""),
            }

        except Exception as e:
            print(f"YFinance get_stock_info error: {e}")
            return None

    async def get_realtime_quote(self, symbol: str) -> dict[str, Any] | None:
        """获取实时行情"""
        if not self._check_available():
            return None

        try:
            ticker = self.yf.Ticker(symbol)

            # 获取最新价格数据
            hist = await asyncio.to_thread(
                lambda: ticker.history(period="1d", interval="1m")
            )

            if hist.empty:
                # 如果没有分钟数据，获取日线数据
                hist = await asyncio.to_thread(
                    lambda: ticker.history(period="5d", interval="1d")
                )

            if hist.empty:
                return None

            # 获取最新一条数据
            latest = hist.iloc[-1]
            prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Close"]

            return {
                "timestamp": latest.name,
                "open": float(latest["Open"]) if pd.notna(latest["Open"]) else None,
                "high": float(latest["High"]) if pd.notna(latest["High"]) else None,
                "low": float(latest["Low"]) if pd.notna(latest["Low"]) else None,
                "close": float(latest["Close"]) if pd.notna(latest["Close"]) else None,
                "volume": int(latest["Volume"]) if pd.notna(latest["Volume"]) else 0,
                "prev_close": float(prev_close) if pd.notna(prev_close) else None,
                "change": float(latest["Close"] - prev_close)
                if pd.notna(latest["Close"]) and pd.notna(prev_close)
                else None,
                "change_percent": float((latest["Close"] - prev_close) / prev_close * 100)
                if pd.notna(latest["Close"]) and pd.notna(prev_close) and prev_close != 0
                else None,
            }

        except Exception as e:
            print(f"YFinance get_realtime_quote error: {e}")
            return None

    async def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> list[dict[str, Any]]:
        """获取历史数据"""
        if not self._check_available():
            return []

        try:
            ticker = self.yf.Ticker(symbol)

            # YFinance 支持的间隔：1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            yf_interval = interval
            if interval == "1min":
                yf_interval = "1m"
            elif interval == "5min":
                yf_interval = "5m"
            elif interval == "15min":
                yf_interval = "15m"
            elif interval == "30min":
                yf_interval = "30m"
            elif interval == "60min":
                yf_interval = "1h"

            # 获取历史数据
            hist = await asyncio.to_thread(
                lambda: ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=yf_interval,
                )
            )

            if hist.empty:
                return []

            # 转换数据格式
            result = []
            for timestamp, row in hist.iterrows():
                result.append(
                    {
                        "timestamp": timestamp,
                        "open": float(row["Open"]) if pd.notna(row["Open"]) else None,
                        "high": float(row["High"]) if pd.notna(row["High"]) else None,
                        "low": float(row["Low"]) if pd.notna(row["Low"]) else None,
                        "close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                        "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
                        "adj_close": float(row.get("Adj Close", row["Close"]))
                        if pd.notna(row.get("Adj Close", row["Close"]))
                        else None,
                        "interval": interval,
                    }
                )

            return result

        except Exception as e:
            print(f"YFinance get_historical_data error: {e}")
            return []

    async def search_stocks(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        搜索股票

        注意：YFinance 不提供直接的搜索功能，这里只返回输入的查询作为符号
        """
        if not self._check_available():
            return []

        try:
            # YFinance 不提供搜索 API，尝试直接获取股票信息
            ticker = self.yf.Ticker(query.upper())
            info = await asyncio.to_thread(lambda: ticker.info)

            if not info or not info.get("symbol"):
                return []

            return [
                {
                    "symbol": info["symbol"],
                    "name": info.get("longName", info.get("shortName", "")),
                    "market": "US" if not query.endswith(".HK") else "HK",
                    "sector": info.get("sector", ""),
                    "industry": info.get("industry", ""),
                }
            ]

        except Exception as e:
            print(f"YFinance search_stocks error: {e}")
            return []
