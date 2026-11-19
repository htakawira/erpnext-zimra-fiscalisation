import frappe
from erpnext_zimra.services.client import call


def transmit_receipt(receipt_name):
    receipt = frappe.get_doc("ZIMRA Fiscal Receipt", receipt_name)
    device = frappe.get_doc("ZIMRA Fiscal Device", receipt.fiscal_device)
    if not receipt.request_payload:
        frappe.throw("Receipt payload builder is not configured. No incomplete payload will be sent to FDMS.")
    result = call(device, "submitReceipt", frappe.parse_json(receipt.request_payload))
    receipt.operation_id = result.get("operationID")
    receipt.receipt_id = result.get("receiptID")
    receipt.server_date = result.get("serverDate")
    receipt.server_signature = frappe.as_json(result.get("receiptServerSignature"))
    receipt.status = "Accepted"
    receipt.save(ignore_permissions=True)
    return result


@frappe.whitelist()
def manual_fiscalise(receipt_name):
    receipt = frappe.get_doc("ZIMRA Fiscal Receipt", receipt_name)
    if receipt.status == "Accepted":
        return receipt.name
    queue = frappe.get_doc({"doctype": "ZIMRA Offline Queue", "fiscal_device": receipt.fiscal_device, "fiscal_day": receipt.fiscal_day, "fiscal_receipt": receipt.name, "queue_type": "Receipt", "status": "Pending"})
    queue.insert(ignore_permissions=True)
    frappe.enqueue("erpnext_zimra.services.queue.process_device_queue", device_name=receipt.fiscal_device, queue="short", enqueue_after_commit=True)
    return queue.name
