"""
ربات تلگرام تحلیل‌گر چند-بازاره (طلا، نقره، نفت، کریپتو و ارز)
------------------------------------------------------------
دستورات:
  /start    - خوش‌آمدگویی
  /markets  - نمایش دکمه‌های انتخاب بازار برای تحلیل
  /history <نام بازار>  - نمایش چند تحلیل اخیر ذخیره‌شده برای اون بازار

نحوه اجرا:
    1) pip install -r requirements.txt
    2) فایل .env.example رو کپی کنید به .env و مقادیرش رو پر کنید
    3) python bot.py
"""

import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from analysis import build_analysis_text, compute_indicators
from charts import build_chart_image
from config import SYMBOLS
from data import fetch_market_data
from database import get_recent_history, init_db, save_snapshot

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_symbols_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"analyze:{name}")]
        for name in SYMBOLS
    ]
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "سلام! به ربات تحلیل‌گر بازار خوش اومدید.\n"
        "برای دیدن لیست بازارها و دریافت تحلیل، دستور /markets رو بفرستید."
    )


async def markets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "یکی از بازارهای زیر رو برای دریافت تحلیل انتخاب کنید:",
        reply_markup=build_symbols_keyboard(),
    )


async def handle_symbol_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    symbol_name = query.data.split(":", 1)[1]
    symbol_code = SYMBOLS.get(symbol_name)
    if not symbol_code:
        await query.edit_message_text("بازار شناخته نشد.")
        return

    await query.edit_message_text(f"در حال دریافت و تحلیل {symbol_name}... ⏳")

    try:
        df = fetch_market_data(symbol_code)
        snap = compute_indicators(df)
        save_snapshot(symbol_name, snap)

        analysis_text = build_analysis_text(symbol_name, snap)
        chart_buffer = build_chart_image(df, symbol_name)

        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=chart_buffer,
            caption=analysis_text,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("خطا در دریافت/تحلیل %s", symbol_name)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"خطا در دریافت داده {symbol_name}: {exc}",
        )


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        available = "، ".join(SYMBOLS.keys())
        await update.message.reply_text(
            f"لطفاً اسم بازار رو هم بنویسید. مثال: /history طلا\n"
            f"بازارهای موجود: {available}"
        )
        return

    symbol_name = " ".join(context.args)
    if symbol_name not in SYMBOLS:
        await update.message.reply_text("این بازار شناخته نشد.")
        return

    rows = get_recent_history(symbol_name, limit=5)
    if not rows:
        await update.message.reply_text(f"هنوز تاریخچه‌ای برای {symbol_name} ذخیره نشده.")
        return

    lines = [f"🕓 آخرین تحلیل‌های ذخیره‌شده برای {symbol_name}:\n"]
    for requested_at, price, rsi in rows:
        lines.append(f"{requested_at} — قیمت: {price:.2f} | RSI: {rsi:.1f}")

    await update.message.reply_text("\n".join(lines))


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("لطفاً TELEGRAM_BOT_TOKEN رو در فایل .env تنظیم کنید.")

    init_db()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("markets", markets))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CallbackQueryHandler(handle_symbol_choice, pattern=r"^analyze:"))

    logger.info("ربات در حال اجراست...")
    application.run_polling()


if __name__ == "__main__":
    main()
