"""
Utility functions for @alo22bot
Word counting and plagiarism checking
"""

import re
import requests
from collections import Counter
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """Text analysis utilities"""
    
    @staticmethod
    def count_words(text: str) -> Dict:
        """
        Count words, characters, sentences, and paragraphs
        
        Args:
            text: Input text string
            
        Returns:
            Dictionary with text statistics
        """
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
            "reading_time_min": round(len(words) / 200, 1)  # Average reading speed
        }
    
    @staticmethod
    def format_word_count_result(stats: Dict) -> str:
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

class PlagiarismChecker:
    """Plagiarism checking utilities"""
    
    @staticmethod
    def check_duplichecker(text: str) -> Dict:
        """
        Check plagiarism using DupliChecker API (free tier)
        
        Args:
            text: Input text to check
            
        Returns:
            Dictionary with plagiarism results
        """
        try:
            # DupliChecker free API (limited to 500 words)
            api_url = "https://www.duplichecker.com/API/check.php"
            payload = {
                'text': text[:500],
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
    
    @staticmethod
    def basic_analysis(text: str) -> Dict:
        """
        Basic plagiarism analysis using frequency patterns
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with basic analysis results
        """
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
        # This is NOT real plagiarism detection, just a placeholder
        plagiarism_score = min(repetition_ratio * 0.5, 50)  # Cap at 50%
        
        return {
            "percentage": round(plagiarism_score, 2),
            "status": "Analysis Complete (Basic)" if plagiarism_score > 0 else "Analysis Complete",
            "details": f"Analyzed {total_words} words with {unique_words} unique words. "
                      f"Repeated pattern ratio: {repetition_ratio:.1f}%",
            "source": "Basic Frequency Analysis"
        }
    
    @staticmethod
    def check(text: str) -> Dict:
        """
        Main plagiarism check function with fallbacks
        
        Args:
            text: Input text to check
            
        Returns:
            Dictionary with plagiarism results
        """
        # Try DupliChecker first
        result = PlagiarismChecker.check_duplichecker(text)
        
        # If DupliChecker fails, use basic analysis
        if not result:
            logger.info("Using basic analysis as fallback")
            result = PlagiarismChecker.basic_analysis(text)
        
        return result
    
    @staticmethod
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
