frappe.ui.form.on("Sales Invoice", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Fiscalise with ZIMRA"), () => {
                frappe.call({method: "erpnext_zimra.events.sales_invoice.enqueue_invoice", args: {invoice_name: frm.doc.name}, freeze: true, callback: () => frm.reload_doc()});
            }, __("ZIMRA"));
        }
    }
});
