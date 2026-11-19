import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRAFiscalDevice(Document):
    def validate(self):
        if self.device_id is not None and int(self.device_id) <= 0:
            frappe.throw(_("ZIMRA Device ID must be a positive integer."))
        if self.integration_mode not in ("Automatic", "Manual"):
            frappe.throw(_("Submission mode must be Automatic or Manual."))
        if self.operating_mode == "Offline":
            frappe.msgprint(_("FDMS Offline mode is configured by ZIMRA and is not implemented by the online queue."), alert=True)
        if self.device_serial_no and not self.device_name:
            self.device_name = self.device_serial_no
