import json
import gspread
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google.oauth2.service_account import Credentials
import os

# ===== BOT CONFIG =====
TOKEN = os.environ.get("TOKEN")  # Render ENV
ADMIN_ID = 7365077848   # اپنا Telegram ID

# ===== GOOGLE SHEET =====
def get_sheet():
    creds_dict = json.loads(os.environ["CREDS"])
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open("telegram_users").sheet1

def user_exists(sheet, user_id):
    ids = sheet.col_values(3)  # 3rd column = User ID
    return str(user_id) in ids

def save_user(user):
    sheet = get_sheet()
    if user_exists(sheet, user.id):
        return
    sheet.append_row([
        user.full_name,
        f"@{user.username}" if user.username else "N/A",
        user.id,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ])

# ===== KEYBOARD =====
keyboard = ReplyKeyboardMarkup(
    [["📄 View Users"]],
    resize_keyboard=True
)

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    day_str = now.strftime("%A")

    message = (
        f"✅ آپ register ہو گئے ہیں\n\n"
        f"👤 Name: {user.full_name}\n"
        f"🔹 Username: @{user.username if user.username else 'N/A'}\n"
        f"🆔 User ID: {user.id}\n"
        f"📅 Date: {date_str}\n"
        f"⏰ Time: {time_str}\n"
        f"📆 Day: {day_str}"
    )

    await update.message.reply_text(message, reply_markup=keyboard)

# ===== ADMIN VIEW =====
async def view_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Access denied")
        return

    sheet = get_sheet()
    rows = sheet.get_all_values()[1:]  # skip headers

    if not rows:
        await update.message.reply_text("کوئی data نہیں")
        return

    text = "📄 Registered Users:\n\n"
    for r in rows:
        text += f"👤 {r[0]}\n"
        text += f"🔹 {r[1]}\n"
        text += f"🆔 {r[2]}\n"
        text += f"📅 Registered: {r[3]}\n\n"

    await update.message.reply_text(text[:4000])  # Telegram limit

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("📄 View Users"), view_users))
    app.run_polling()

if __name__ == "__main__":
    main()