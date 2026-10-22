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


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🐇 Running WhatsApp RabbitMQ Queue & Fallback Verification Suite")
    print("=" * 70 + "\n")
    unittest.main(verbosity=2)
