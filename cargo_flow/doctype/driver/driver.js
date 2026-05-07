frappe.ui.form.on('Driver', {
	refresh: function(frm) {
		if (!frm.doc.license_expiry) return;

		const today = frappe.datetime.get_today();
		const expiry = frm.doc.license_expiry;
		const daysLeft = frappe.datetime.get_diff(expiry, today);

		if (daysLeft < 0) {
			frm.set_intro(
				__('⛔ This driver\'s license has EXPIRED on {0}. Cannot be assigned to trips.',
					[expiry]),
				'red'
			);
		} else if (daysLeft <= 30) {
			frm.set_intro(
				__('⚠️ This driver\'s license expires on {0} ({1} days remaining). Please renew soon.',
					[expiry, daysLeft]),
				'orange'
			);
		} else {
			frm.set_intro(
				__('✅ License valid until {0} ({1} days remaining).',
					[expiry, daysLeft]),
				'green'
			);
		}
	},

	license_expiry: function(frm) {
		// Re-trigger refresh to update intro banner
		frm.trigger('refresh');
	}
});
