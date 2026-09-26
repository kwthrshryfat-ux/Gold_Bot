"""دریافت داده‌های OHLC از Servix (بازار ایران)."""

import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from config import (
    HISTORY_DAYS,
    INTERVAL,
    OUTPUT_SIZE,
    SERVIX_BASE_URL,
)

def fetch_market_data(symbol: str) -> pd.DataFrame:
    """داده‌های کندلی یک نماد را از Servix می‌گیرد و به DataFrame تبدیل می‌کند."""

    # bot.py ماژول را قبل از load_dotenv وارد می‌کند؛ پس کلید را هنگام اجرا می‌خوانیم.
    servix_api_key = os.getenv("SERVIX_API_KEY")

    if not servix_api_key:
        raise RuntimeError(
            "متغیر SERVIX_API_KEY در فایل .env تنظیم نشده است."
        )

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=HISTORY_DAYS)

    url = f"{SERVIX_BASE_URL}/assets/{symbol}/ohlc"
    params = {
        "interval": INTERVAL,
        "from": start.isoformat().replace("+00:00", "Z"),
        "to": now.isoformat().replace("+00:00", "Z"),
    }
    headers = {"X-API-Key": servix_api_key}

    response = requests.get(url, params=params, headers=headers, timeout=20)

    if response.status_code == 401:
        raise RuntimeError("کلید SERVIX_API_KEY نامعتبر است یا ارسال نشده.")
    if response.status_code == 403:
        raise RuntimeError("دسترسی API Servix برای این حساب فعال نیست.")
    if response.status_code == 404:
        raise RuntimeError(f"نماد {symbol} در Servix پیدا نشد یا داده‌ای ندارد.")
    if response.status_code == 429:
        raise RuntimeError("سهمیه روزانه API Servix تمام شده است.")

    response.raise_for_status()
    data = response.json()

    if data.get("s") == "error":
        raise RuntimeError(f"خطای Servix برای {symbol}: {data}")

    candles = data.get("candles")
    if not candles:
        raise RuntimeError(f"برای {symbol} کندل قابل استفاده‌ای از Servix دریافت نشد.")

    df = pd.DataFrame(candles)

    required = ["start", "open", "high", "low", "close"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise RuntimeError(
            f"ساختار پاسخ Servix ناقص است؛ ستون‌های موجود نیستند: {missing}"
        )

    df["datetime"] = pd.to_datetime(df["start"], utc=True)

    numeric_cols = ["open", "high", "low", "close"]
    for column in numeric_cols:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = (
        df.dropna(subset=["datetime", *numeric_cols])
        .sort_values("datetime")
        .drop_duplicates(subset=["datetime"])
        .reset_index(drop=True)
    )

    # آخرین کندل‌ها را نگه می‌داریم تا حجم داده برای اندیکاتورها کنترل شود.
    if len(df) > OUTPUT_SIZE:
        df = df.tail(OUTPUT_SIZE).reset_index(drop=True)

    if len(df) < 50:
        raise RuntimeError(
            f"فقط {len(df)} کندل دریافت شد؛ برای SMA50 حداقل 50 کندل لازم است."
        )

    return df
