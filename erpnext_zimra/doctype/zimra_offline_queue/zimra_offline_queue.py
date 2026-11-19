import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRAOfflineQueue(Document):
    def validate(self):
        if self.sequence_no is not None and int(self.sequence_no) < 1:
            frappe.throw(_("Queue sequence number must be positive."))
        if self.status == "Sent" and not self.sent_at:
            frappe.throw(_("Sent queue records must have a sent timestamp."))
