import frappe
from frappe.model.document import Document
from frappe import _

class ZIMRAFiscalDay(Document):
    def validate(self):
        if self.fiscal_day_no is not None and self.fiscal_day_no < 1:
            frappe.throw(_("Fiscal day number must be a positive integer."))
        if self.status == "FiscalDayClosed" and not self.server_signature:
            frappe.throw(_("A closed fiscal day must retain the FDMS fiscal day signature."))
        if self.status == "FiscalDayCloseInitiated" and not self.close_operation_id:
            frappe.throw(_("Close operation ID is required after closeDay is accepted."))
