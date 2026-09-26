"""تنظیمات ربات تحلیل بازار ایران."""

# نام فارسی نمایشی -> کد رسمی دارایی در Servix
SYMBOLS = {
    "دلار": "USD_RLS",
    "یورو": "EUR_RLS",
    "درهم": "AED_RLS",
    "طلای ۱۸ عیار": "GOLD_18_RLS",
    "طلای ۲۴ عیار": "GOLD_24_RLS",
    "مثقال طلا": "GOLD_MESGHAL_RLS",
    "سکه امامی": "SEKKEH_RLS",
    "سکه بهار آزادی": "BAHAR_RLS",
    "بیت‌کوین": "BTC_RLS",
    "اتریوم": "ETH_RLS",
    "تتر": "USDT_RLS",
}

INTERVAL = "1h"
OUTPUT_SIZE = 100
HISTORY_DAYS = 7
DB_PATH = "market_history.db"
SERVIX_BASE_URL = "https://servix.cc/api/v1"
