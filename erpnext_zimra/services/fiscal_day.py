import frappe
from erpnext_zimra.services.client import call


def transmit_open_day(day_name):
    day = frappe.get_doc("ZIMRA Fiscal Day", day_name)
    device = frappe.get_doc("ZIMRA Fiscal Device", day.fiscal_device)
    result = call(device, "openDay", {"deviceID": int(device.device_id), "fiscalDayNo": int(day.fiscal_day_no)})
    day.operation_id = result.get("operationID")
    day.status = "FiscalDayOpened"
    day.save(ignore_permissions=True)
    return result


@frappe.whitelist()
def open_day(device_name):
    device = frappe.get_doc("ZIMRA Fiscal Device", device_name)
    day_no = (device.last_fiscal_day_no or 0) + 1
    day = frappe.get_doc({"doctype": "ZIMRA Fiscal Day", "fiscal_device": device.name, "fiscal_day_no": day_no, "status": "Pending Open"})
    day.insert(ignore_permissions=True)
    queue = frappe.get_doc({"doctype": "ZIMRA Offline Queue", "fiscal_device": device.name, "fiscal_day": day.name, "queue_type": "Open Day", "status": "Pending"})
    queue.insert(ignore_permissions=True)
    frappe.enqueue("erpnext_zimra.services.queue.process_device_queue", device_name=device.name, queue="short", enqueue_after_commit=True)
    return day.name
