import logging
import sys
from app.core.config import settings

class EmojiLogFormatter(logging.Formatter):
    """Custom formatter to add emojis based on log level."""
    
    EMOJIS = {
        logging.DEBUG: "🐛",
        logging.INFO: "💡",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }
    
    def format(self, record):
        emoji = self.EMOJIS.get(record.levelno, "")
        original_msg = str(record.msg)
        # Avoid prepending emoji multiple times
        if not any(original_msg.startswith(e) for e in self.EMOJIS.values()):
            record.msg = f"{emoji} {original_msg}"
        return super().format(record)

def setup_logger(name: str) -> logging.Logger:
    """Sets up and returns a configured logger."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
        
        # Create formatter and add it to the handler
        formatter = EmojiLogFormatter(
            '%(asctime)s | %(levelname)-8s| %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        logger.addHandler(console_handler)
        logger.propagate = False
        
    return logger
