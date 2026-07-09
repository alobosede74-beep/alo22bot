"""
Command handlers for @alo22bot
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils import TextAnalyzer, PlagiarismChecker
from bot.config import Config

logger = logging.getLogger(__name__)

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

**Example:**
`/wc The quick brown fox jumps over the lazy dog`

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

**Support:**
For issues or suggestions, contact the bot creator.
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
    if len(text) > Config.MAX_TEXT_LENGTH:
        text = text[:Config.MAX_TEXT_LENGTH]
        await update.message.reply_text("⚠️ Text truncated to 5000 characters for analysis.")
    
    # Calculate statistics
    stats = TextAnalyzer.count_words(text)
    
    # Format response
    response = TextAnalyzer.format_word_count_result(stats)
    
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
    if len(text) > Config.PLAGIARISM_MAX_WORDS * 6:  # Approximate character limit
        await update.message.reply_text(
            f"⚠️ Text is too long. Please limit to {Config.PLAGIARISM_MAX_WORDS} words."
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("🔍 Analyzing text for plagiarism... Please wait ⏳")
    
    try:
        # Check plagiarism
        result = PlagiarismChecker.check(text)
        
        # Format response
        response = PlagiarismChecker.format_plagiarism_result(result)
        
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

**Usage Stats:**
• Total Users: Tracking
• Commands Processed: Tracking

**Links:**
• Repository: GitHub
• Created: 2024
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

**Why This Bot:**
✅ Free to use
✅ No registration required
✅ Privacy-focused
✅ Fast and reliable

**Limitations:**
• Plagiarism check: ~500 words max (API limit)
• Results are approximate
• Use professional tools for critical work

**Support:**
For issues or suggestions, contact the developer.

Made with ❤️ for the Telegram community
    """
    await update.message.reply_text(about_text, parse_mode='Markdown')

# ==================== MESSAGE HANDLER ====================

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages (auto word count)."""
    text = update.message.text
    
    # Ignore commands
    if not text or text.startswith('/'):
        return
    
    # Analyze text
    stats = TextAnalyzer.count_words(text)
    
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

# ==================== CALLBACK HANDLER ====================

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
            result = PlagiarismChecker.check(text)
            response = PlagiarismChecker.format_plagiarism_result(result)
            
            await query.edit_message_text(response, parse_mode='Markdown')
        
        elif data.startswith("stats_"):
            # Extract text and show detailed stats
            text = data.replace("stats_", "")
            if not text:
                await query.edit_message_text("⚠️ No text found for statistics.")
                return
            
            stats = TextAnalyzer.count_words(text)
            response = TextAnalyzer.format_word_count_result(stats)
            
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

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user."""
    logger.error(f"Update {update} caused error: {context.error}")
    
    # Send message to user
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Sorry, an error occurred while processing your request.\n"
            "Please try again later or contact support."
        )
