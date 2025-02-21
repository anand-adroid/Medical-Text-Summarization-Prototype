from loguru import logger
import os

LOG_DIR = "backend/logs"
LOG_FILE = os.path.join(LOG_DIR, "summary.log")


os.makedirs(LOG_DIR, exist_ok=True)


logger.remove()


logger.add(
    LOG_FILE,
    rotation="10 MB",  
    retention="10 days",  
    compression="zip",  
    enqueue=True,  
    backtrace=True,  
    diagnose=False,  
    level="INFO"
)


logger.info("Logging system initialized successfully!")

def log_request(input_text, output_text, input_tokens, output_tokens, duration):
    """Log each API request for debugging and monitoring."""
    logger.info(f"""
    REQUEST LOG:
    Input Tokens: {input_tokens}
    Output Tokens: {output_tokens}
    Duration: {duration:.2f} seconds
    Input (Preview): {input_text[:300]}...
    Output (Preview): {output_text[:300]}...
    """)
