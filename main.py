"""
@alo22bot - Main entry point for Railway deployment
A Telegram bot for word counting and plagiarism checking
"""

import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.handlers import (
    start, help_command, wordcount_command, plagiarism_command,
    stats_command, about_command, handle_text, button_callback, error_handler
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot with Railway configuration"""
    
    # Get token from environment variables
    BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not BOT_TOKEN:
        logger.error("No TELEGRAM_TOKEN found in environment variables!")
        raise ValueError("TELEGRAM_TOKEN is required")
    
    logger.info("🤖 @alo22bot is starting...")
    
    # Create application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("wc", wordcount_command))
    application.add_handler(CommandHandler("wordcount", wordcount_command))
    application.add_handler(CommandHandler("plag", plagiarism_command))
    application.add_handler(CommandHandler("plagiarism", plagiarism_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # Add message handler for text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot with long polling (best for Railway)
    logger.info("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
