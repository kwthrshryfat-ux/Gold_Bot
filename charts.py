"""ساخت نمودار تصویری قیمت + میانگین متحرک و RSI."""

import io

import matplotlib
matplotlib.use("Agg")  # اجرای بدون نیاز به نمایشگر (مناسب سرور)
import matplotlib.pyplot as plt
import pandas as pd
import ta


def build_chart_image(df: pd.DataFrame, symbol_name: str) -> io.BytesIO:
    """یک نمودار PNG شامل قیمت+SMA و زیرنمودار RSI می‌سازه و برمی‌گردونه."""
    close = df["close"]
    sma20 = ta.trend.SMAIndicator(close=close, window=20).sma_indicator()
    sma50 = ta.trend.SMAIndicator(close=close, window=50).sma_indicator()
    rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()

    fig, (ax_price, ax_rsi) = plt.subplots(
        2, 1, figsize=(10, 6), gridspec_kw={"height_ratios": [3, 1]}, sharex=True
    )

    ax_price.plot(df["datetime"], close, label="قیمت", color="#2E5395", linewidth=1.5)
    ax_price.plot(df["datetime"], sma20, label="SMA20", color="#E8A33D", linewidth=1)
    ax_price.plot(df["datetime"], sma50, label="SMA50", color="#C0392B", linewidth=1)
    ax_price.set_title(f"{symbol_name} — نمودار قیمت و میانگین متحرک")
    ax_price.legend(loc="upper left")
    ax_price.grid(alpha=0.3)

    ax_rsi.plot(df["datetime"], rsi, color="#6A4C93", linewidth=1.2)
    ax_rsi.axhline(70, color="red", linestyle="--", linewidth=0.8)
    ax_rsi.axhline(30, color="green", linestyle="--", linewidth=0.8)
    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_title("RSI")
    ax_rsi.grid(alpha=0.3)

    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120)
    plt.close(fig)
    buffer.seek(0)
    return buffer
