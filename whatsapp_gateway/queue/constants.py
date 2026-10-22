"""
RabbitMQ Queue, Routing & Exchange Constants for WhatsApp Gateway.
"""

DEFAULT_INCOMING_QUEUE = "whatsapp_incoming_messages"
DEFAULT_OUTGOING_QUEUE = "whatsapp_outgoing_messages"
DEFAULT_DEAD_LETTER_QUEUE = "whatsapp_dead_letter"
EXCHANGE_NAME = "whatsapp_gateway_direct"
DLX_EXCHANGE_NAME = "whatsapp_gateway_dlx"
