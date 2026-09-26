"""محاسبه اندیکاتورها و ساخت متن تحلیل."""

from dataclasses import dataclass

import pandas as pd
import ta

from config import INTERVAL


@dataclass
class IndicatorSnapshot:
    price: float
    rsi: float
    macd: float
    macd_signal: float
    sma20: float
    sma50: float


def compute_indicators(df: pd.DataFrame) -> IndicatorSnapshot:
    close = df["close"]

    rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()
    macd_indicator = ta.trend.MACD(close=close)
    macd_line = macd_indicator.macd()
    macd_signal = macd_indicator.macd_signal()
    sma_20 = ta.trend.SMAIndicator(close=close, window=20).sma_indicator()
    sma_50 = ta.trend.SMAIndicator(close=close, window=50).sma_indicator()

    return IndicatorSnapshot(
        price=close.iloc[-1],
        rsi=rsi.iloc[-1],
        macd=macd_line.iloc[-1],
        macd_signal=macd_signal.iloc[-1],
        sma20=sma_20.iloc[-1],
        sma50=sma_50.iloc[-1],
    )


def build_analysis_text(symbol_name: str, snap: IndicatorSnapshot) -> str:
    if snap.rsi > 70:
        rsi_comment = "اشباع خرید (احتمال اصلاح قیمت)"
    elif snap.rsi < 30:
        rsi_comment = "اشباع فروش (احتمال برگشت قیمت)"
    else:
        rsi_comment = "در محدوده خنثی"

    macd_comment = (
        "مثبت (روند صعودی کوتاه‌مدت)"
        if snap.macd > snap.macd_signal
        else "منفی (روند نزولی کوتاه‌مدت)"
    )

    trend_comment = (
        "روند صعودی (SMA20 بالای SMA50)"
        if snap.sma20 > snap.sma50
        else "روند نزولی (SMA20 زیر SMA50)"
    )

    text = (
        f"📊 تحلیل {symbol_name} — بازه {INTERVAL}\n\n"
        f"💰 قیمت فعلی: {snap.price:.2f}\n\n"
        f"RSI: {snap.rsi:.1f} → {rsi_comment}\n"
        f"MACD: {macd_comment}\n"
        f"روند میانگین متحرک: {trend_comment}\n\n"
        f"⚠️ این فقط یک تحلیل خودکار بر پایه اندیکاتورهاست و "
        f"توصیه مالی محسوب نمی‌شود.\n"
        f"📡 منبع داده: Servix"
    )
    return text
