import asyncio
import threading
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import current_app

class TelegramService:
    def __init__(self, token):
        self.token = token
        self.bot = Bot(token=token) if token else None

    async def _send_message_async(self, chat_id, text, reply_markup=None):
        if not self.bot: return
        try:
            await self.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode='HTML')
        except Exception as e:
            print(f"TELEGRAM ERROR: {str(e)}")

    def send_notification(self, chat_id, text, reply_markup=None):
        if not self.token: return
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._send_message_async(chat_id, text, reply_markup))
        loop.close()

    def notify_upload_success(self, chat_id, file_name, file_size, share_url, expiry=None):
        text = f"<b>📁 File Shared Successfully</b>\n\n" \
               f"<b>File:</b> {file_name}\n" \
               f"<b>Size:</b> {file_size}\n" \
               f"<b>Expiry:</b> {expiry if expiry else 'Never'}\n\n" \
               f"Your secure link is ready!"
        
        keyboard = [[InlineKeyboardButton("📥 Open Download Page", url=share_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        threading.Thread(target=self.send_notification, args=(chat_id, text, reply_markup)).start()

    # --- Bot Command Handlers ---
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_html(
            "<b>👋 Welcome to CloudShare Pro Bot!</b>\n\n"
            "I'm your AI-powered assistant. You can ask me questions about your files or how to use the platform.\n\n"
            "<b>Commands:</b>\n"
            "/link [USER_ID] - Link your account\n"
            "/myfiles - List your recent files\n"
            "/stats - View your sharing stats\n"
            "/help - Get AI assistance"
        )

    # --- AI Message Handler ("Training") ---
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text.lower()
        
        # Smart FAQ Logic (AI Training Simulation)
        responses = {
            "upload": "To upload files, simply go to the CloudShare Pro homepage and drag your files into the blue box! You can also set passwords and expiry dates in 'Advanced Options'.",
            "size": "On the free plan, you can share files up to 2GB. Upgrade to Pro for larger limits!",
            "password": "Yes! You can password-protect any share. Just click 'Show Options' on the upload screen before selecting your files.",
            "expiry": "Files can be set to expire after 24 hours, 7 days, or 30 days. You can also set them to never expire.",
            "delete": "You can manage and delete your files anytime from your personal Dashboard on the website.",
            "p2p": "P2P transfer is a direct device-to-device connection. It's the fastest way to share files without them ever touching our servers!"
        }

        # Check for keywords
        found_response = False
        for key, response in responses.items():
            if key in user_text:
                await update.message.reply_html(f"<b>🤖 CloudShare AI:</b>\n\n{response}")
                found_response = True
                break
        
        if not found_response:
            await update.message.reply_html(
                "<b>🤖 CloudShare AI:</b>\n\n"
                "I'm not sure about that one yet. You can ask me about <b>uploads, file sizes, passwords, or P2P transfers</b>!\n\n"
                "Or type /help to see all available commands."
            )

    async def link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Please provide your User ID. Example: /link 123")
            return
        user_id = context.args[0]
        await update.message.reply_html(f"<b>✅ Success!</b> Your Telegram account is now linked to User ID: <code>{user_id}</code>.")

    def run_bot(self):
        if not self.token: return
        application = ApplicationBuilder().token(self.token).build()
        
        # Commands
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.start_command))
        application.add_handler(CommandHandler("link", self.link_command))
        
        # "AI Training" Message Handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("CloudShare AI Bot is polling...")
        application.run_polling()

def get_telegram_service():
    return TelegramService(current_app.config.get('TELEGRAM_BOT_TOKEN'))
