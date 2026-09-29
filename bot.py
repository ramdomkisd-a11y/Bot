import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]

MAX_DATA = 100


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("data", [])

    await update.message.reply_text(
        "🤖 Bot Status Email aktif!\n\n"
        "Kirim data dengan format:\n"
        "email|status\n\n"
        "Contoh:\n"
        "contoh@gmail.com|good\n\n"
        "Status:\n"
        "good\n"
        "verify\n"
        "captcha\n"
        "disabled\n\n"
        "Perintah:\n"
        "/result - lihat jumlah status\n"
        "/list - lihat semua data\n"
        "/reset - hapus semua data"
    )


async def add_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "|" not in text:
        return

    email, status = text.split("|", 1)
    email = email.strip()
    status = status.strip().lower()

    allowed = {"good", "verify", "captcha", "disabled"}

    if not email or status not in allowed:
        await update.message.reply_text(
            "Format salah.\n"
            "Gunakan: email|good"
        )
        return

    data = context.user_data.setdefault("data", [])

    if len(data) >= MAX_DATA:
        await update.message.reply_text(
            f"Data sudah mencapai batas {MAX_DATA}."
        )
        return

    data.append({
        "email": email,
        "status": status
    })

    await update.message.reply_text(
        f"✅ Tersimpan\n"
        f"Email: {email}\n"
        f"Status: {status}"
    )


async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("data", [])

    counts = {
        "good": 0,
        "verify": 0,
        "captcha": 0,
        "disabled": 0
    }

    for item in data:
        if item["status"] in counts:
            counts[item["status"]] += 1

    await update.message.reply_text(
        f"📊 HASIL\n\n"
        f"Total: {len(data)}\n"
        f"Good: {counts['good']}\n"
        f"Verify: {counts['verify']}\n"
        f"Captcha: {counts['captcha']}\n"
        f"Disabled: {counts['disabled']}"
    )


async def list_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("data", [])

    if not data:
        await update.message.reply_text("📭 Belum ada data.")
        return

    lines = ["📋 DAFTAR DATA\n"]

    for i, item in enumerate(data, start=1):
        lines.append(
            f"{i}. {item['email']} | {item['status']}"
        )

    await update.message.reply_text("\n".join(lines))


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["data"] = []

    await update.message.reply_text(
        "🗑️ Semua data sudah dihapus."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("result", result))
    app.add_handler(CommandHandler("list", list_data))
    app.add_handler(CommandHandler("reset", reset))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            add_data
        )
    )

    print("Bot aktif...")
    app.run_polling()


if __name__ == "__main__":
    main()
