"""FDMS v3.0 cryptographic formatting and signing helpers."""
from __future__ import annotations
import base64, hashlib
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa, utils
from cryptography.x509.oid import NameOID

def iso_local_seconds(value):
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%dT%H:%M:%S") if isinstance(value, datetime) else value.isoformat()
    return str(value).replace(" ", "T")[:19]

def minor_units(value, exponent=2):
    amount = Decimal(str(value)).quantize(Decimal(1).scaleb(-exponent), rounding=ROUND_HALF_UP)
    return str(int(amount.scaleb(exponent)))

def percent_text(value):
    if value is None or value == "":
        return ""
    return format(Decimal(str(value)).normalize(), "f")

def receipt_signature_input(device_id, receipt, previous_receipt_hash=None):
    taxes = sorted(receipt.get("receiptTaxes") or [], key=lambda row: int(row["taxID"]))
    tax_text = "".join(str(t.get("taxCode") or "") + percent_text(t.get("taxPercent")) +
                       minor_units(t.get("taxAmount", 0)) + minor_units(t.get("salesAmountWithTax", 0))
                       for t in taxes)
    fields = [str(int(device_id)), str(receipt["receiptType"]).upper(),
              str(receipt["receiptCurrency"]).upper(), str(int(receipt["receiptGlobalNo"])),
              iso_local_seconds(receipt["receiptDate"]), minor_units(receipt["receiptTotal"]), tax_text]
    if previous_receipt_hash:
        fields.append(previous_receipt_hash)
    return "".join(fields)

def fiscal_day_counters_input(counters):
    def key(c):
        detail = c.get("fiscalCounterTaxID")
        if detail is None:
            detail = c.get("fiscalCounterMoneyType") or ""
        return (str(c["fiscalCounterType"]).upper(),
                str(c.get("fiscalCounterCurrency") or "").upper(), str(detail).upper())
    parts = []
    for c in sorted(counters or [], key=key):
        if Decimal(str(c.get("fiscalCounterValue", 0))) == 0:
            continue
        kind = str(c["fiscalCounterType"]).upper()
        currency = str(c.get("fiscalCounterCurrency") or "").upper()
        detail = (str(c["fiscalCounterMoneyType"]).upper() if "fiscalCounterMoneyType" in c
                  else percent_text(c.get("fiscalCounterTaxPercent")))
        parts.append(kind + currency + detail + minor_units(c["fiscalCounterValue"]))
    return "".join(parts)

def fiscal_day_signature_input(device_id, fiscal_day_no, fiscal_day_date, counters):
    day_date = fiscal_day_date.isoformat() if hasattr(fiscal_day_date, "isoformat") else str(fiscal_day_date)[:10]
    return str(int(device_id)) + str(int(fiscal_day_no)) + day_date + fiscal_day_counters_input(counters)

def fiscal_day_server_signature_input(device_id, fiscal_day_no, fiscal_day_date, fiscal_day_updated,
                                      reconciliation_mode, counters, fiscal_day_device_signature=None):
    value = (str(int(device_id)) + str(int(fiscal_day_no)) +
             (fiscal_day_date.isoformat() if hasattr(fiscal_day_date, "isoformat") else str(fiscal_day_date)[:10]) +
             iso_local_seconds(fiscal_day_updated) + str(reconciliation_mode).upper() +
             fiscal_day_counters_input(counters))
    if str(reconciliation_mode).upper() == "AUTO" and fiscal_day_device_signature:
        value += fiscal_day_device_signature
    return value

def sha256_b64(value):
    return base64.b64encode(hashlib.sha256(value.encode("utf-8")).digest()).decode("ascii")

def sign_hash(private_key_pem, hash_b64, password=None):
    key_bytes = private_key_pem.encode() if isinstance(private_key_pem, str) else private_key_pem
    key = serialization.load_pem_private_key(key_bytes, password=password)
    digest = base64.b64decode(hash_b64, validate=True)
    if len(digest) != 32:
        raise ValueError("Expected a 32-byte SHA-256 digest")
    if isinstance(key, rsa.RSAPrivateKey):
        if key.key_size < 2048:
            raise ValueError("RSA key must be at least 2048 bits")
        signature = key.sign(digest, padding.PKCS1v15(), utils.Prehashed(hashes.SHA256()))
    elif isinstance(key, ec.EllipticCurvePrivateKey):
        if not isinstance(key.curve, ec.SECP256R1):
            raise ValueError("FDMS device keys must use ECDSA P-256")
        signature = key.sign(digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
    else:
        raise TypeError("Unsupported private key; use RSA-2048 or ECDSA P-256")
    return base64.b64encode(signature).decode("ascii")

def create_csr(device_serial_no, device_id, key_type="ECDSA"):
    cn = "ZIMRA-{}-{:010d}".format(device_serial_no, int(device_id))
    subject = x509.Name([x509.NameAttribute(NameOID.COUNTRY_NAME, "ZW"),
                         x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Zimbabwe Revenue Authority"),
                         x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Zimbabwe"),
                         x509.NameAttribute(NameOID.COMMON_NAME, cn)])
    if key_type.upper() == "ECDSA":
        key = ec.generate_private_key(ec.SECP256R1())
    elif key_type.upper() == "RSA":
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    else:
        raise ValueError("key_type must be ECDSA or RSA")
    csr = x509.CertificateSigningRequestBuilder().subject_name(subject).sign(key, hashes.SHA256())
    private_pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                    serialization.NoEncryption()).decode()
    return private_pem, csr.public_bytes(serialization.Encoding.PEM).decode()

def verify_fdms_signature(public_certificate_pem, signature_b64, expected_hash_b64):
    cert = x509.load_pem_x509_certificate(public_certificate_pem.encode() if isinstance(public_certificate_pem, str) else public_certificate_pem)
    public_key = cert.public_key()
    signature, digest = base64.b64decode(signature_b64, validate=True), base64.b64decode(expected_hash_b64, validate=True)
    try:
        if isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(signature, digest, padding.PKCS1v15(), utils.Prehashed(hashes.SHA256()))
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            public_key.verify(signature, digest, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        else:
            raise TypeError("Unsupported FDMS public key type")
        return True
    except Exception:
        return False
