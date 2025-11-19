"""AkShare 数据提供者"""

import asyncio
from datetime import datetime
from typing import Any

import pandas as pd

from app.data_providers.base import BaseDataProvider


class AkShareProvider(BaseDataProvider):
    """AkShare 数据提供者（中国 A 股/港股/美股）"""

    def __init__(self):
        """初始化 AkShare"""
        try:
            import akshare as ak

            self.ak = ak
        except ImportError:
            self.ak = None

    def _check_available(self) -> bool:
        """检查 AkShare 是否可用"""
        return self.ak is not None

    async def get_stock_info(self, symbol: str) -> dict[str, Any] | None:
        """获取股票基本信息"""
        if not self._check_available():
            return None

        try:
            # A 股股票信息
            if len(symbol) == 6 and symbol.isdigit():
                # 获取股票基本信息
                df = await asyncio.to_thread(
                    self.ak.stock_individual_info_em, symbol=symbol
                )

                if df.empty:
                    return None

                # 转换为字典
                info_dict = dict(zip(df["item"], df["value"]))

                return {
                    "symbol": symbol,
                    "name": info_dict.get("股票简称", ""),
                    "sector": info_dict.get("所属行业", ""),
                    "industry": info_dict.get("所属行业", ""),
                    "market": "CN",
                    "description": info_dict.get("公司简介", ""),
                }

        except Exception as e:
            print(f"AkShare get_stock_info error: {e}")

        return None

    async def get_realtime_quote(self, symbol: str) -> dict[str, Any] | None:
        """获取实时行情"""
        if not self._check_available():
            return None

        try:
            # A 股实时行情
            if len(symbol) == 6 and symbol.isdigit():
                # 获取实时行情数据
                df = await asyncio.to_thread(
                    self.ak.stock_zh_a_spot_em
                )

                if df.empty:
                    return None

                # 查找对应股票
                stock_df = df[df["代码"] == symbol]
                if stock_df.empty:
                    return None

                row = stock_df.iloc[0]

                return {
                    "timestamp": datetime.now(),
                    "open": float(row["今开"]) if pd.notna(row["今开"]) else None,
                    "high": float(row["最高"]) if pd.notna(row["最高"]) else None,
                    "low": float(row["最低"]) if pd.notna(row["最低"]) else None,
                    "close": float(row["最新价"]) if pd.notna(row["最新价"]) else None,
                    "volume": int(row["成交量"]) if pd.notna(row["成交量"]) else 0,
                    "prev_close": float(row["昨收"]) if pd.notna(row["昨收"]) else None,
                    "change": float(row["涨跌额"]) if pd.notna(row["涨跌额"]) else None,
                    "change_percent": float(row["涨跌幅"]) if pd.notna(row["涨跌幅"]) else None,
                }

        except Exception as e:
            print(f"AkShare get_realtime_quote error: {e}")

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
            # A 股历史数据
            if len(symbol) == 6 and symbol.isdigit():
                # 转换日期格式
                start_str = start_date.strftime("%Y%m%d")
                end_str = end_date.strftime("%Y%m%d")

                # 根据间隔选择不同的接口
                if interval == "1d":
                    # 日线数据
                    df = await asyncio.to_thread(
                        self.ak.stock_zh_a_hist,
                        symbol=symbol,
                        start_date=start_str,
                        end_date=end_str,
                        adjust="qfq",  # 前复权
                    )
                elif interval in ["1", "5", "15", "30", "60"]:
                    # 分钟数据
                    df = await asyncio.to_thread(
                        self.ak.stock_zh_a_hist_min_em,
                        symbol=symbol,
                        period=interval,
                        start_date=start_str + " 09:30:00",
                        end_date=end_str + " 15:00:00",
                        adjust="qfq",
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
                            "timestamp": pd.to_datetime(row["日期"])
                            if "日期" in row
                            else pd.to_datetime(row["时间"]),
                            "open": float(row["开盘"]) if pd.notna(row["开盘"]) else None,
                            "high": float(row["最高"]) if pd.notna(row["最高"]) else None,
                            "low": float(row["最低"]) if pd.notna(row["最低"]) else None,
                            "close": float(row["收盘"]) if pd.notna(row["收盘"]) else None,
                            "volume": int(row["成交量"]) if pd.notna(row["成交量"]) else 0,
                            "interval": interval,
                        }
                    )

                return result

        except Exception as e:
            print(f"AkShare get_historical_data error: {e}")

        return []

    async def search_stocks(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """搜索股票"""
        if not self._check_available():
            return []

        try:
            # 获取所有 A 股列表
            df = await asyncio.to_thread(self.ak.stock_zh_a_spot_em)

            if df.empty:
                return []

            # 搜索：代码或名称包含查询词
            query_upper = query.upper()
            mask = (
                df["代码"].str.contains(query, case=False, na=False)
                | df["名称"].str.contains(query, na=False)
            )
            df = df[mask]

            # 限制返回数量
            df = df.head(limit)

            # 转换结果
            result = []
            for _, row in df.iterrows():
                result.append(
                    {
                        "symbol": row["代码"],
                        "name": row["名称"],
                        "market": "CN",
                        "sector": "",
                        "industry": "",
                    }
                )

            return result

        except Exception as e:
            print(f"AkShare search_stocks error: {e}")
            return []
