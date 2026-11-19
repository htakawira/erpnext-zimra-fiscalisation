import json
import frappe
import requests


def call(device, method, payload=None, authenticated=True):
    settings = frappe.get_single("ZIMRA Settings")
    base = (settings.api_base_url or "").rstrip("/")
    paths = json.loads(settings.endpoint_paths or "{}")
    path = paths.get(method)
    if not base or not path:
        frappe.throw("Configure the ZIMRA API base URL and exact endpoint path for " + method + ". Obtain these from ZIMRA; paths are not inferred.")
    headers = {"Content-Type": "application/json", "DeviceModelName": settings.device_model_name, "DeviceModelVersionNo": str(settings.device_model_version_no)}
    cert = None
    if authenticated:
        if not device.client_certificate_path or not device.private_key_path:
            frappe.throw("Device client certificate and private key paths are required for mutual TLS.")
        cert = (device.client_certificate_path, device.private_key_path)
    response = requests.post(base + "/" + path.lstrip("/"), json=payload or {}, headers=headers, cert=cert, timeout=30, verify=True)
    response.raise_for_status()
    try:
        return response.json()
    except ValueError:
        frappe.throw("ZIMRA returned a non-JSON response.")
