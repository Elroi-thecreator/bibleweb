"""
Typed exceptions for WhatsApp Gateway operations.
"""


class WAGatewayError(Exception):
    """Base exception for all WhatsApp gateway errors."""
    pass


class WAGatewayConnectionError(WAGatewayError):
    """Raised when the connection to the WA-AKG service fails or times out."""
    pass


class WASessionError(WAGatewayError):
    """Raised when the specified WhatsApp session is invalid, disconnected, or unauthenticated."""
    pass


class WAMessageSendError(WAGatewayError):
    """Raised when sending a text or media message fails."""
    pass


class WAWebhookPayloadError(WAGatewayError):
    """Raised when parsing an incoming webhook payload fails."""
    pass
