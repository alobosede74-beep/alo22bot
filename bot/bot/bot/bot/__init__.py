"""
Bot package for @alo22bot
"""

from .handlers import *
from .config import Config
from .utils import TextAnalyzer, PlagiarismChecker

__version__ = "1.0.0"
__all__ = ["start", "help_command", "wordcount_command", "plagiarism_command", 
           "stats_command", "about_command", "handle_text", "button_callback",
           "error_handler", "Config", "TextAnalyzer", "PlagiarismChecker"]
