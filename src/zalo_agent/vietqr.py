"""VietQR NAPAS 247 Dynamic Payload and Image Generator."""

import re
from urllib.parse import urlencode
from typing import Optional, Dict
from zalo_agent.contracts import VietQRPayload


# Vietnamese Bank Name / Alias to BIN code (SSOT matched with bank-helpers.js)
BANK_NAME_TO_BIN: Dict[str, int] = {
    "abbank": 970425,
    "acb": 970416,
    "agribank": 970405,
    "bidv": 970418,
    "bvbank": 970454,
    "bacabank": 970409,
    "baoviet": 970438,
    "cake": 546034,
    "cbbank": 970444,
    "cimb": 422589,
    "coopbank": 970446,
    "dbs": 796500,
    "dongabank": 970406,
    "eximbank": 970431,
    "gpbank": 970408,
    "hdbank": 970437,
    "hsbc": 458761,
    "hongleong": 970442,
    "ibkhcm": 970456,
    "ibkhn": 970455,
    "indovina": 970434,
    "kbank": 668888,
    "kienlongbank": 970452,
    "kookminhcm": 970463,
    "kookminhn": 970462,
    "mbbank": 970422,
    "mb": 970422,
    "msb": 970426,
    "ncb": 970419,
    "namabank": 970428,
    "nonghyup": 801011,
    "ocb": 970448,
    "oceanbank": 970414,
    "pgbank": 970430,
    "pvcombank": 970412,
    "publicbank": 970439,
    "scb": 970429,
    "shb": 970443,
    "sacombank": 970403,
    "saigonbank": 970400,
    "seabank": 970440,
    "shinhan": 970424,
    "standardchartered": 970410,
    "tnex": 9704261,
    "tpbank": 970423,
    "techcombank": 970407,
    "timo": 963388,
    "ubank": 546035,
    "uob": 970458,
    "vib": 970441,
    "vpbank": 970432,
    "vrb": 970421,
    "vietabank": 970427,
    "vietbank": 970433,
    "vietcombank": 970436,
    "vcb": 970436,
    "vietinbank": 970415,
    "ctg": 970415,
    "woori": 970457,
}

BIN_TO_DISPLAY: Dict[int, str] = {
    970425: "ABBank",
    970416: "ACB",
    970405: "Agribank",
    970418: "BIDV",
    970454: "BVBank",
    970409: "BacA Bank",
    970438: "BaoViet Bank",
    546034: "CAKE",
    970444: "CB Bank",
    422589: "CIMB",
    970446: "Co-op Bank",
    796500: "DBS",
    970406: "DongA Bank",
    970431: "Eximbank",
    970408: "GPBank",
    970437: "HDBank",
    458761: "HSBC",
    970442: "Hong Leong",
    970456: "IBK HCM",
    970455: "IBK HN",
    970434: "Indovina",
    668888: "KBank",
    970452: "KienlongBank",
    970463: "Kookmin HCM",
    970462: "Kookmin HN",
    970422: "MB Bank",
    970426: "MSB",
    970419: "NCB",
    970428: "Nam A Bank",
    801011: "NongHyup",
    970448: "OCB",
    970414: "OceanBank",
    970430: "PGBank",
    970412: "PVcomBank",
    970439: "Public Bank",
    970429: "SCB",
    970443: "SHB",
    970403: "Sacombank",
    970400: "Saigon Bank",
    970440: "SeABank",
    970424: "Shinhan",
    970410: "Standard Chartered",
    9704261: "TNEX",
    970423: "TPBank",
    970407: "Techcombank",
    963388: "Timo",
    546035: "UBank",
    970458: "UOB",
    970441: "VIB",
    970432: "VPBank",
    970421: "VRB",
    970427: "VietABank",
    970433: "VietBank",
    970436: "Vietcombank",
    970415: "VietinBank",
    970457: "Woori",
}

BIN_TO_SEPAY: Dict[int, str] = {
    970415: "VietinBank",
    970436: "Vietcombank",
    970422: "MBBank",
    970416: "ACB",
    970432: "VPBank",
    970423: "TPBank",
    970426: "MSB",
    970428: "NamABank",
    970449: "LienVietPostBank",
    970454: "VietCapitalBank",
    970418: "BIDV",
    970403: "Sacombank",
    970441: "VIB",
    970437: "HDBank",
    970440: "SeABank",
    970408: "GPBank",
    970412: "PVcomBank",
    970419: "NCB",
    970424: "ShinhanBank",
    970429: "SCB",
    970430: "PGBank",
    970405: "Agribank",
    970407: "Techcombank",
    970400: "SaigonBank",
    970406: "DongABank",
    970409: "BacABank",
    970410: "StandardChartered",
    970414: "Oceanbank",
    970421: "VRB",
    970425: "ABBANK",
    970427: "VietABank",
    970431: "Eximbank",
    970433: "VietBank",
    970434: "IndovinaBank",
    970438: "BaoVietBank",
    970439: "PublicBank",
    970443: "SHB",
    970444: "CBBank",
    970448: "OCB",
    970452: "KienLongBank",
    422589: "CIMB",
    458761: "HSBC",
    796500: "DBSBank",
    801011: "Nonghyup",
    970442: "HongLeong",
    970457: "Woori",
    970458: "UnitedOverseas",
    970462: "KookminHN",
    970463: "KookminHCM",
    970446: "COOPBANK",
}


def resolve_bank_bin(bank_input: str) -> Optional[int]:
    """Convert bank alias or string BIN to numeric BIN code."""
    cleaned = bank_input.strip().lower().replace(" ", "").replace("_", "")
    if cleaned.isdigit():
        n = int(cleaned)
        return n if n in BIN_TO_DISPLAY else n
    return BANK_NAME_TO_BIN.get(cleaned)


def _format_tlv(tag: str, value: str) -> str:
    """Format EMVCo TLV string (Tag, Length 2-digits, Value)."""
    val_bytes = value.encode("utf-8")
    return f"{tag}{len(val_bytes):02d}{value}"


def compute_crc16(data: str) -> str:
    """Compute CRC16-CCITT (polynomial 0x1021, init 0xFFFF)."""
    crc = 0xFFFF
    for byte in data.encode("utf-8"):
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def generate_vietqr_payload(payload: VietQRPayload) -> str:
    """Generate EMVCo compliant VietQR string conforming to NAPAS 247 specification."""
    bin_code = resolve_bank_bin(payload.bank)
    if not bin_code:
        raise ValueError(f"Unknown bank identifier: {payload.bank}")

    # Tag 00: Payload Format Indicator
    res = _format_tlv("00", "01")

    # Tag 01: Point of Initiation Method (12 = Dynamic, 11 = Static)
    res += _format_tlv("01", "12" if payload.amount else "11")

    # Tag 38: Merchant Account Information (NAPAS 247)
    # Sub-tag 00: GUID (A000000727)
    # Sub-tag 01: Beneficiary Bank BIN + Account (Tag 00: BIN, Tag 01: Acc)
    # Sub-tag 02: Service Code (QRIBFTTA)
    sub01 = _format_tlv("00", str(bin_code)) + _format_tlv("01", payload.account_number)
    tag38_val = (
        _format_tlv("00", "A000000727")
        + _format_tlv("01", sub01)
        + _format_tlv("02", "QRIBFTTA")
    )
    res += _format_tlv("38", tag38_val)

    # Tag 53: Transaction Currency (704 = VND)
    res += _format_tlv("53", "704")

    # Tag 54: Transaction Amount
    if payload.amount and payload.amount > 0:
        res += _format_tlv("54", str(payload.amount))

    # Tag 58: Country Code (VN)
    res += _format_tlv("58", "VN")

    # Tag 62: Additional Data Field (Memo / Purpose)
    if payload.content:
        # Sub-tag 08: Purpose of Transaction (max 50 chars)
        sub08 = _format_tlv("08", payload.content[:50])
        res += _format_tlv("62", sub08)

    # Tag 63: CRC placeholder (Tag 63, length 04)
    res += "6304"
    crc_code = compute_crc16(res)
    return res + crc_code


def generate_vietqr_image_url(payload: VietQRPayload) -> str:
    """Generate qr.sepay.vn URL for rendering image directly."""
    bin_code = resolve_bank_bin(payload.bank)
    if not bin_code:
        raise ValueError(f"Unknown bank: {payload.bank}")

    sepay_name = BIN_TO_SEPAY.get(bin_code)
    bank_param = sepay_name if sepay_name else str(bin_code)

    query = {
        "bank": bank_param,
        "acc": payload.account_number,
        "template": payload.template,
    }
    if payload.amount:
        query["amount"] = str(payload.amount)
    if payload.content:
        query["des"] = payload.content[:50]

    return f"https://qr.sepay.vn/img?{urlencode(query)}"
