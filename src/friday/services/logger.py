"""
Simplified Logger Module

This module is deprecated. Use standard Python logging instead.
For WebSocket functionality, implement specific WebSocket handlers as needed.
"""

import logging

# Simple logger for backward compatibility
ws_logger = None  # Deprecated - use standard logging instead


def get_logger(name: str = __name__) -> logging.Logger:
    """Get a standard Python logger."""
    return logging.getLogger(name)
