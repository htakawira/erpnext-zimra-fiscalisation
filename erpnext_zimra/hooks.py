app_name = "erpnext_zimra"
app_title = "ERPNext ZIMRA Fiscalisation"
app_publisher = "Community"
app_description = "ZIMRA Fiscal Device Gateway integration for ERPNext"
app_email = ""
app_license = "MIT"

required_apps = ["frappe", "erpnext"]
doctype_js = {"Sales Invoice": "public/js/sales_invoice.js"}
doc_events = {
    "Sales Invoice": {
        "on_submit": "erpnext_zimra.events.sales_invoice.on_submit",
        "on_cancel": "erpnext_zimra.events.sales_invoice.on_cancel",
    }
}
scheduler_events = {"cron": {"* * * * *": ["erpnext_zimra.services.queue.process_pending"]}}
