import frappe
from frappe.utils import cint


def on_submit(doc, method=None):
    settings = frappe.get_single("ZIMRA Settings")
    if not cint(settings.enabled):
        return
    if settings.fiscalisation_mode == "Automatic":
        enqueue_invoice(doc.name)


def on_cancel(doc, method=None):
    # A submitted fiscal receipt must never be silently deleted or re-used.
    rows = frappe.get_all("ZIMRA Fiscal Receipt", filters={"sales_invoice": doc.name}, fields=["name", "status"])
    if any(r.status in ("Accepted", "Submitted", "Queued") for r in rows):
        frappe.msgprint("This invoice has a fiscalisation record. Process the required ZIMRA credit-note/cancellation workflow; do not delete the fiscal receipt.", alert=True)


@frappe.whitelist()
def enqueue_invoice(invoice_name):
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    if doc.docstatus != 1:
        frappe.throw("Only submitted Sales Invoices can be fiscalised.")
    settings = frappe.get_single("ZIMRA Settings")
    device = frappe.db.get_value("ZIMRA Fiscal Device", {"company": doc.company, "branch": getattr(doc, "branch", None), "enabled": 1}, "name")
    if not device:
        device = frappe.db.get_value("ZIMRA Fiscal Device", {"company": doc.company, "enabled": 1}, "name")
    if not device:
        frappe.throw("No enabled ZIMRA Fiscal Device is mapped to this company/branch.")
    existing = frappe.db.get_value("ZIMRA Fiscal Receipt", {"sales_invoice": invoice_name}, "name")
    if existing:
        return existing
    receipt = frappe.get_doc({"doctype": "ZIMRA Fiscal Receipt", "sales_invoice": invoice_name, "company": doc.company, "fiscal_device": device, "status": "Queued", "request_mode": "Manual"})
    receipt.insert(ignore_permissions=True)
    frappe.enqueue("erpnext_zimra.services.queue.submit_receipt", receipt_name=receipt.name, queue="short", enqueue_after_commit=True)
    return receipt.name
