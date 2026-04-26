"""
Majestic AI v1.0 – Error Handling Engine
10 error types, exponential backoff (immediate→5s→10s, 3 retries),
graceful degradation with fallback chains.
"""
import time
import logging
import functools
from enum import Enum
from typing import Callable, Any, List

logger = logging.getLogger("majestic.errors")

# ── Error taxonomy ────────────────────────────────────────────────────────
class ErrorType(str, Enum):
    TIMEOUT              = "TIMEOUT"
    PERMISSION_DENIED    = "PERMISSION_DENIED"
    NETWORK_UNREACHABLE  = "NETWORK_UNREACHABLE"
    RATE_LIMITED         = "RATE_LIMITED"
    TOOL_NOT_FOUND       = "TOOL_NOT_FOUND"
    INVALID_PARAMETERS   = "INVALID_PARAMETERS"
    RESOURCE_EXHAUSTED   = "RESOURCE_EXHAUSTED"
    AUTHENTICATION_FAILED= "AUTHENTICATION_FAILED"
    TARGET_UNREACHABLE   = "TARGET_UNREACHABLE"
    PARSING_ERROR        = "PARSING_ERROR"

class MajesticError(Exception):
    def __init__(self, error_type: ErrorType, message: str, recoverable: bool = True):
        self.error_type  = error_type
        self.recoverable = recoverable
        super().__init__(message)

# ── Exponential back-off schedule ─────────────────────────────────────────
BACKOFF_DELAYS = [0, 5, 10]   # immediate, then 5 s, then 10 s

def with_retry(max_retries: int = 3, error_types_to_retry: List[ErrorType] = None):
    """Decorator: retry with exponential backoff on recoverable errors."""
    if error_types_to_retry is None:
        error_types_to_retry = [
            ErrorType.TIMEOUT,
            ErrorType.NETWORK_UNREACHABLE,
            ErrorType.RATE_LIMITED,
            ErrorType.RESOURCE_EXHAUSTED,
            ErrorType.TARGET_UNREACHABLE,
        ]

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries):
                delay = BACKOFF_DELAYS[min(attempt, len(BACKOFF_DELAYS) - 1)]
                if delay:
                    logger.debug("⏳ Retry %d/%d – sleeping %ds", attempt, max_retries, delay)
                    time.sleep(delay)
                try:
                    return fn(*args, **kwargs)
                except MajesticError as exc:
                    last_exc = exc
                    if exc.error_type not in error_types_to_retry or not exc.recoverable:
                        raise
                    logger.warning("⚠ [%s] %s – retrying (%d/%d)",
                                   exc.error_type, exc, attempt + 1, max_retries)
                except Exception as exc:
                    last_exc = exc
                    logger.warning("⚠ Unexpected error: %s – retrying (%d/%d)",
                                   exc, attempt + 1, max_retries)
            raise last_exc
        return wrapper
    return decorator

# ── Graceful Degradation ──────────────────────────────────────────────────
class GracefulDegradation:
    """
    Execute a primary callable; on failure fall through an ordered list
    of fallback callables (nmap → masscan → rustscan pattern).
    """

    @staticmethod
    def execute_with_fallbacks(primary: Callable, fallbacks: List[Callable],
                               *args, **kwargs) -> Any:
        chain = [primary] + list(fallbacks)
        last_exc = None
        for fn in chain:
            try:
                result = fn(*args, **kwargs)
                if fn != primary:
                    logger.info("✅ Degraded to fallback: %s", getattr(fn, '__name__', str(fn)))
                return result
            except Exception as exc:
                last_exc = exc
                logger.warning("⚠ %s failed (%s), trying next…",
                               getattr(fn, '__name__', str(fn)), exc)
        raise MajesticError(
            ErrorType.TOOL_NOT_FOUND,
            f"All fallbacks exhausted. Last error: {last_exc}",
            recoverable=False,
        )

    # Pre-built fallback groups ─────────────────────────────────────────
    PORT_SCAN_CHAIN = ["nmap", "masscan", "rustscan"]
    DNS_ENUM_CHAIN  = ["amass", "subfinder", "assetfinder"]
    WEB_CRAWL_CHAIN = ["katana", "gau", "waybackurls"]

# ── classify_exception helper ─────────────────────────────────────────────
def classify_exception(exc: Exception) -> ErrorType:
    msg = str(exc).lower()
    if "timeout" in msg or "timed out" in msg:
        return ErrorType.TIMEOUT
    if "permission" in msg or "denied" in msg:
        return ErrorType.PERMISSION_DENIED
    if "network" in msg or "unreachable" in msg or "no route" in msg:
        return ErrorType.NETWORK_UNREACHABLE
    if "rate" in msg or "429" in msg or "too many" in msg:
        return ErrorType.RATE_LIMITED
    if "not found" in msg or "no such file" in msg:
        return ErrorType.TOOL_NOT_FOUND
    if "invalid" in msg or "parameter" in msg:
        return ErrorType.INVALID_PARAMETERS
    if "memory" in msg or "resource" in msg:
        return ErrorType.RESOURCE_EXHAUSTED
    if "auth" in msg or "401" in msg or "403" in msg:
        return ErrorType.AUTHENTICATION_FAILED
    if "connect" in msg or "refused" in msg:
        return ErrorType.TARGET_UNREACHABLE
    return ErrorType.PARSING_ERROR
