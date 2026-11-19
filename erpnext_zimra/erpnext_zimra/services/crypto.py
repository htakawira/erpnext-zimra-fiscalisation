"""ZIMRA SHA-256 and device-signature primitives (FDMS API v3.0 §§13.1-13.2)."""
from __future__ import annotations
import base64, hashlib
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa, utils

def iso_local_seconds(value: Any) -> str:
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    return str(value).replace(" ", "T")[:19]

def minor_units(value: Any, exponent: int = 2) -> str:
    amount = Decimal(str(value)).quantize(Decimal(1).scaleb(-exponent), rounding=ROUND_HALF_UP)
    return str(int(amount.scaleb(exponent)))

def _tax_signature_part(tax: dict) -> str:
    percent = tax.get("taxPercent")
    percent_text = "" if percent is None else str(Decimal(str(percent)).normalize())
    return "".join((str(tax.get("taxCode", tax.get("taxID", ""))), percent_text,
                    minor_units(tax.get("taxAmount", 0)), minor_units(tax.get("salesAmountWithTax", 0))))

def receipt_signature_input(device_id: int, receipt: dict, previous_receipt_hash: str | None = None) -> str:
    taxes = sorted(receipt.get("receiptTaxes") or [], key=lambda row: int(row.get("taxID", 0)))
    fields = [str(int(device_id)), str(receipt["receiptType"]).upper(),
              str(receipt["receiptCurrency"]).upper(), str(int(receipt["receiptGlobalNo"])),
              iso_local_seconds(receipt["receiptDate"]), minor_units(receipt["receiptTotal"]),
              "".join(_tax_signature_part(row) for row in taxes)]
    if previous_receipt_hash:
        fields.append(previous_receipt_hash)
    return "".join(fields)

def sha256_b64(value: str) -> str:
    return base64.b64encode(hashlib.sha256(value.encode("utf-8")).digest()).decode("ascii")

def sign_hash(private_key_pem: str | bytes, hash_b64: str, password: bytes | None = None) -> str:
    key_bytes = private_key_pem.encode() if isinstance(private_key_pem, str) else private_key_pem
    key = serialization.load_pem_private_key(key_bytes, password=password)
    digest = base64.b64decode(hash_b64)
    if len(digest) != 32:
        raise ValueError("Expected a 32-byte SHA-256 digest")
    if isinstance(key, rsa.RSAPrivateKey):
        signature = key.sign(digest, padding.PKCS1v15(), utils.Prehashed(hashes.SHA256()))
    elif isinstance(key, ec.EllipticCurvePrivateKey):
        if not isinstance(key.curve, ec.SECP256R1):
            raise ValueError("ZIMRA requires ECDSA on SECG secp256r1 / P-256")
        signature = key.sign(digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
    else:
        raise TypeError("Unsupported private key type; use RSA-2048 or ECDSA P-256")
    return base64.b64encode(signature).decode("ascii")

def create_receipt_device_signature(device_id: int, receipt: dict, private_key_pem: str | bytes,
                                    previous_receipt_hash: str | None = None,
                                    password: bytes | None = None) -> tuple[str, str]:
    digest_b64 = sha256_b64(receipt_signature_input(device_id, receipt, previous_receipt_hash))
    return digest_b64, sign_hash(private_key_pem, digest_b64, password=password)
