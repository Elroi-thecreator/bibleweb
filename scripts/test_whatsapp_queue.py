#!/usr/bin/env python3
"""
Automated Verification Suite for WhatsApp RabbitMQ Queue Engine.
Tests queue models, credential masking, fallback direct execution,
runtime toggling, and FastAPI queue telemetry endpoints.
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from whatsapp_gateway.config import config
from whatsapp_gateway.queue.constants import DEFAULT_INCOMING_QUEUE, DEFAULT_OUTGOING_QUEUE
from whatsapp_gateway.queue.connection import mask_amqp_url
from whatsapp_gateway.queue.models import QueueTask, TaskType
from whatsapp_gateway.queue.manager import QueueManager, queue_manager
from whatsapp_gateway.client.models import IncomingWebhookPayload


class TestWhatsAppRabbitMQQueue(unittest.TestCase):
    """Test suite covering WhatsApp RabbitMQ Queue and fallback mechanisms."""

    def setUp(self):
        self.client = TestClient(app)
        from whatsapp_gateway.routes.webhook import get_client
        self._orig_sim = get_client().simulation_mode
        get_client().simulation_mode = True

    def tearDown(self):
        from whatsapp_gateway.routes.webhook import get_client
        get_client().simulation_mode = self._orig_sim

    def test_01_url_masking(self):
        """Verifies credentials in AMQP URLs are masked for safe logging and status."""
        raw = "amqp://admin_user:super_secret_password@cluster01.rabbitmq.cloud:5672/vhost"
        masked = mask_amqp_url(raw)
        self.assertNotIn("super_secret_password", masked)
        self.assertIn("admin_user", masked)
        self.assertIn("••••••••", masked)
        self.assertIn("cluster01.rabbitmq.cloud", masked)

    def test_02_queue_models(self):
        """Verifies QueueTask serialization and validation."""
        task = QueueTask(
            task_type=TaskType.INCOMING_MESSAGE,
            payload={"sender": "919876543210@s.whatsapp.net", "text": "John 3:16"},
            session_id="session_test",
        )
        self.assertTrue(task.task_id)
        self.assertEqual(task.task_type, TaskType.INCOMING_MESSAGE)

        raw_json = task.model_dump_json()
        deserialized = QueueTask.model_validate_json(raw_json)
        self.assertEqual(deserialized.task_id, task.task_id)
        self.assertEqual(deserialized.payload["text"], "John 3:16")

    def test_03_queue_status_in_gateway_status(self):
        """Verifies /api/whatsapp/status includes queue telemetry block."""
        resp = self.client.get("/api/whatsapp/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("queue", data)
        q = data["queue"]
        self.assertIn("enabled", q)
        self.assertIn("backend", q)
        self.assertIn("connected", q)
        self.assertIn("metrics", q)

    def test_04_queue_dedicated_endpoints(self):
        """Verifies /api/whatsapp/queue/status and config endpoints."""
        status_resp = self.client.get("/api/whatsapp/queue/status")
        self.assertEqual(status_resp.status_code, 200)
        st = status_resp.json()
        self.assertIn("backend", st)
        self.assertIn("queues", st)
        self.assertEqual(st["queues"]["incoming"], DEFAULT_INCOMING_QUEUE)

        # Test config update endpoint
        cfg_resp = self.client.post(
            "/api/whatsapp/queue/config",
            json={"enabled": False, "rabbitmq_url": "amqp://guest:guest@127.0.0.1:5672/"},
        )
        self.assertEqual(cfg_resp.status_code, 200)
        cfg_data = cfg_resp.json()
        self.assertFalse(cfg_data["enabled"])

    def test_05_fallback_to_direct_mode_when_offline(self):
        """
        Verifies that when RabbitMQ is enabled but broker is unreachable,
        the system falls back to direct in-memory execution without throwing errors.
        """
        async def run_fallback_test():
            mgr = QueueManager()
            mock_dispatcher = MagicMock()
            mock_dispatcher.dispatch = AsyncMock(return_value=True)
            mock_client = MagicMock()
            mock_client.default_session_id = "default"
            mock_session = MagicMock()

            mgr.initialize(mock_dispatcher, mock_client, mock_session)

            # Enable queue with unreachable dummy port
            config.queue_enabled = True
            config.rabbitmq_url = "amqp://guest:guest@127.0.0.1:59999/"  # Closed port

            started = await mgr.start()
            self.assertFalse(started, "Start should return False when broker is offline")
            self.assertFalse(mgr.is_connected, "Connection should be marked disconnected")
            self.assertEqual(mgr.backend_name, "direct", "Backend must fallback to direct")

            # Dispatch an incoming webhook
            payload = IncomingWebhookPayload(
                event="messages.upsert",
                sessionId="default",
                data={
                    "key": {"remoteJid": "919790423246@s.whatsapp.net", "fromMe": False, "id": "test_msg_01"},
                    "message": {"conversation": "John 3:16"},
                },
            )

            res = await mgr.enqueue_incoming(payload)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["backend"], "direct")
            self.assertTrue(mock_dispatcher.dispatch.called)

            # Clean up
            await mgr.stop()
            config.queue_enabled = False

        asyncio.run(run_fallback_test())

    def test_06_simulated_rabbitmq_publish_and_consume(self):
        """
        Simulates an active RabbitMQ connection using mocked aio-pika channel/queue,
        verifying the complete asynchronous publish and consume workflow.
        """
        async def run_rmq_test():
            mgr = QueueManager()
            mock_dispatcher = MagicMock()
            mock_dispatcher.dispatch = AsyncMock(return_value=True)
            mock_client = MagicMock()
            mock_client.default_session_id = "default"
            mock_session = MagicMock()

            mgr.initialize(mock_dispatcher, mock_client, mock_session)

            # Mock RabbitMQ connection and channel
            mock_channel = AsyncMock()
            mock_queue = AsyncMock()
            mock_channel.declare_queue.return_value = mock_queue

            mock_conn = MagicMock()
            mock_conn.is_connected = True
            mock_conn.get_channel = AsyncMock(return_value=mock_channel)
            mock_conn.close = AsyncMock()

            mgr._conn = mock_conn
            from whatsapp_gateway.queue.publisher import QueuePublisher
            mgr._publisher = QueuePublisher(mock_conn)

            config.queue_enabled = True

            payload = IncomingWebhookPayload(
                event="messages.upsert",
                sessionId="default",
                data={
                    "key": {"remoteJid": "919790423246@s.whatsapp.net", "fromMe": False, "id": "test_msg_02"},
                    "message": {"conversation": "audio John 1"},
                },
            )

            res = await mgr.enqueue_incoming(payload)
            self.assertEqual(res["status"], "queued")
            self.assertEqual(res["backend"], "rabbitmq")
            self.assertTrue(mock_channel.default_exchange.publish.called)

            # Test consumer handling task directly
            task = QueueTask(
                task_type=TaskType.INCOMING_MESSAGE,
                payload=payload.model_dump(),
                session_id="default",
            )
            await mgr._consumer._handle_incoming_task(task)
            self.assertTrue(mock_dispatcher.dispatch.called)

            # Clean up
            await mgr.stop()
            config.queue_enabled = False

        asyncio.run(run_rmq_test())

    def test_07_fastapi_webhook_e2e_with_queue(self):
        """
        Tests end-to-end webhook invocation via FastAPI test client
        in direct/fallback mode.
        """
        sample_webhook = {
            "event": "messages.upsert",
            "sessionId": "1lxijr",
            "data": {
                "key": {
                    "remoteJid": "919790423246@s.whatsapp.net",
                    "fromMe": False,
                    "id": "WEBHOOK_E2E_001",
                },
                "pushName": "Dev Tester",
                "message": {
                    "conversation": "John 3:16",
                },
            },
        }

        resp = self.client.post("/api/whatsapp/webhook", json=sample_webhook)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("status", data)
        self.assertIn(data["status"], ("success", "queued"))

    def test_08_client_auto_enqueues_outgoing_when_queue_ready(self):
        """
        Verifies that any request from web bible via client.send_text or client.send_media
        is automatically pushed as a RabbitMQ message when the queue is ready.
        """
        async def run_client_queue_test():
            from whatsapp_gateway.client.client import WAClient
            from whatsapp_gateway.client.models import SendMessageResponse
            from whatsapp_gateway.queue.publisher import QueuePublisher

            client = WAClient(base_url="https://wa-akg-gateway-ub6a.onrender.com/api", default_session_id="test_sess")

            mock_channel = AsyncMock()
            mock_queue = AsyncMock()
            mock_channel.declare_queue.return_value = mock_queue

            mock_conn = MagicMock()
            mock_conn.is_connected = True
            mock_conn.get_channel = AsyncMock(return_value=mock_channel)

            mgr = QueueManager()
            mock_dispatcher = MagicMock()
            mock_session = MagicMock()
            mgr.initialize(mock_dispatcher, client, mock_session)
            mgr._conn = mock_conn
            mgr._publisher = QueuePublisher(mock_conn)
            config.queue_enabled = True

            # Patch global queue_manager to our ready mgr
            with patch("whatsapp_gateway.queue.manager.queue_manager", mgr):
                # Outgoing text from web bible
                resp_text = await client.send_text(to="919876543210", text="Psalm 23:1 The Lord is my shepherd")
                self.assertTrue(resp_text.success)
                self.assertTrue(resp_text.message_id)
                self.assertEqual(resp_text.raw.get("backend"), "rabbitmq")
                self.assertEqual(resp_text.raw.get("status"), "queued")

                # Outgoing media (audio verse) from web bible
                dummy_audio = b"\x00\x01\x02\x03RIFFWAVEfmt"
                resp_media = await client.send_media(
                    to="919876543210",
                    media_type="audio",
                    file_bytes=dummy_audio,
                    caption="Audio Bible",
                    file_name="psalm_23.m4a",
                    ptt=True,
                )
                self.assertTrue(resp_media.success)
                self.assertEqual(resp_media.raw.get("backend"), "rabbitmq")
                self.assertEqual(resp_media.raw.get("status"), "queued")

                # Verify direct_http=True bypasses re-enqueueing
                client.simulation_mode = True
                resp_direct = await client.send_text(to="919876543210", text="Direct dispatch", direct_http=True)
                self.assertTrue(resp_direct.success)
                self.assertEqual(resp_direct.message_id, "sim-msg-id-123")

            config.queue_enabled = False

        asyncio.run(run_client_queue_test())

    def test_09_gateway_health_checks_and_cold_start_detection(self):
        """
        Verifies client.is_gateway_running accurately detects whether the remote gateway
        is alive or down/sleeping, and wait_until_gateway_running polls until ready.
        """
        async def run_gateway_health_test():
            from whatsapp_gateway.client.client import WAClient
            import httpx

            client = WAClient(base_url="https://wa-akg-gateway-ub6a.onrender.com/api", default_session_id="1lxijr")
            client.simulation_mode = False

            mock_http = AsyncMock()
            mock_http.is_closed = False
            client._client = mock_http

            # Test 1: Remote gateway returns 200 -> running
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_http.get.return_value = mock_resp
            self.assertTrue(await client.is_gateway_running())

            # Test 2: Remote gateway returns 502 Bad Gateway (Render sleeping) -> False
            mock_resp.status_code = 502
            mock_http.get.return_value = mock_resp
            self.assertFalse(await client.is_gateway_running())

            # Test 3: Remote gateway throws ConnectTimeout -> False
            mock_http.get.side_effect = httpx.ConnectTimeout("Connection timed out")
            self.assertFalse(await client.is_gateway_running())

            # Test 4: wait_until_gateway_running polls until gateway recovers
            poll_count = 0

            async def mock_is_running(timeout=5.0):
                nonlocal poll_count
                poll_count += 1
                return poll_count >= 3  # Becomes True on 3rd poll

            with patch.object(client, "is_gateway_running", side_effect=mock_is_running):
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    ready = await client.wait_until_gateway_running(poll_interval=0.01, timeout=5.0)
                    self.assertTrue(ready)
                    self.assertEqual(poll_count, 3)

        asyncio.run(run_gateway_health_test())

    def test_10_outgoing_consumer_waits_for_gateway_to_be_running(self):
        """
        Verifies that when an outgoing task is consumed from RabbitMQ,
        if the gateway is currently sleeping/down, it holds the message until
        the gateway is actively running, and then dispatches without message loss.
        """
        async def run_consumer_wait_test():
            from whatsapp_gateway.client.client import WAClient
            from whatsapp_gateway.client.models import SendMessageResponse
            from whatsapp_gateway.queue.consumer import QueueConsumer

            mock_conn = MagicMock()
            mock_dispatcher = MagicMock()
            mock_session = MagicMock()

            client = WAClient(base_url="https://wa-akg-gateway-ub6a.onrender.com/api", default_session_id="1lxijr")
            client.simulation_mode = False

            consumer = QueueConsumer(
                connection_manager=mock_conn,
                dispatcher=mock_dispatcher,
                client=client,
                session_store=mock_session,
            )

            # Mock gateway status: initially not running, then wait_until_gateway_running succeeds
            with patch.object(client, "is_gateway_running", new_callable=AsyncMock) as mock_is_running:
                mock_is_running.return_value = False

                with patch.object(client, "wait_until_gateway_running", new_callable=AsyncMock) as mock_wait:
                    mock_wait.return_value = True

                    with patch.object(client, "send_text", new_callable=AsyncMock) as mock_send:
                        mock_send.return_value = SendMessageResponse(
                            success=True,
                            message_id="msg_live_789",
                            to="919876543210@s.whatsapp.net",
                        )

                        task = QueueTask(
                            task_type=TaskType.OUTGOING_TEXT,
                            payload={"to": "919876543210", "text": "Proverbs 3:5"},
                            session_id="1lxijr",
                        )

                        await consumer._handle_outgoing_task(task)

                        # Verifications
                        mock_wait.assert_awaited_once()
                        mock_send.assert_awaited_once_with(
                            to="919876543210",
                            text="Proverbs 3:5",
                            session_id="1lxijr",
                            direct_http=True,
                        )

        asyncio.run(run_consumer_wait_test())

    def test_11_outgoing_media_task_consumption_and_base64_decoding(self):
        """
        Verifies that outgoing media tasks (audio verses, voice notes) are correctly
        consumed, base64 payload decoded back to bytes, and passed to client.send_media.
        """
        async def run_media_consumer_test():
            import base64
            from whatsapp_gateway.client.client import WAClient
            from whatsapp_gateway.client.models import SendMessageResponse
            from whatsapp_gateway.queue.consumer import QueueConsumer

            mock_conn = MagicMock()
            mock_dispatcher = MagicMock()
            mock_session = MagicMock()

            client = WAClient(base_url="https://wa-akg-gateway-ub6a.onrender.com/api", default_session_id="1lxijr")
            client.simulation_mode = True

            consumer = QueueConsumer(
                connection_manager=mock_conn,
                dispatcher=mock_dispatcher,
                client=client,
                session_store=mock_session,
            )

            raw_bytes = b"AUDIO_SAMPLE_DATA_BYTES_12345"
            b64_str = base64.b64encode(raw_bytes).decode("ascii")

            with patch.object(client, "send_media", new_callable=AsyncMock) as mock_send_media:
                mock_send_media.return_value = SendMessageResponse(
                    success=True,
                    message_id="media_test_msg_001",
                    to="919876543210@s.whatsapp.net",
                )

                task = QueueTask(
                    task_type=TaskType.OUTGOING_MEDIA,
                    payload={
                        "to": "919876543210",
                        "media_type": "audio",
                        "bytes_b64": b64_str,
                        "caption": "John 1:1 Audio",
                        "file_name": "john_1.m4a",
                        "ptt": True,
                    },
                    session_id="1lxijr",
                )

                await consumer._handle_outgoing_task(task)

                mock_send_media.assert_awaited_once_with(
                    to="919876543210",
                    media_type="audio",
                    file_bytes=raw_bytes,
                    caption="John 1:1 Audio",
                    file_name="john_1.m4a",
                    ptt=True,
                    session_id="1lxijr",
                    direct_http=True,
                )

        asyncio.run(run_media_consumer_test())


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🐇 Running WhatsApp RabbitMQ Queue & Fallback Verification Suite")
    print("=" * 70 + "\n")
    unittest.main(verbosity=2)
