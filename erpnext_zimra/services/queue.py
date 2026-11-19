import frappe
from frappe.utils import now_datetime
from erpnext_zimra.services.client import call


def process_pending():
    # Serial queue per device; global receipt numbers must not be skipped.
    devices = frappe.get_all("ZIMRA Offline Queue", filters={"status": "Pending"}, fields=["fiscal_device"], group_by="fiscal_device")
    for row in devices:
        frappe.enqueue("erpnext_zimra.services.queue.process_device_queue", device_name=row.fiscal_device, queue="short")


def process_device_queue(device_name):
    rows = frappe.get_all("ZIMRA Offline Queue", filters={"fiscal_device": device_name, "status": "Pending"}, fields=["name", "queue_type", "fiscal_day", "fiscal_receipt"], order_by="creation asc", limit=1)
    if not rows:
        return
    row = frappe.get_doc("ZIMRA Offline Queue", rows[0].name)
    device = frappe.get_doc("ZIMRA Fiscal Device", device_name)
    try:
        # Enforce openDay before any receipt delayed by loss of connectivity.
        if row.queue_type == "Open Day":
            from erpnext_zimra.services.fiscal_day import transmit_open_day
            transmit_open_day(row.fiscal_day)
        elif row.queue_type == "Receipt":
            day = frappe.get_doc("ZIMRA Fiscal Day", row.fiscal_day)
            if day.status != "FiscalDayOpened":
                frappe.throw("Receipt cannot be sent until its fiscal day is confirmed opened in FDMS.")
            from erpnext_zimra.services.receipts import transmit_receipt
            transmit_receipt(row.fiscal_receipt)
        row.status = "Sent"
        row.sent_at = now_datetime()
        row.save(ignore_permissions=True)
    except Exception:
        row.status = "Failed"
        row.error = frappe.get_traceback()[-4000:]
        row.save(ignore_permissions=True)
        frappe.log_error(title="ZIMRA queue processing failed", message=row.error)
