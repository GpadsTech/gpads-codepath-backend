"""Compatibility entry point for WSGI servers; Django owns routing."""

from app.config.wsgi import application

__all__ = ["application"]
