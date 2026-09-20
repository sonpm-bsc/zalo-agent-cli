"""Pydantic V2 data contracts for Zalo Banking & Operational Alert CLI Integration."""

from enum import Enum
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class AlertPriority(str, Enum):
    """Operational alert priority levels."""
    P1 = "P1"  # Critical / Emergency
    P2 = "P2"  # High
    P3 = "P3"  # Medium
    P4 = "P4"  # Low / Info


class VietQRPayload(BaseModel):
    """Payload definition for generating VietQR NAPAS 247."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    bank: str = Field(description="Bank name alias (e.g. bidv, vcb) or numeric BIN")
    account_number: str = Field(description="Beneficiary account number", min_length=4, max_length=30)
    account_name: Optional[str] = Field(default=None, description="Beneficiary account holder name")
    amount: Optional[int] = Field(default=None, ge=0, description="Transfer amount in VND")
    content: Optional[str] = Field(default=None, max_length=50, description="Transfer memo/description (max 50 chars)")
    template: str = Field(default="compact", description="QR template (compact | print | qronly)")


class ZaloMessagePayload(BaseModel):
    """Payload for dispatching messages and operational alerts to Zalo."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    thread_id: str = Field(description="Recipient User ID or Group ID")
    message: str = Field(description="Message body text (supports markdown syntax)")
    thread_type: int = Field(default=1, description="0 = User (DM), 1 = Group")
    priority: AlertPriority = Field(default=AlertPriority.P3, description="Alert priority level")
    attachments: List[str] = Field(default_factory=list, description="File/Image paths to attach")
    qr_payload: Optional[VietQRPayload] = Field(default=None, description="Optional VietQR details to attach")


class DeliveryReport(BaseModel):
    """Delivery receipt report following dispatch."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    success: bool
    thread_id: str
    message_id: Optional[str] = None
    channel: str = "zalo"
    priority: Optional[AlertPriority] = None
    error_message: Optional[str] = None
