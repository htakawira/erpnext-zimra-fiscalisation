import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRAOfflineQueue(Document):
    def validate(self):
        if self.sequence_no is not None and self.sequence_no < 1:
            frappe.throw(_("Queue sequence number must be positive."))
        if self.attempts is not None and self.attempts < 0:
            frappe.throw(_("Attempts cannot be negative."))
        if self.status == "Completed" and not self.response_payload:
            frappe.throw(_("Completed queue records must retain the response payload."))
