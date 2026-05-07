frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            // Check if Waybill exists for this Delivery Note
            frappe.db.get_value('Waybill', { 'delivery_note': frm.doc.name }, 'name')
                .then(r => {
                    if (r && r.message && r.message.name) {
                        frm.add_custom_button(__('View Waybill'), function() {
                            frappe.set_route('Form', 'Waybill', r.message.name);
                        }, __('Logistics'));
                    }
                });
        }
    }
});
