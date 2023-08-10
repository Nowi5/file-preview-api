import logging
from flask import g
import config

class ContextualFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    def filter(self, record):
        record.execution_id = getattr(g, "execution_id", "Unknown")
        return True

def configure_logger(app):
    """
    Configure logger with custom filter.
    """
    logging_level = getattr(logging, config.LOGGING_LEVEL)
    logging.basicConfig(level=logging_level)
    
    log = logging.getLogger()
    f = logging.Formatter("%(asctime)s - %(levelname)s - [%(execution_id)s] - %(message)s")
    log_filter = ContextualFilter()
    log.addFilter(log_filter)

    for handler in log.handlers:
        handler.setFormatter(f)
