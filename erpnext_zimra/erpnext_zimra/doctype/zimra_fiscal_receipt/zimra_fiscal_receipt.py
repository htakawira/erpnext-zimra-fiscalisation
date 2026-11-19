import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRAFiscalReceipt(Document):
    def validate(self):
        if self.receipt_total is not None and self.receipt_total < 0 and self.receipt_type != "CreditNote":
            frappe.throw(_("A negative total is only valid for a CreditNote."))
        if self.receipt_counter is not None and self.receipt_counter < 1:
            frappe.throw(_("Receipt counter must be at least 1."))
        if self.receipt_global_no is not None and self.receipt_global_no < 1:
            frappe.throw(_("Receipt global number must be at least 1."))
        if self.status == "Accepted" and not self.fdms_receipt_id:
            frappe.throw(_("An accepted receipt must have an FDMS receipt ID."))
        if self.status == "Accepted" and not self.server_signature:
            frappe.throw(_("An accepted online receipt must retain the FDMS signature."))
        if self.status in ("Submitting", "Accepted") and not self.receipt_payload:
            frappe.throw(_("Receipt payload is required before submission."))
