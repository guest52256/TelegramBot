import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")
DATA_FILE = "users.txt"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Commands:\n"
        "/add - Add username\n"
        "/view - View usernames\n"
        "/delete - Delete username"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "add"
    await update.message.reply_text("✍️ Send username to save:")

async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(DATA_FILE):
        await update.message.reply_text("📂 No data found.")
        return

    with open(DATA_FILE, "r") as f:
        data = f.read()

    await update.message.reply_text(
        "📋 Saved Usernames:\n\n" + (data if data else "Empty")
    )

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "delete"
    await update.message.reply_text("❌ Send username to delete:")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    mode = context.user_data.get("mode")

    if not mode:
        return

    if mode == "add":
        with open(DATA_FILE, "a") as f:
            f.write(text + "\n")
        await update.message.reply_text(f"✅ Saved: {text}")

    elif mode == "delete":
        if not os.path.exists(DATA_FILE):
            await update.message.reply_text("⚠️ No file found.")
            return

        with open(DATA_FILE, "r") as f:
            lines = f.readlines()

        with open(DATA_FILE, "w") as f:
            for line in lines:
                if line.strip() != text:
                    f.write(line)

        await update.message.reply_text(f"🗑 Deleted: {text}")

    context.user_data["mode"] = None

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("view", view))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
