import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRAFiscalDay(Document):
    def validate(self):
        if self.fiscal_day_no is not None and int(self.fiscal_day_no) < 1:
            frappe.throw(_("Fiscal day number must be positive."))
        if self.status == "FiscalDayCloseInitiated" and not self.close_operation_id:
            frappe.throw(_("FDMS close operation ID is required."))
        if self.status == "FiscalDayClosed" and not self.server_signature:
            frappe.throw(_("Closed fiscal day must retain its FDMS signature."))
