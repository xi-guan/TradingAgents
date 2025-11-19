"""技术指标服务"""

from typing import Any
from uuid import UUID

import numpy as np
import pandas as pd
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock import Stock, StockHistory


class IndicatorsService:
    """技术指标计算服务"""

    @staticmethod
    async def calculate_indicators(
        db: AsyncSession,
        symbol: str,
        market: str,
        indicators: list[str],
        period: int = 14,
    ) -> dict[str, Any]:
        """
        计算技术指标

        Args:
            db: 数据库会话
            symbol: 股票代码
            market: 市场
            indicators: 指标列表 ['sma', 'ema', 'rsi', 'macd', 'bbands', 'kdj', 'obv']
            period: 计算周期（天数）

        Returns:
            指标数据字典
        """
        # 获取股票
        stmt = select(Stock).where(
            and_(
                Stock.symbol == symbol,
                Stock.market == market,
            )
        )
        result = await db.execute(stmt)
        stock = result.scalar_one_or_none()

        if not stock:
            return {}

        # 获取历史数据（需要更多数据来计算指标）
        lookback_days = max(period * 3, 100)  # 获取足够的数据
        stmt = (
            select(StockHistory)
            .where(StockHistory.stock_id == stock.id)
            .order_by(StockHistory.timestamp.desc())
            .limit(lookback_days)
        )
        result = await db.execute(stmt)
        history = list(result.scalars().all())

        if not history:
            return {}

        # 转换为 DataFrame（反转顺序，使其按时间升序）
        df = pd.DataFrame([
            {
                "timestamp": h.timestamp,
                "open": float(h.open) if h.open else None,
                "high": float(h.high) if h.high else None,
                "low": float(h.low) if h.low else None,
                "close": float(h.close) if h.close else None,
                "volume": h.volume if h.volume else 0,
            }
            for h in reversed(history)
        ])

        # 计算各个指标
        results = {}

        for indicator in indicators:
            if indicator == "sma":
                results["sma"] = IndicatorsService._calculate_sma(df, period)
            elif indicator == "ema":
                results["ema"] = IndicatorsService._calculate_ema(df, period)
            elif indicator == "rsi":
                results["rsi"] = IndicatorsService._calculate_rsi(df, period)
            elif indicator == "macd":
                results["macd"] = IndicatorsService._calculate_macd(df)
            elif indicator == "bbands":
                results["bbands"] = IndicatorsService._calculate_bbands(df, period)
            elif indicator == "kdj":
                results["kdj"] = IndicatorsService._calculate_kdj(df, period)
            elif indicator == "obv":
                results["obv"] = IndicatorsService._calculate_obv(df)

        return results

    @staticmethod
    def _calculate_sma(df: pd.DataFrame, period: int = 20) -> dict[str, Any]:
        """简单移动平均线 (Simple Moving Average)"""
        sma = df["close"].rolling(window=period).mean()

        return {
            "name": "SMA",
            "period": period,
            "values": sma.dropna().tolist(),
            "current": float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None,
        }

    @staticmethod
    def _calculate_ema(df: pd.DataFrame, period: int = 20) -> dict[str, Any]:
        """指数移动平均线 (Exponential Moving Average)"""
        ema = df["close"].ewm(span=period, adjust=False).mean()

        return {
            "name": "EMA",
            "period": period,
            "values": ema.dropna().tolist(),
            "current": float(ema.iloc[-1]) if not pd.isna(ema.iloc[-1]) else None,
        }

    @staticmethod
    def _calculate_rsi(df: pd.DataFrame, period: int = 14) -> dict[str, Any]:
        """相对强弱指标 (Relative Strength Index)"""
        close = df["close"]
        delta = close.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        current = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None

        # 判断超买超卖
        signal = None
        if current:
            if current > 70:
                signal = "overbought"  # 超买
            elif current < 30:
                signal = "oversold"  # 超卖
            else:
                signal = "neutral"  # 中性

        return {
            "name": "RSI",
            "period": period,
            "values": rsi.dropna().tolist(),
            "current": current,
            "signal": signal,
        }

    @staticmethod
    def _calculate_macd(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> dict[str, Any]:
        """MACD (Moving Average Convergence Divergence)"""
        close = df["close"]

        # 计算 MACD
        ema_fast = close.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False).mean()
        macd_line = ema_fast - ema_slow

        # 计算信号线
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

        # 计算柱状图
        histogram = macd_line - signal_line

        macd_current = float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None
        signal_current = float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None
        histogram_current = float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None

        # 判断交叉信号
        cross_signal = None
        if macd_current and signal_current:
            if len(macd_line) > 1 and len(signal_line) > 1:
                macd_prev = macd_line.iloc[-2]
                signal_prev = signal_line.iloc[-2]

                if macd_prev < signal_prev and macd_current > signal_current:
                    cross_signal = "bullish"  # 金叉（买入信号）
                elif macd_prev > signal_prev and macd_current < signal_current:
                    cross_signal = "bearish"  # 死叉（卖出信号）

        return {
            "name": "MACD",
            "macd_line": macd_line.dropna().tolist(),
            "signal_line": signal_line.dropna().tolist(),
            "histogram": histogram.dropna().tolist(),
            "current": {
                "macd": macd_current,
                "signal": signal_current,
                "histogram": histogram_current,
            },
            "cross_signal": cross_signal,
        }

    @staticmethod
    def _calculate_bbands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> dict[str, Any]:
        """布林带 (Bollinger Bands)"""
        close = df["close"]

        # 中轨（SMA）
        middle_band = close.rolling(window=period).mean()

        # 标准差
        rolling_std = close.rolling(window=period).std()

        # 上轨和下轨
        upper_band = middle_band + (rolling_std * std_dev)
        lower_band = middle_band - (rolling_std * std_dev)

        current_price = float(close.iloc[-1]) if not pd.isna(close.iloc[-1]) else None
        upper_current = float(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else None
        middle_current = float(middle_band.iloc[-1]) if not pd.isna(middle_band.iloc[-1]) else None
        lower_current = float(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else None

        # 判断位置
        position = None
        if current_price and upper_current and lower_current:
            if current_price > upper_current:
                position = "above_upper"  # 价格在上轨之上
            elif current_price < lower_current:
                position = "below_lower"  # 价格在下轨之下
            else:
                position = "within_bands"  # 价格在带内

        return {
            "name": "Bollinger Bands",
            "period": period,
            "std_dev": std_dev,
            "upper_band": upper_band.dropna().tolist(),
            "middle_band": middle_band.dropna().tolist(),
            "lower_band": lower_band.dropna().tolist(),
            "current": {
                "upper": upper_current,
                "middle": middle_current,
                "lower": lower_current,
                "price": current_price,
            },
            "position": position,
        }

    @staticmethod
    def _calculate_kdj(df: pd.DataFrame, period: int = 9, m1: int = 3, m2: int = 3) -> dict[str, Any]:
        """KDJ 指标 (中国市场常用)"""
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # 计算 RSV (Raw Stochastic Value)
        low_min = low.rolling(window=period).min()
        high_max = high.rolling(window=period).max()
        rsv = (close - low_min) / (high_max - low_min) * 100

        # 计算 K, D, J
        k = rsv.ewm(com=m1 - 1, adjust=False).mean()
        d = k.ewm(com=m2 - 1, adjust=False).mean()
        j = 3 * k - 2 * d

        k_current = float(k.iloc[-1]) if not pd.isna(k.iloc[-1]) else None
        d_current = float(d.iloc[-1]) if not pd.isna(d.iloc[-1]) else None
        j_current = float(j.iloc[-1]) if not pd.isna(j.iloc[-1]) else None

        # 判断交叉信号
        cross_signal = None
        if k_current and d_current and len(k) > 1 and len(d) > 1:
            k_prev = k.iloc[-2]
            d_prev = d.iloc[-2]

            if k_prev < d_prev and k_current > d_current:
                cross_signal = "golden_cross"  # 金叉
            elif k_prev > d_prev and k_current < d_current:
                cross_signal = "death_cross"  # 死叉

        # 判断超买超卖
        signal = None
        if k_current and d_current:
            if k_current > 80 and d_current > 80:
                signal = "overbought"
            elif k_current < 20 and d_current < 20:
                signal = "oversold"
            else:
                signal = "neutral"

        return {
            "name": "KDJ",
            "period": period,
            "k_values": k.dropna().tolist(),
            "d_values": d.dropna().tolist(),
            "j_values": j.dropna().tolist(),
            "current": {
                "k": k_current,
                "d": d_current,
                "j": j_current,
            },
            "cross_signal": cross_signal,
            "signal": signal,
        }

    @staticmethod
    def _calculate_obv(df: pd.DataFrame) -> dict[str, Any]:
        """能量潮指标 (On-Balance Volume)"""
        close = df["close"]
        volume = df["volume"]

        obv = np.where(
            close > close.shift(1),
            volume,
            np.where(close < close.shift(1), -volume, 0)
        ).cumsum()

        obv_series = pd.Series(obv, index=df.index)
        current = float(obv_series.iloc[-1]) if not pd.isna(obv_series.iloc[-1]) else None

        # 计算 OBV 的移动平均
        obv_ma = obv_series.rolling(window=20).mean()
        obv_ma_current = float(obv_ma.iloc[-1]) if not pd.isna(obv_ma.iloc[-1]) else None

        # 判断趋势
        trend = None
        if current and obv_ma_current:
            if current > obv_ma_current:
                trend = "bullish"  # 上升趋势
            else:
                trend = "bearish"  # 下降趋势

        return {
            "name": "OBV",
            "values": obv_series.dropna().tolist(),
            "ma_values": obv_ma.dropna().tolist(),
            "current": current,
            "ma_current": obv_ma_current,
            "trend": trend,
        }

    @staticmethod
    async def get_all_indicators(
        db: AsyncSession,
        symbol: str,
        market: str,
        period: int = 14,
    ) -> dict[str, Any]:
        """获取所有技术指标"""
        return await IndicatorsService.calculate_indicators(
            db,
            symbol,
            market,
            ["sma", "ema", "rsi", "macd", "bbands", "kdj", "obv"],
            period,
        )
