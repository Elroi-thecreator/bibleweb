"""
RabbitMQ Connection Management with Robust Reconnection & Health Diagnostics.
"""

import asyncio
import logging
import re
from typing import Optional

logger = logging.getLogger("whatsapp_gateway.queue.connection")


def mask_amqp_url(url: str) -> str:
    """Masks credentials in an AMQP connection URL for secure logging."""
    if not url:
        return "(empty)"
    return re.sub(r"://([^:@]+):([^@]+)@", r"://\1:••••••••@", url)


class RabbitMQConnection:
    """Manages an asynchronous, robust connection to RabbitMQ via aio-pika."""

    def __init__(self, url: str):
        self.url = url
        self.masked_url = mask_amqp_url(url)
        self._connection = None
        self._channel = None
        self._connected = False
        self._connecting = False
        self._lock = asyncio.Lock()

    @property
    def is_connected(self) -> bool:
        """Returns True if the connection and channel are open and ready."""
        return bool(
            self._connected
            and self._connection
            and not self._connection.is_closed
            and self._channel
            and not self._channel.is_closed
        )

    async def connect(self, timeout: float = 4.0) -> bool:
        """
        Attempts to establish connection to RabbitMQ with a strict timeout.
        Returns True on success, False if broker is unreachable.
        """
        async with self._lock:
            if self.is_connected:
                return True

            try:
                import aio_pika

                logger.info("Connecting to RabbitMQ broker at %s (timeout: %.1fs)...", self.masked_url, timeout)
                self._connecting = True

                self._connection = await asyncio.wait_for(
                    aio_pika.connect_robust(
                        self.url,
                        timeout=timeout,
                        client_properties={"connection_name": "HolyBible-WhatsApp-Gateway"},
                    ),
                    timeout=timeout,
                )

                self._channel = await self._connection.channel()
                self._connected = True
                self._connecting = False

                logger.info("Successfully connected to RabbitMQ broker at %s", self.masked_url)
                return True

            except asyncio.TimeoutError:
                logger.warning(
                    "RabbitMQ connection to %s timed out after %.1fs. Falling back to direct mode.",
                    self.masked_url,
                    timeout,
                )
                await self._cleanup()
                return False
            except Exception as exc:
                logger.warning(
                    "RabbitMQ connection to %s failed (%s). Falling back to direct mode.",
                    self.masked_url,
                    exc,
                )
                await self._cleanup()
                return False

    async def get_channel(self):
        """Returns the active robust channel, reconnecting if necessary."""
        if not self.is_connected:
            success = await self.connect()
            if not success:
                raise ConnectionError(f"Cannot acquire channel: RabbitMQ broker unreachable at {self.masked_url}")
        return self._channel

    async def _cleanup(self):
        """Safely cleans up connection references upon failure or close."""
        self._connected = False
        self._connecting = False
        if self._channel and not self._channel.is_closed:
            try:
                await self._channel.close()
            except Exception:
                pass
        if self._connection and not self._connection.is_closed:
            try:
                await self._connection.close()
            except Exception:
                pass
        self._channel = None
        self._connection = None

    async def close(self):
        """Closes channel and connection cleanly."""
        async with self._lock:
            await self._cleanup()
            logger.info("RabbitMQ connection closed cleanly.")
