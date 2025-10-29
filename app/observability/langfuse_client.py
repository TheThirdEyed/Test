from contextlib import contextmanager
from typing import Any, Dict, Optional
from app.config import settings

try:
    if settings.LANGFUSE_HOST and settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
        from langfuse import Langfuse
        _lf = Langfuse(
            host=settings.LANGFUSE_HOST,
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            debug=settings.LANGFUSE_DEBUG,
        )
    else:
        _lf = None
except Exception:
    _lf = None

@contextmanager
def lf_trace(name: str, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
    if _lf is None:
        yield None
        return
    trace = _lf.trace(name=name, user_id=user_id, metadata=metadata or {})
    try:
        yield trace
    finally:
        try:
            trace.end()
        except Exception:
            pass

@contextmanager
def lf_span(trace, name: str, metadata: Optional[Dict[str, Any]] = None):
    if _lf is None or trace is None:
        yield None
        return
    span = trace.span(name=name, metadata=metadata or {})
    try:
        yield span
    finally:
        try:
            span.end()
        except Exception:
            pass
