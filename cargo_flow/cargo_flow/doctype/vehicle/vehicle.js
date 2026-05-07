frappe.ui.form.on('Vehicle', {
	refresh: function(frm) {
		// Show status colour indicator
		if (frm.doc.status === 'On Trip') {
			frm.set_intro(__('This vehicle is currently on an active trip.'), 'blue');
		} else if (frm.doc.status === 'Maintenance') {
			frm.set_intro(__('This vehicle is under maintenance and cannot be assigned.'), 'orange');
		} else if (frm.doc.status === 'Out of Service') {
			frm.set_intro(__('This vehicle is out of service.'), 'red');
		} else if (frm.doc.status === 'Available') {
			frm.set_intro(__('This vehicle is available for assignment.'), 'green');
		}
	},

	capacity_kg: function(frm) {
		if (frm.doc.capacity_kg < 0) {
			frappe.msgprint(__('Capacity (Kg) cannot be negative.'));
			frm.set_value('capacity_kg', 0);
		}
	},

	volume_m3: function(frm) {
		if (frm.doc.volume_m3 < 0) {
			frappe.msgprint(__('Volume cannot be negative.'));
			frm.set_value('volume_m3', 0);
		}
	}
});
