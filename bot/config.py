"""
Configuration file for @alo22bot
"""

import os

class Config:
    """Bot configuration settings"""
    
    # Bot token from environment variable
    BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    
    # Optional API keys (add your own if needed)
    DUPLICHECKER_KEY = os.environ.get("DUPLICHECKER_KEY", "")
    COPYLEAKS_KEY = os.environ.get("COPYLEAKS_KEY", "")
    
    # Rate limiting
    MAX_TEXT_LENGTH = 5000  # Maximum text length
    PLAGIARISM_MAX_WORDS = 500  # Free API limit
    
    # Command descriptions
    COMMANDS = {
        "start": "Welcome message",
        "help": "Show help",
        "wc": "Word count",
        "wordcount": "Word count",
        "plag": "Plagiarism check",
        "plagiarism": "Plagiarism check",
        "stats": "Bot statistics",
        "about": "About this bot"
    }
