"""Tushare 数据提供者"""

import asyncio
from datetime import datetime
from typing import Any

import pandas as pd

from app.config import settings
from app.data_providers.base import BaseDataProvider
from app.utils.market_utils import normalize_tushare_symbol


class TushareProvider(BaseDataProvider):
    """Tushare 数据提供者（中国 A 股）"""

    def __init__(self):
        """初始化 Tushare 客户端"""
        try:
            import tushare as ts

            self.ts = ts
            self.pro = ts.pro_api(settings.tushare_token) if settings.tushare_token else None
        except ImportError:
            self.ts = None
            self.pro = None

    def _check_available(self) -> bool:
        """检查 Tushare 是否可用"""
        return self.pro is not None

    async def get_stock_info(self, symbol: str) -> dict[str, Any] | None:
        """获取股票基本信息"""
        if not self._check_available():
            return None

        try:
            # 转换股票代码格式 (000001 -> 000001.SZ)
            ts_symbol = normalize_tushare_symbol(symbol)

            # 在线程池中运行同步函数
            df = await asyncio.to_thread(
                self.pro.stock_basic,
                ts_code=ts_symbol,
                fields="ts_code,symbol,name,area,industry,market,list_date",
            )

            if df.empty:
                return None

            row = df.iloc[0]
            return {
                "symbol": row["symbol"],
                "name": row["name"],
                "sector": row.get("area", ""),
                "industry": row.get("industry", ""),
                "market": "CN",
                "list_date": row.get("list_date", ""),
            }

        except Exception as e:
            print(f"Tushare get_stock_info error: {e}")
            return None

    async def get_realtime_quote(self, symbol: str) -> dict[str, Any] | None:
        """获取实时行情"""
        if not self._check_available():
            return None

        try:
            # Tushare 的实时行情需要付费权限，这里使用最新日线数据代替
            ts_symbol = normalize_tushare_symbol(symbol)

            # 获取最新日线数据
            df = await asyncio.to_thread(
                self.pro.daily,
                ts_code=ts_symbol,
                start_date=datetime.now().strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
            )

            if df.empty:
                # 如果当天没有数据，获取最近一个交易日的数据
                df = await asyncio.to_thread(
                    self.pro.daily, ts_code=ts_symbol, limit=1
                )

            if df.empty:
                return None

            row = df.iloc[0]
            return {
                "timestamp": pd.to_datetime(row["trade_date"], format="%Y%m%d"),
                "open": float(row["open"]) if pd.notna(row["open"]) else None,
                "high": float(row["high"]) if pd.notna(row["high"]) else None,
                "low": float(row["low"]) if pd.notna(row["low"]) else None,
                "close": float(row["close"]) if pd.notna(row["close"]) else None,
                "volume": int(row["vol"]) * 100 if pd.notna(row["vol"]) else 0,  # 手转换为股
                "prev_close": float(row["pre_close"]) if pd.notna(row["pre_close"]) else None,
                "change": float(row["change"]) if pd.notna(row["change"]) else None,
                "change_percent": float(row["pct_chg"]) if pd.notna(row["pct_chg"]) else None,
            }

        except Exception as e:
            print(f"Tushare get_realtime_quote error: {e}")
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
            ts_symbol = normalize_tushare_symbol(symbol)

            # Tushare 主要支持日线数据，分钟数据需要更高权限
            if interval == "1d":
                df = await asyncio.to_thread(
                    self.pro.daily,
                    ts_code=ts_symbol,
                    start_date=start_date.strftime("%Y%m%d"),
                    end_date=end_date.strftime("%Y%m%d"),
                )
            elif interval in ["1min", "5min", "15min", "30min", "60min"]:
                # 分钟数据（需要高级权限）
                freq = interval.replace("min", "")
                df = await asyncio.to_thread(
                    self.pro.stk_mins,
                    ts_code=ts_symbol,
                    start_date=start_date.strftime("%Y%m%d %H:%M:%S"),
                    end_date=end_date.strftime("%Y%m%d %H:%M:%S"),
                    freq=freq,
                )
            else:
                return []

            if df.empty:
                return []

            # 转换数据格式
            result = []
            for _, row in df.iterrows():
                result.append(
                    {
                        "timestamp": pd.to_datetime(row["trade_date"], format="%Y%m%d")
                        if interval == "1d"
                        else pd.to_datetime(row["trade_time"]),
                        "open": float(row["open"]) if pd.notna(row["open"]) else None,
                        "high": float(row["high"]) if pd.notna(row["high"]) else None,
                        "low": float(row["low"]) if pd.notna(row["low"]) else None,
                        "close": float(row["close"]) if pd.notna(row["close"]) else None,
                        "volume": int(row["vol"]) * 100 if pd.notna(row["vol"]) else 0,
                        "interval": interval,
                    }
                )

            return result

        except Exception as e:
            print(f"Tushare get_historical_data error: {e}")
            return []

    async def search_stocks(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """搜索股票"""
        if not self._check_available():
            return []

        try:
            # 获取所有股票列表
            df = await asyncio.to_thread(
                self.pro.stock_basic,
                fields="ts_code,symbol,name,area,industry,market,list_status",
            )

            if df.empty:
                return []

            # 过滤上市股票
            df = df[df["list_status"] == "L"]

            # 搜索：代码或名称包含查询词
            query_lower = query.lower()
            mask = (
                df["symbol"].str.contains(query_lower, case=False, na=False)
                | df["name"].str.contains(query, na=False)
            )
            df = df[mask]

            # 限制返回数量
            df = df.head(limit)

            # 转换结果
            result = []
            for _, row in df.iterrows():
                result.append(
                    {
                        "symbol": row["symbol"],
                        "name": row["name"],
                        "market": "CN",
                        "sector": row.get("area", ""),
                        "industry": row.get("industry", ""),
                    }
                )

            return result

        except Exception as e:
            print(f"Tushare search_stocks error: {e}")
            return []
