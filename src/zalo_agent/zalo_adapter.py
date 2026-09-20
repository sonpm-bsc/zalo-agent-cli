"""Zalo Alert Adapter integrating Node CLI zalo-agent and direct dispatch."""

import json
import subprocess
from pathlib import Path
from typing import Optional, List
from zalo_agent.contracts import ZaloMessagePayload, DeliveryReport, AlertPriority
from zalo_agent.vietqr import generate_vietqr_image_url


class ZaloAlertAdapter:
    """Adapter for dispatching operational alerts and banking requests to Zalo."""

    def __init__(self, cli_root: Optional[Path] = None):
        self.cli_root = cli_root or Path(__file__).resolve().parent.parent.parent
        self.cli_entry = self.cli_root / "src" / "index.js"

    def send_alert(self, payload: ZaloMessagePayload) -> DeliveryReport:
        """Send message, priority alerts, and optional VietQR code to Zalo."""
        # Build command invoking zalo-agent-cli
        cmd = ["node", str(self.cli_entry), "msg"]

        if payload.qr_payload:
            cmd.extend([
                "qr-transfer",
                payload.thread_id,
                payload.qr_payload.account_number,
                "--bank", payload.qr_payload.bank,
                "-t", str(payload.thread_type),
            ])
            if payload.qr_payload.amount:
                cmd.extend(["-a", str(payload.qr_payload.amount)])
            if payload.qr_payload.content:
                cmd.extend(["-c", payload.qr_payload.content])
        else:
            cmd.extend([
                "send",
                payload.thread_id,
                payload.message,
                "-t", str(payload.thread_type),
            ])

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )

            if res.returncode == 0:
                msg_id = None
                try:
                    data = json.loads(res.stdout) if res.stdout.strip().startswith("{") else {}
                    msg_id = data.get("message_id") or data.get("msgId")
                except Exception:
                    pass

                return DeliveryReport(
                    success=True,
                    thread_id=payload.thread_id,
                    message_id=msg_id,
                    channel="zalo",
                    priority=payload.priority,
                )
            else:
                return DeliveryReport(
                    success=False,
                    thread_id=payload.thread_id,
                    channel="zalo",
                    priority=payload.priority,
                    error_message=res.stderr.strip() or res.stdout.strip() or "Process returned non-zero",
                )
        except Exception as e:
            return DeliveryReport(
                success=False,
                thread_id=payload.thread_id,
                channel="zalo",
                priority=payload.priority,
                error_message=str(e),
            )
