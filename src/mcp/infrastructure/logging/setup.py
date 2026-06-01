from __future__ import annotations

import json
import logging
import logging.config
import sys
from datetime import UTC, datetime
from typing import Any

# ── JSON Formatter (production) ────────────────────────────────────────────────
 
class JsonFormatter(logging.Formatter):
 
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=UTC
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
 
        # Attach exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
 
        # Attach any extra fields passed via logger.info("msg", extra={...})
        extra_keys = set(record.__dict__) - {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "taskName",
        }
        for key in extra_keys:
            log_entry[key] = getattr(record, key)
 
        return json.dumps(log_entry, ensure_ascii=False)
 
 
# ── Human-readable formatter (development) ────────────────────────────────────
 
_DEV_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DEV_DATE   = "%Y-%m-%dT%H:%M:%S"
 
 
# ── Main configuration function ────────────────────────────────────────────────
 
def configure_logging(log_level: str, json_logs: bool = False) -> None:

    level = log_level.upper()
 
    # Validate level early — fail loud at startup, not on first log call
    numeric_level = getattr(logging, level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(
            f"Invalid log level: {log_level!r}. "
            f"Expected one of: DEBUG, INFO, WARNING, ERROR, CRITICAL."
        )
 
    if json_logs:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(fmt=_DEV_FORMAT, datefmt=_DEV_DATE)
 
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(formatter)
 
    # Configure the root logger — all named loggers inherit from it
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
 
    # Remove existing handlers to avoid duplicate output on re-configuration
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
 
    # Silence noisy third-party loggers in production
    if level != "DEBUG":
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("slack_bolt").setLevel(logging.WARNING)
        logging.getLogger("slack_sdk").setLevel(logging.WARNING)
 
    logging.getLogger(__name__).info(
        "Logging configured | level=%s | format=%s",
        level,
        "json" if json_logs else "text",
    )