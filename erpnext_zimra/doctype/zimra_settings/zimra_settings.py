import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRASettings(Document):
    def validate(self):
        if self.request_timeout and not 1 <= int(self.request_timeout) <= 120:
            frappe.throw(_("Request timeout must be between 1 and 120 seconds."))
        if self.api_base_url and not self.api_base_url.startswith("https://"):
            frappe.throw(_("FDMS API URL must use HTTPS."))
        if self.endpoint_paths:
            try:
                paths = frappe.parse_json(self.endpoint_paths)
            except Exception:
                frappe.throw(_("Endpoint Paths must contain valid JSON."))
            allowed = {"registerDevice","issueCertificate","getConfig","getStatus","openDay",
                       "submitReceipt","closeDay","getServerCertificate"}
            if not isinstance(paths, dict) or set(paths) - allowed:
                frappe.throw(_("Endpoint Paths JSON contains unsupported operations."))
