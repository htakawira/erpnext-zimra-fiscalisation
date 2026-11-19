import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRAFiscalDevice(Document):
    def validate(self):
        if self.device_id is not None and int(self.device_id) <= 0:
            frappe.throw(_("ZIMRA Device ID must be a positive integer."))
        if self.integration_mode not in ("Automatic", "Manual"):
            frappe.throw(_("Choose Automatic or Manual submission mode."))
        if self.device_serial_no and not self.device_name:
            self.device_name = self.device_serial_no
        if self.registration_status == "Registered" and not self.certificate:
            frappe.throw(_("A registered device must have its FDMS certificate."))
        if self.operating_mode == "Offline":
            frappe.msgprint(_("Offline file submission is not implemented by the online queue."), alert=True)
