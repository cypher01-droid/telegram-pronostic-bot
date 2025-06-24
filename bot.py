from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)
import json
import os

# File to store user data
DATA_FILE = "users.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

# States for ConversationHandler
VERIFY, EDIT = range(2)

PROMO_CODE = "AXEL1017"

# Load users
def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save users
def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["✅ Verify Inscription", "✏️ Edit Inscription"],
          ["❌ Remove Inscription", "📊 Request Prediction"]]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)

    await update.message.reply_text(
        f"""👋 *Welcome to AXEL1017 Bot!*

🎁 Use this promo code on any of the platforms to claim your bonus:
*AXEL1017*

📌 Supported Bookmakers:
- 1xBet
- Betwinner
- Melbet

Choose an option below 👇""",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# Start verification
async def verify_inscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Which platform did you register on? (1xBet / Betwinner / Melbet)")
    return VERIFY

# Save verified data
async def save_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    platform = update.message.text.strip().lower()
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username or "N/A"

    if platform not in ["1xbet", "betwinner", "melbet"]:
        await update.message.reply_text("❌ Invalid platform. Please type: 1xBet, Betwinner, or Melbet.")
        return VERIFY

    users = load_users()
    users[user_id] = {
        "username": username,
        "platform": platform,
        "promo_code": PROMO_CODE,
        "verified": True
    }
    save_users(users)

    await update.message.reply_text("✅ Registration verified! You can now request predictions.")
    return ConversationHandler.END

# Edit existing inscription
async def edit_inscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    users = load_users()
    if user_id not in users:
        await update.message.reply_text("❌ No existing registration found. Please verify first.")
        return ConversationHandler.END
    return await verify_inscription(update, context)

# Remove registration
async def remove_inscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    users = load_users()
    if user_id in users:
        del users[user_id]
        save_users(users)
        await update.message.reply_text("🗑️ Your registration has been removed.")
    else:
        await update.message.reply_text("⚠️ No registration found.")

# Handle prediction request
async def request_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    users = load_users()
    if user_id in users and users[user_id]["verified"]:
        await update.message.reply_text(
            "🔮 Here's your prediction:\n\n👉 *Today’s tip: 1xBet – Over 2.5 goals*\n\n(⚠️ This is a sample prediction)",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("🚫 Please verify your registration with our promo code first.")

# Cancel fallback
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.")
    return ConversationHandler.END

# Main function (NO bot.id access before polling!)
def main():
    application = ApplicationBuilder().token("7720597904:AAHxmsKU834O2O92DJimUkEgjpvnVq30pVA").build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^✅ Verify Inscription$"), verify_inscription),
            MessageHandler(filters.Regex("^✏️ Edit Inscription$"), edit_inscription),
        ],
        states={
            VERIFY: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_verification)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Regex("^❌ Remove Inscription$"), remove_inscription))
    application.add_handler(MessageHandler(filters.Regex("^📊 Request Prediction$"), request_prediction))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("✅ Bot has stopped.")

if __name__ == "__main__":
    main()
