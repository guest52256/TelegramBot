import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Get token from environment (SAFE)
TOKEN = os.getenv("TOKEN")

DATA_FILE = "users.txt"

def start(update, context):
    update.message.reply_text(
        "👋 Welcome!\n\n"
        "Commands:\n"
        "/add - Add username\n"
        "/view - View usernames\n"
        "/delete - Delete username"
    )

def add(update, context):
    update.message.reply_text("✍️ Send username to save:")
    context.user_data['mode'] = 'add'

def view(update, context):
    if not os.path.exists(DATA_FILE):
        update.message.reply_text("📂 No data found.")
        return

    with open(DATA_FILE, "r") as f:
        data = f.read()

    update.message.reply_text(
        "📋 Saved Usernames:\n\n" + (data if data else "Empty")
    )

def delete(update, context):
    update.message.reply_text("❌ Send username to delete:")
    context.user_data['mode'] = 'delete'

def text_handler(update, context):
    text = update.message.text.strip()
    mode = context.user_data.get('mode')

    if mode == 'add':
        with open(DATA_FILE, "a") as f:
            f.write(text + "\n")
        update.message.reply_text(f"✅ Saved: {text}")

    elif mode == 'delete':
        if not os.path.exists(DATA_FILE):
            update.message.reply_text("⚠️ No file found.")
            return

        with open(DATA_FILE, "r") as f:
            lines = f.readlines()

        with open(DATA_FILE, "w") as f:
            for line in lines:
                if line.strip() != text:
                    f.write(line)

        update.message.reply_text(f"🗑 Deleted: {text}")

    context.user_data['mode'] = None

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("view", view))
    dp.add_handler(CommandHandler("delete", delete))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()