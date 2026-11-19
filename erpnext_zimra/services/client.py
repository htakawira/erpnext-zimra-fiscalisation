import frappe
import requests
from frappe import _
from erpnext_zimra.services.crypto import create_csr
from pathlib import Path

PUBLIC_OPERATIONS = {"registerDevice", "getServerCertificate"}

def call(device, method, payload=None, authenticated=True):
    settings = frappe.get_single("ZIMRA Settings")
    base = (settings.api_base_url or "").rstrip("/")
    try:
        paths = frappe.parse_json(settings.endpoint_paths or "{}")
    except Exception:
        frappe.throw(_("ZIMRA Endpoint Paths must be valid JSON."))
    path = paths.get(method)
    if not base or not path:
        frappe.throw(_("Configure the official FDMS base URL and exact endpoint path for {0}.").format(method))
    if not base.startswith("https://"):
        frappe.throw(_("FDMS communication must use HTTPS."))
    headers = {
        "Content-Type": "application/json",
        "DeviceModelName": settings.device_model_name,
        "DeviceModelVersionNo": str(settings.device_model_version_no),
    }
    cert = None
    if authenticated and method not in PUBLIC_OPERATIONS:
        if not device.client_certificate_path or not device.private_key_path:
            frappe.throw(_("Device client certificate and private key files are required for mutual TLS."))
        cert = (device.client_certificate_path, device.private_key_path)
    try:
        response = requests.post(
            base + "/" + path.lstrip("/"), json=payload or {}, headers=headers,
            cert=cert, timeout=int(settings.request_timeout or 30), verify=True
        )
        response.raise_for_status()
    except requests.Timeout:
        frappe.throw(_("FDMS request timed out. It remains eligible for ordered retry."))
    except requests.RequestException as exc:
        frappe.log_error(title="ZIMRA HTTP communication error", message=str(exc))
        frappe.throw(_("FDMS communication failed: {0}").format(str(exc)))
    try:
        result = response.json()
    except ValueError:
        frappe.throw(_("FDMS returned a non-JSON response."))
    if not isinstance(result, dict):
        frappe.throw(_("FDMS response must be a JSON object."))
    return result

@frappe.whitelist()
def register_device(device_name, key_type="ECDSA"):
    device = frappe.get_doc("ZIMRA Fiscal Device", device_name)
    if device.registration_status == "Registered" and device.certificate:
        frappe.throw(_("This device is already registered. Use certificate renewal instead."))
    if not device.activation_key:
        frappe.throw(_("Enter the ZIMRA-issued 8-character activation key first."))
    private_key, csr = create_csr(device.device_serial_no, device.device_id, key_type)
    result = call(device, "registerDevice", {
        "deviceID": int(device.device_id),
        "activationKey": device.get_password("activation_key"),
        "certificateRequest": csr,
    }, authenticated=False)
    if not result.get("certificate") or not result.get("operationID"):
        frappe.throw(_("FDMS registration response is missing certificate or operationID."))
    private_dir = Path(frappe.get_site_path("private", "files", "zimra", device.name))
    private_dir.mkdir(parents=True, exist_ok=True)
    key_path = private_dir / "device-private-key.pem"
    key_path.write_text(private_key, encoding="utf-8")
    key_path.chmod(0o600)
    cert_path = private_dir / "device-certificate.pem"
    cert_path.write_text(result["certificate"], encoding="utf-8")
    cert_path.chmod(0o600)
    device.certificate = result["certificate"]
    device.private_key_path = str(key_path)
    device.client_certificate_path = str(cert_path)
    device.registration_status = "Registered"
    device.save(ignore_permissions=True)
    return {"operationID": result["operationID"], "registration_status": device.registration_status}
