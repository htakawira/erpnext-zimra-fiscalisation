import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRAFiscalReceipt(Document):
    def validate(self):
        if self.receipt_counter is not None and int(self.receipt_counter) < 1:
            frappe.throw(_("Receipt counter must be positive."))
        if self.receipt_global_no is not None and int(self.receipt_global_no) < 1:
            frappe.throw(_("Receipt global number must be positive."))
        if self.status == "Accepted" and (not self.receipt_id or not self.server_signature):
            frappe.throw(_("Accepted online receipts must retain FDMS receipt ID and signature."))
        if self.status in ("Submitting", "Accepted") and not self.request_payload:
            frappe.throw(_("Receipt payload is required before submission."))
