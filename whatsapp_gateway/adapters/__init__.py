"""
Domain Adapters Package.
Contains application-specific logic integrating domain models with the WhatsApp bot.
"""

from whatsapp_gateway.adapters.bible_adapter import register_bible_handlers

__all__ = ["register_bible_handlers"]
