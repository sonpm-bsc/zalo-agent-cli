import pytest
from pathlib import Path
from zalo_agent.contracts import (
    AlertPriority,
    VietQRPayload,
    ZaloMessagePayload,
    DeliveryReport,
)
from zalo_agent.vietqr import (
    generate_vietqr_payload,
    generate_vietqr_image_url,
    BANK_NAME_TO_BIN,
    resolve_bank_bin,
)
from zalo_agent.zalo_adapter import ZaloAlertAdapter


def test_contracts_validation():
    # VietQRPayload valid
    qr_payload = VietQRPayload(
        bank="bidv",
        account_number="1234567890",
        account_name="NGUYEN VAN A",
        amount=500000,
        content="UNG HO",
    )
    assert qr_payload.bank == "bidv"
    assert qr_payload.amount == 500000

    # ZaloMessagePayload valid
    msg_payload = ZaloMessagePayload(
        thread_id="123456789",
        message="Alert: High latency detected",
        priority=AlertPriority.P1,
        qr_payload=qr_payload,
    )
    assert msg_payload.priority == AlertPriority.P1
    assert msg_payload.thread_type == 1  # default group

    # DeliveryReport valid
    report = DeliveryReport(
        success=True,
        thread_id="123456789",
        message_id="msg_001",
        channel="zalo",
    )
    assert report.success is True
    assert report.channel == "zalo"


def test_vietqr_crc16_and_payload_generation():
    qr = VietQRPayload(
        bank="970418",  # BIDV
        account_number="1234567890",
        amount=50000,
        content="TEST CHUYEN TIEN",
    )
    payload_str = generate_vietqr_payload(qr)
    assert payload_str.startswith("000201010212")
    assert "A000000727" in payload_str  # Napas AID
    assert "970418" in payload_str
    assert "1234567890" in payload_str
    assert "50000" in payload_str
    assert "6304" in payload_str  # CRC tag
    # Verify exact length format
    crc_part = payload_str[-4:]
    assert len(crc_part) == 4


def test_vietqr_image_url():
    qr = VietQRPayload(
        bank="vcb",
        account_number="0071001234567",
        amount=100000,
        content="THANH TOAN",
    )
    url = generate_vietqr_image_url(qr)
    assert "https://qr.sepay.vn/img?" in url
    assert "acc=0071001234567" in url
    assert "amount=100000" in url


def test_zalo_adapter_send_alert(monkeypatch):
    adapter = ZaloAlertAdapter()

    # Test message building
    qr = VietQRPayload(
        bank="bidv",
        account_number="1234567890",
        amount=2000000,
        content="P1 EMERGENCY",
    )
    payload = ZaloMessagePayload(
        thread_id="group_test_01",
        message="Incident: Core Flex disconnected",
        priority=AlertPriority.P1,
        qr_payload=qr,
    )

    # Mock CLI subprocess call
    def mock_run(cmd, *args, **kwargs):
        class MockResult:
            returncode = 0
            stdout = '{"success": true, "message_id": "zalo_mock_123"}'
            stderr = ""
        return MockResult()

    import subprocess
    monkeypatch.setattr(subprocess, "run", mock_run)

    report = adapter.send_alert(payload)
    assert report.success is True
    assert report.thread_id == "group_test_01"
    assert report.priority == AlertPriority.P1
