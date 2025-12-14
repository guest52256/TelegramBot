import json
import os
import gspread
from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from google.oauth2.service_account import Credentials

# ================= CONFIG =================
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 7365077848   # 🔴 اپنا Telegram ID یہاں لگائیں
SHEET_NAME = "telegram_users"

# ================= GOOGLE SHEET =================
def get_sheet():
    creds_dict = json.loads(os.environ["CREDS"])
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def user_exists(sheet, user_id):
    ids = sheet.col_values(3)  # User ID column
    return str(user_id) in ids

def save_user(user):
    sheet = get_sheet()
    if user_exists(sheet, user.id):
        return
    sheet.append_row([
        user.full_name,
        f"@{user.username}" if user.username else "N/A",
        user.id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

# ================= KEYBOARDS =================
reply_keyboard = ReplyKeyboardMarkup(
    [["📄 View Users"]],
    resize_keyboard=True
)

def inline_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📅 Show Date", callback_data="show_date"),
                InlineKeyboardButton("⏰ Show Time", callback_data="show_time")
            ]
        ]
    )

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)

    now = datetime.now()

    text = (
        "✅ You are registered\n\n"
        f"👤 Name: {user.full_name}\n"
        f"🔹 Username: @{user.username if user.username else 'N/A'}\n"
        f"🆔 User ID: {user.id}\n"
        f"📆 Day: {now.strftime('%A')}"
    )

    await update.message.reply_text(
        text,
        reply_markup=inline_buttons()
    )

# ================= INLINE BUTTON HANDLER =================
async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    now = datetime.now()

    if query.data == "show_date":
        await query.message.reply_text(
            f"📅 Current Date:\n{now.strftime('%Y-%m-%d')}"
        )

    elif query.data == "show_time":
        await query.message.reply_text(
            f"⏰ Current Time:\n{now.strftime('%H:%M:%S')}"
        )

# ================= ADMIN VIEW =================
async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Access denied")
        return

    sheet = get_sheet()
    rows = sheet.get_all_values()[1:]  # skip header

    if not rows:
        await update.message.reply_text("No users found")
        return

    text = "📄 Registered Users:\n\n"
    for r in rows:
        text += (
            f"👤 {r[0]}\n"
            f"🔹 {r[1]}\n"
            f"🆔 {r[2]}\n"
            f"📅 {r[3]}\n\n"
        )

    await update.message.reply_text(text[:4000])

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(inline_handler))
    app.add_handler(MessageHandler(filters.Regex("📄 View Users"), view_users))

    app.run_polling()

if __name__ == "__main__":
    main()
