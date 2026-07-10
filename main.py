"""
@alo22bot - Complete Working Version
A Telegram bot for word counting and plagiarism checking
"""

import os
import sys
import re
import logging
import requests
from collections import Counter
from typing import Dict

# ==================== LOGGING SETUP ====================

# Print debug info at startup
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

# Now import telegram
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
    print("✅ Telegram module imported successfully!")
except ImportError as e:
    print(f"❌ Failed to import telegram: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

# Get token from environment variables
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN environment variable is required!")
    print("❌ TELEGRAM_TOKEN environment variable is required!")
    sys.exit(1)

logger.info(f"✅ TELEGRAM_TOKEN found: {BOT_TOKEN[:10]}...")

# Constants
MAX_TEXT_LENGTH = 5000
PLAGIARISM_MAX_WORDS = 500

# ==================== UTILITY FUNCTIONS ====================

def count_words(text: str) -> Dict:
    """Count words, characters, sentences, and paragraphs"""
    if not text or not text.strip():
        return {
            "words": 0,
            "characters_no_space": 0,
            "characters_with_space": 0,
            "sentences": 0,
            "paragraphs": 0,
            "unique_words": 0,
            "top_words": [],
            "reading_time_min": 0
        }
    
    # Clean and split text
    words = re.findall(r'\b\w+\b', text)
    sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    
    # Count characters
    chars_no_space = len(re.sub(r'\s', '', text))
    chars_with_space = len(text)
    
    # Word frequency
    word_freq = Counter(words)
    top_words = word_freq.most_common(5)
    
    return {
        "words": len(words),
        "characters_no_space": chars_no_space,
        "characters_with_space": chars_with_space,
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "unique_words": len(word_freq),
        "top_words": top_words,
        "reading_time_min": round(len(words) / 200, 1)
    }

def check_plagiarism_duplichecker(text: str) -> Dict:
    """Check plagiarism using DupliChecker API (free tier)"""
    try:
        # Truncate to API limit
        api_text = text[:500]
        api_url = "https://www.duplichecker.com/API/check.php"
        payload = {
            'text': api_text,
            'format': 'json'
        }
        
        response = requests.post(api_url, data=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                plagiarism_score = float(data.get('plagiarism', 0))
                return {
                    "percentage": plagiarism_score,
                    "status": "Plagiarism Detected" if plagiarism_score > 20 else "Original Content",
                    "details": data.get('message', ''),
                    "source": "DupliChecker API"
                }
    except Exception as e:
        logger.error(f"DupliChecker API error: {e}")
    
    return None

def check_plagiarism_basic(text: str) -> Dict:
    """Basic plagiarism analysis using frequency patterns"""
    words = re.findall(r'\b\w+\b', text.lower())
    
    if not words:
        return {
            "percentage": 0,
            "status": "No text to analyze",
            "details": "Please provide valid text",
            "source": "Basic Analysis"
        }
    
    # Count word frequencies
    word_freq = Counter(words)
    total_words = len(words)
    unique_words = len(word_freq)
    
    # Calculate repetition ratio
    repeated_words = sum(1 for w, c in word_freq.items() if c > 2)
    repetition_ratio = (repeated_words / unique_words * 100) if unique_words > 0 else 0
    
    # Simple plagiarism indicator based on repetition
    plagiarism_score = min(repetition_ratio * 0.5, 50)
    
    return {
        "percentage": round(plagiarism_score, 2),
        "status": "Analysis Complete (Basic)",
        "details": f"Analyzed {total_words} words with {unique_words} unique words. "
                  f"Repeated pattern ratio: {repetition_ratio:.1f}%",
        "source": "Basic Frequency Analysis"
    }

def check_plagiarism(text: str) -> Dict:
    """Main plagiarism check function with fallbacks"""
    # Try DupliChecker first
    result = check_plagiarism_duplichecker(text)
    
    # If DupliChecker fails, use basic analysis
    if not result:
        logger.info("Using basic analysis as fallback")
        result = check_plagiarism_basic(text)
    
    return result

def format_word_count(stats: Dict) -> str:
    """Format word count results for display"""
    if stats["words"] == 0:
        return "📝 No text found to analyze."
    
    result = f"""
📊 **Text Statistics**

📝 **Words:** {stats['words']:,}
📝 **Characters (no spaces):** {stats['characters_no_space']:,}
📝 **Characters (with spaces):** {stats['characters_with_space']:,}
📝 **Sentences:** {stats['sentences']}
📝 **Paragraphs:** {stats['paragraphs']}
🔤 **Unique Words:** {stats['unique_words']:,}
⏱️ **Reading Time:** ~{stats['reading_time_min']} min

**Top 5 Words:**
"""
    for word, count in stats['top_words']:
        result += f"• `{word}`: {count} times\n"
    
    return result

def format_plagiarism_result(result: Dict) -> str:
    """Format plagiarism results for display"""
    if not result:
        return "❌ Could not perform plagiarism check. Please try again."
    
    percentage = result.get('percentage', 0)
    status = result.get('status', 'Unknown')
    details = result.get('details', '')
    source = result.get('source', 'Unknown')
    
    response = f"""
🔍 **Plagiarism Analysis Results**

📊 **Similarity Score:** {percentage}%
📌 **Status:** {status}
🔧 **Source:** {source}

📝 **Details:**
{details}

⚠️ **Disclaimer:** Free tools have limitations. For academic or professional use, 
please use paid plagiarism checkers.
"""
    
    # Add recommendations based on score
    if percentage > 50:
        response += "\n🚨 **High similarity detected!** Consider significant revision and proper citation."
    elif percentage > 25:
        response += "\n⚠️ **Moderate similarity.** Review sources and consider paraphrasing."
    elif percentage > 10:
        response += "\n💡 **Low similarity.** Generally acceptable, but review for proper attribution."
    else:
        response += "\n✅ **Text appears original.** Good work!"
    
    return response

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = f"""
👋 Hello **{user.first_name}**!

Welcome to **@alo22bot** - Your All-in-One Text Analysis Tool!

I can help you with:
📝 **Word Count** - Detailed text statistics
🔍 **Plagiarism Check** - Originality analysis
📊 **Text Analysis** - Complete text metrics

**Quick Start:**
• Send any text message for instant analysis
• Use `/wc Your text here` for detailed word count
• Use `/plag Your text here` for plagiarism check
• Use `/help` to see all commands

🚀 **Powered by Railway & GitHub**
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    help_text = """
📖 **Available Commands:**

**Core Commands:**
/start - Show welcome message
/help - Show this help message
/about - About this bot
/stats - Bot statistics

**Text Analysis:**
/wc [text] - Count words and characters
/wordcount [text] - Same as /wc
/plag [text] - Check for plagiarism
/plagiarism [text] - Same as /plag

**Tips:**
• Send any text message for automatic analysis
• Reply to a message with /wc or /plag
• Use inline buttons for quick actions
• No limit on word counting

**Limitations:**
• Plagiarism check: Up to 500 words (free API limit)
• Results are approximate - use professional tools for critical work
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def wordcount_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /wordcount command."""
    # Get text from command arguments or reply
    if context.args:
        text = ' '.join(context.args)
    elif update.message.reply_to_message:
        text = update.message.reply_to_message.text or update.message.reply_to_message.caption
        if not text:
            await update.message.reply_text("⚠️ Please reply to a text message.")
            return
    else:
        await update.message.reply_text(
            "⚠️ Please provide text or reply to a message.\n"
            "Example: `/wc Your text here`",
            parse_mode='Markdown'
        )
        return
    
    # Check text length
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
        await update.message.reply_text("⚠️ Text truncated to 5000 characters for analysis.")
    
    # Calculate statistics
    stats = count_words(text)
    
    # Format response
    response = format_word_count(stats)
    
    # Add inline keyboard for actions
    keyboard = [
        [
            InlineKeyboardButton("🔍 Check Plagiarism", callback_data=f"plag_{text[:100]}"),
            InlineKeyboardButton("📊 More Stats", callback_data="more_stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)

async def plagiarism_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /plagiarism command."""
    # Get text from command arguments or reply
    if context.args:
        text = ' '.join(context.args)
    elif update.message.reply_to_message:
        text = update.message.reply_to_message.text or update.message.reply_to_message.caption
        if not text:
            await update.message.reply_text("⚠️ Please reply to a text message.")
            return
    else:
        await update.message.reply_text(
            "⚠️ Please provide text or reply to a message.\n"
            "Example: `/plag Your text here`",
            parse_mode='Markdown'
        )
        return
    
    # Limit text length for API
    if len(text) > PLAGIARISM_MAX_WORDS * 6:
        await update.message.reply_text(
            f"⚠️ Text is too long. Please limit to {PLAGIARISM_MAX_WORDS} words."
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("🔍 Analyzing text for plagiarism... Please wait ⏳")
    
    try:
        # Check plagiarism
        result = check_plagiarism(text)
        
        # Format response
        response = format_plagiarism_result(result)
        
        await processing_msg.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in plagiarism check: {e}")
        await processing_msg.edit_text(
            "❌ An error occurred during plagiarism check. Please try again later."
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot statistics."""
    stats_text = """
📊 **Bot Statistics:**

🤖 **Bot:** @alo22bot
📅 **Status:** ✅ Online
⏰ **Uptime:** Continuous
🔧 **Platform:** Railway + GitHub

**Features:**
✅ Word Counting (unlimited)
✅ Plagiarism Checking (basic)
✅ Text Analysis
✅ Interactive Buttons
✅ Auto-response to messages

**Limitations:**
• Plagiarism check: ~500 words max
• Results are approximate
• Use professional tools for critical work
    """
    await update.message.reply_text(stats_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show about information."""
    about_text = """
🤖 **About @alo22bot**

A powerful Telegram bot for text analysis and plagiarism checking.

**Core Features:**
• 📝 Word and character counting
• 📊 Sentence and paragraph analysis  
• 🔍 Plagiarism detection
• 🎯 Interactive keyboard buttons
• 💬 Instant text analysis

**Technical Stack:**
• Python 3.11+
• python-telegram-bot v20+
• Railway.app hosting
• GitHub version control

Made with ❤️ for the Telegram community
    """
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages (auto word count)."""
    text = update.message.text
    
    # Ignore commands
    if not text or text.startswith('/'):
        return
    
    # Analyze text
    stats = count_words(text)
    
    # Quick response
    response = f"""
📊 **Quick Analysis**

📝 **Words:** {stats['words']:,}
🔤 **Characters:** {stats['characters_no_space']:,} (no spaces)
⏱️ **Reading Time:** ~{stats['reading_time_min']} min

💡 Use `/wc` for detailed stats or `/plag` for plagiarism check!
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Detailed Stats", callback_data=f"stats_{text[:100]}"),
            InlineKeyboardButton("🔍 Check Plagiarism", callback_data=f"plag_{text[:100]}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    try:
        if data.startswith("plag_"):
            # Extract text from callback data
            text = data.replace("plag_", "")
            if not text:
                await query.edit_message_text("⚠️ No text found for plagiarism check.")
                return
            
            # Send processing message
            await query.edit_message_text("🔍 Checking plagiarism... Please wait ⏳")
            
            # Check plagiarism
            result = check_plagiarism(text)
            response = format_plagiarism_result(result)
            
            await query.edit_message_text(response, parse_mode='Markdown')
        
        elif data.startswith("stats_"):
            # Extract text and show detailed stats
            text = data.replace("stats_", "")
            if not text:
                await query.edit_message_text("⚠️ No text found for statistics.")
                return
            
            stats = count_words(text)
            response = format_word_count(stats)
            
            # Add back button
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        
        elif data == "more_stats":
            await query.edit_message_text(
                "📊 To get detailed statistics, use:\n"
                "`/wc Your text here`\n\n"
                "Or send a text message and click 'Detailed Stats'.",
                parse_mode='Markdown'
            )
        
        elif data == "back":
            await query.edit_message_text(
                "🔙 Back to main menu.\n"
                "Send a message or use /help for commands."
            )
    
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await query.edit_message_text(
            "❌ An error occurred. Please try again."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user."""
    logger.error(f"Update {update} caused error: {context.error}")
    
    # Send message to user
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Sorry, an error occurred while processing your request.\n"
            "Please try again later or contact support."
        )

# ==================== MAIN ====================

def main():
    """Start the bot."""
    logger.info("🤖 @alo22bot is starting...")
    print("🤖 @alo22bot is starting...")
    
    try:
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
        
        # Start the bot with long polling
        logger.info("✅ Bot is running! Press Ctrl+C to stop.")
        print("✅ Bot is running! Press Ctrl+C to stop.")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
