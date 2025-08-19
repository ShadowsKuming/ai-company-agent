"""
Display and console configuration
"""

import os
import sys
import platform

class DisplayConfig:
    """Centralized display configuration"""
    
    def __init__(self):
        self.platform = platform.system()
        self.encoding = sys.stdout.encoding
        self.is_windows_gbk = (
            self.platform == 'Windows' and 
            self.encoding.lower() in ['gbk', 'cp936']
        )
        
        # Load from environment or config file
        self.use_ascii_only = (
            os.getenv('USE_ASCII_ONLY', '').lower() == 'true' or
            self.is_windows_gbk
        )
    
    @property
    def emoji_map(self):
        """Emoji to ASCII mapping"""
        return {
            '✅': '[OK]',
            '❌': '[FAIL]', 
            '⚠️': '[WARN]',
            '🚀': '[START]',
            '📊': '[DATA]',
            '💰': '[MONEY]',
            '👤': '[USER]',
            '💻': '[TECH]',
            '📈': '[UP]',
            '🤖': '[AI]',
            '📄': '[DOC]',
            '🎯': '[TARGET]',
            '📁': '[FOLDER]',
            '💡': '[IDEA]',
            '🔧': '[TOOL]',
            '⏰': '[TIME]',
            '🎉': '[SUCCESS]',
            '📋': '[LIST]',
            '💥': '[ERROR]',
            '🔍': '[SEARCH]',
        }
    
    def safe_text(self, text: str) -> str:
        """Convert text to safe display format"""
        if not self.use_ascii_only:
            return text
            
        safe_text = text
        for emoji, replacement in self.emoji_map.items():
            safe_text = safe_text.replace(emoji, replacement)
        return safe_text

# Global instance
display_config = DisplayConfig()

def safe_format(text: str) -> str:
    """Quick function to format text safely"""
    return display_config.safe_text(text)