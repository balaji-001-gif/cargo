frappe.ui.form.on('Waybill', {
	refresh: function(frm) {
		// Status colour indicators
		const statusColors = {
			'Draft':     'gray',
			'Scheduled': 'blue',
			'Loaded':    'orange',
			'Delivered': 'green',
			'Cancelled': 'red'
		};
		const color = statusColors[frm.doc.status] || 'gray';
		frm.set_intro(
			__('Status: {0}', [frm.doc.status]),
			color
		);

		// Show link to related Delivery Note
		if (frm.doc.delivery_note && !frm.is_new()) {
			frm.add_custom_button(__('View Delivery Note'), function() {
				frappe.set_route('Form', 'Delivery Note', frm.doc.delivery_note);
			}, __('Links'));
		}
	},

	delivery_note: function(frm) {
		if (!frm.doc.delivery_note) return;

		frappe.db.get_doc('Delivery Note', frm.doc.delivery_note)
			.then(dn => {
				frm.set_value('customer', dn.customer);

				// Populate destination address
				if (dn.shipping_address) {
					frm.set_value('destination_address', dn.shipping_address);
				}

				// Populate origin warehouse from first item
				if (dn.items && dn.items.length > 0 && dn.items[0].warehouse) {
					frm.set_value('origin_warehouse', dn.items[0].warehouse);
				}
			});
	},

	weight: function(frm) {
		if (frm.doc.weight <= 0) {
			frappe.msgprint(__('Weight must be greater than zero.'));
			frm.set_value('weight', 1);
		}
	},

	volume: function(frm) {
		if (frm.doc.volume <= 0) {
			frappe.msgprint(__('Volume must be greater than zero.'));
			frm.set_value('volume', 1);
		}
	}
});
