import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonCommands
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]
MAX_DATA = 100


def menu_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Hasil", callback_data="result"),
            InlineKeyboardButton("📋 Daftar", callback_data="list"),
        ],
        [
            InlineKeyboardButton("🗑️ Reset", callback_data="reset"),
            InlineKeyboardButton("ℹ️ Bantuan", callback_data="help"),
        ],
    ])


def result_text(data):
    counts = {
        "good": 0,
        "verify": 0,
        "captcha": 0,
        "disabled": 0,
    }

    for item in data:
        if item["status"] in counts:
            counts[item["status"]] += 1

    return (
        "╭━━━━━━━━━━━━━━━━╮\n"
        "      📊 *HASIL DATA*\n"
        "╰━━━━━━━━━━━━━━━━╯\n\n"
        f"📦 Total      : *{len(data)}*\n"
        f"🟢 Good       : *{counts['good']}*\n"
        f"🟡 Verify     : *{counts['verify']}*\n"
        f"🟠 Captcha    : *{counts['captcha']}*\n"
        f"🔴 Disabled   : *{counts['disabled']}*"
    )


async def post_init(application):
    # Mengatur daftar perintah bot
    await application.bot.set_my_commands([
        ("start", "🏠 Menu utama"),
        ("result", "📊 Lihat hasil"),
        ("list", "📋 Lihat daftar"),
        ("reset", "🗑️ Reset data"),
        ("help", "ℹ️ Bantuan"),
    ])
    # Mengaktifkan Tombol Menu warna biru di pojok kiri bawah
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("data", [])

    await update.message.reply_text(
        "╭━━━━━━━━━━━━━━━━╮\n"
        "    🤖 *STATUS EMAIL BOT*\n"
        "╰━━━━━━━━━━━━━━━━╯\n\n"
        "Bot siap digunakan! 🚀\n\n"
        "📌 Kirim data dengan format:\n"
        "`email|status`\n\n"
        "Contoh:\n"
        "`contoh@gmail.com|good`\n\n"
        "Gunakan tombol di bawah atau menu Telegram.",
        parse_mode="Markdown",
        reply_markup=menu_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "╭━━━━━━━━━━━━━━━━╮\n"
        "       ℹ️ *BANTUAN*\n"
        "╰━━━━━━━━━━━━━━━━╯\n\n"
        "📌 Format:\n"
        "`email|status`\n\n"
        "Status yang tersedia:\n"
        "🟢 good\n"
        "🟡 verify\n"
        "🟠 captcha\n"
        "🔴 disabled\n\n"
        "Contoh:\n"
        "`contoh@gmail.com|good`",
        parse_mode="Markdown",
        reply_markup=menu_keyboard(),
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
            "❌ *Format salah!*\n\n"
            "Gunakan:\n"
            "`email|good`\n"
            "`email|verify`\n"
            "`email|captcha`\n"
            "`email|disabled`",
            parse_mode="Markdown",
        )
        return

    data = context.user_data.setdefault("data", [])

    if len(data) >= MAX_DATA:
        await update.message.reply_text(
            f"⚠️ Batas data sudah mencapai *{MAX_DATA}*.",
            parse_mode="Markdown",
        )
        return

    data.append({
        "email": email,
        "status": status,
    })

    icons = {
        "good": "🟢",
        "verify": "🟡",
        "captcha": "🟠",
        "disabled": "🔴",
    }

    await update.message.reply_text(
        "╭━━━━━━━━━━━━━━━━╮\n"
        "       ✅ *TERSIMPAN*\n"
        "╰━━━━━━━━━━━━━━━━╯\n\n"
        f"📧 Email: `{email}`\n"
        f"{icons[status]} Status: *{status.upper()}*\n\n"
        f"📦 Total data: *{len(data)}*",
        parse_mode="Markdown",
        reply_markup=menu_keyboard(),
    )


async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("data", [])

    await update.message.reply_text(
        result_text(data),
        parse_mode="Markdown",
        reply_markup=menu_keyboard(),
    )


async def list_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("data", [])

    if not data:
        await update.message.reply_text(
            "📭 *Belum ada data.*",
            parse_mode="Markdown",
            reply_markup=menu_keyboard(),
        )
        return

    icons = {
        "good": "🟢",
        "verify": "🟡",
        "captcha": "🟠",
        "disabled": "🔴",
    }

    lines = [
        "╭━━━━━━━━━━━━━━━━╮",
        "      📋 *DAFTAR DATA*",
        "╰━━━━━━━━━━━━━━━━╯",
        "",
    ]

    for i, item in enumerate(data, start=1):
        lines.append(
            f"{i}. {icons[item['status']]} "
            f"`{item['email']}` — *{item['status']}*"
        )

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=menu_keyboard(),
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Ya, hapus",
                callback_data="confirm_reset"
            ),
            InlineKeyboardButton(
                "❌ Batal",
                callback_data="cancel_reset"
            ),
        ]
    ])

    await update.message.reply_text(
        "⚠️ *KONFIRMASI RESET*\n\n"
        "Semua data yang tersimpan akan dihapus.\n\n"
        "Yakin ingin melanjutkan?",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = context.user_data.get("data", [])

    if query.data == "result":
        await query.edit_message_text(
            result_text(data),
            parse_mode="Markdown",
            reply_markup=menu_keyboard(),
        )

    elif query.data == "list":
        if not data:
            await query.edit_message_text(
                "📭 *Belum ada data.*",
                parse_mode="Markdown",
                reply_markup=menu_keyboard(),
            )
            return

        icons = {
            "good": "🟢",
            "verify": "🟡",
            "captcha": "🟠",
            "disabled": "🔴",
        }

        lines = [
            "╭━━━━━━━━━━━━━━━━╮",
            "      📋 *DAFTAR DATA*",
            "╰━━━━━━━━━━━━━━━━╯",
            "",
        ]

        for i, item in enumerate(data, start=1):
            lines.append(
                f"{i}. {icons[item['status']]} "
                f"`{item['email']}` — *{item['status']}*"
            )

        await query.edit_message_text(
            "\n".join(lines),
            parse_mode="Markdown",
            reply_markup=menu_keyboard(),
        )

    elif query.data == "reset":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Ya, hapus",
                    callback_data="confirm_reset"
                ),
                InlineKeyboardButton(
                    "❌ Batal",
                    callback_data="cancel_reset"
                ),
            ]
        ])

        await query.edit_message_text(
            "⚠️ *KONFIRMASI RESET*\n\n"
            "Semua data akan dihapus.\n\n"
            "Yakin ingin melanjutkan?",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

    elif query.data == "confirm_reset":
        context.user_data["data"] = []

        await query.edit_message_text(
            "🗑️ *DATA DIHAPUS*\n\n"
            "Semua data sudah berhasil dihapus.",
            parse_mode="Markdown",
            reply_markup=menu_keyboard(),
        )

    elif query.data == "cancel_reset":
        await query.edit_message_text(
            "↩️ Reset dibatalkan.",
            reply_markup=menu_keyboard(),
        )

    elif query.data == "help":
        await query.edit_message_text(
            "╭━━━━━━━━━━━━━━━━╮\n"
            "       ℹ️ *BANTUAN*\n"
            "╰━━━━━━━━━━━━━━━━╯\n\n"
            "📌 Format:\n"
            "`email|status`\n\n"
            "🟢 good\n"
            "🟡 verify\n"
            "🟠 captcha\n"
            "🔴 disabled\n\n"
            "Contoh:\n"
            "`contoh@gmail.com|good`",
            parse_mode="Markdown",
            reply_markup=menu_keyboard(),
        )


def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("result", result))
    app.add_handler(CommandHandler("list", list_data))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CallbackQueryHandler(button_handler))

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
