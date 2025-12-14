import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "7833277818:AAGKzbWytWcjuikEfXGGWlvK1NMPqJovIUs"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ====== KEYBOARD ======
keyboard = ReplyKeyboardMarkup(
    [
        ["➕ Add Name"],
        ["📄 View Names"],
        ["❌ Delete All"]
    ],
    resize_keyboard=True
)

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome 👋\nOption select کریں:",
        reply_markup=keyboard
    )

# ====== ADD NAME ======
async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["adding"] = True
    await update.message.reply_text("اپنا نام لکھیں:")

# ====== HANDLE TEXT ======
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("adding"):
        name = update.message.text
        with open("users.txt", "a", encoding="utf-8") as f:
            f.write(name + "\n")

        context.user_data["adding"] = False
        await update.message.reply_text(
            f"✅ نام save ہو گیا:\n{name}",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            "Menu سے option select کریں 👇",
            reply_markup=keyboard
        )

# ====== VIEW NAMES ======
async def view_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("users.txt", "r", encoding="utf-8") as f:
            data = f.read().strip()

        if not data:
            data = "کوئی نام موجود نہیں"

    except FileNotFoundError:
        data = "کوئی data نہیں ملی"

    await update.message.reply_text(
        f"📄 Saved Names:\n\n{data}",
        reply_markup=keyboard
    )

# ====== DELETE ALL ======
async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    open("users.txt", "w").close()
    await update.message.reply_text(
        "❌ تمام names delete ہو گئے",
        reply_markup=keyboard
    )

# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("➕ Add Name"), add_name))
    app.add_handler(MessageHandler(filters.Regex("📄 View Names"), view_names))
    app.add_handler(MessageHandler(filters.Regex("❌ Delete All"), delete_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
