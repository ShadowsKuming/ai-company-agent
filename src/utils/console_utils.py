"""
Console utilities for cross-platform Unicode handling
"""

import sys
import platform

# Check if we're on Windows with GBK encoding issues
WINDOWS_GBK = (
    platform.system() == 'Windows' and 
    sys.stdout.encoding.lower() in ['gbk', 'cp936']
)

def safe_print(*args, **kwargs):
    """
    Unicode-safe print function that works on all platforms
    Automatically replaces Unicode emojis with ASCII on Windows GBK
    """
    if WINDOWS_GBK and args:
        # Unicode emoji replacements
        replacements = {
            '✅': '[OK]',
            '❌': '[FAIL]', 
            '⚠️': '[WARN]',
            '🚀': '[ROCKET]',
            '📊': '[CHART]',
            '💰': '[MONEY]',
            '👤': '[PERSON]',
            '💻': '[COMPUTER]',
            '📈': '[TRENDING]',
            '🤖': '[ROBOT]',
            '📄': '[PAGE]',
            '🎯': '[TARGET]',
            '📁': '[FOLDER]',
            '💡': '[BULB]',
            '🔧': '[WRENCH]',
            '⏰': '[CLOCK]',
            '🎉': '[PARTY]',
            '📋': '[CLIPBOARD]',
            '💥': '[BOOM]',
            '🔍': '[SEARCH]',
        }
        
        # Convert all args to strings and replace emojis
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_str = arg
                for emoji, replacement in replacements.items():
                    safe_str = safe_str.replace(emoji, replacement)
                safe_args.append(safe_str)
            else:
                safe_args.append(arg)
        
        print(*safe_args, **kwargs)
    else:
        # Normal print on other platforms
        print(*args, **kwargs)

# Aliases for convenience
console_print = safe_print
log = safe_print