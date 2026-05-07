// -----------------------------------------------------------------------
// Trip Form Controller
// -----------------------------------------------------------------------
frappe.ui.form.on('Trip', {

	setup: function(frm) {
		// Filter vehicle link field to show only Available vehicles
		frm.set_query('vehicle', function() {
			return {
				filters: { 'status': 'Available' }
			};
		});

		// Filter driver link field to show only Available drivers
		frm.set_query('driver', function() {
			return {
				filters: { 'status': 'Available' }
			};
		});
	},

	refresh: function(frm) {
		// Status indicator banners
		const statusMessages = {
			'Planned':   { msg: 'Trip is planned and awaiting submission.', color: 'gray' },
			'Active':    { msg: 'Trip is currently Active and in progress.', color: 'blue' },
			'Completed': { msg: 'Trip has been Completed.', color: 'green' },
			'Cancelled': { msg: 'Trip has been Cancelled.', color: 'red' }
		};

		const info = statusMessages[frm.doc.status];
		if (info) frm.set_intro(__(info.msg), info.color);

		// Show "Complete Trip" button only on submitted + Active trips
		if (frm.doc.docstatus === 1 && frm.doc.status === 'Active') {
			frm.add_custom_button(__('Complete Trip'), function() {
				frm.trigger('show_complete_trip_dialog');
			}, __('Actions'));
		}
	},

	show_complete_trip_dialog: function(frm) {
		const dialog = new frappe.ui.Dialog({
			title: __('Complete Trip — {0}', [frm.doc.name]),
			fields: [
				{
					label: __('Final Odometer Reading (km)'),
					fieldname: 'end_odometer',
					fieldtype: 'Float',
					reqd: 1,
					default: frm.doc.start_odometer || 0,
					description: __('Must be greater than or equal to start: {0} km',
						[frm.doc.start_odometer || 0])
				},
				{
					label: __('Actual Arrival Date & Time'),
					fieldname: 'actual_arrival_time',
					fieldtype: 'Datetime',
					reqd: 1,
					default: frappe.datetime.now_datetime()
				}
			],
			primary_action_label: __('Mark as Completed'),
			primary_action: function(values) {
				if (values.end_odometer < (frm.doc.start_odometer || 0)) {
					frappe.msgprint({
						message: __('End odometer ({0} km) must be ≥ start odometer ({1} km).',
							[values.end_odometer, frm.doc.start_odometer || 0]),
						indicator: 'red',
						title: __('Invalid Odometer Reading')
					});
					return;
				}

				dialog.hide();

				frm.call({
					doc: frm.doc,
					method: 'complete_trip',
					args: {
						current_odometer: values.end_odometer,
						arrival_time: values.actual_arrival_time
					},
					freeze: true,
					freeze_message: __('Completing trip, please wait...'),
					callback: function(r) {
						if (!r.exc) {
							frappe.show_alert({
								message: __('Trip {0} has been marked as Completed.', [frm.doc.name]),
								indicator: 'green'
							}, 5);
							frm.reload_doc();
						}
					}
				});
			}
		});

		dialog.show();
	},

	vehicle: function(frm) {
		if (!frm.doc.vehicle) return;

		// Auto-fill start odometer from selected vehicle
		frappe.db.get_value('Vehicle', frm.doc.vehicle, 'current_odometer')
			.then(r => {
				if (r && r.message) {
					frm.set_value('start_odometer', r.message.current_odometer || 0);
				}
			});
	}
});

// -----------------------------------------------------------------------
// Trip Waybill Child Table Controller
// -----------------------------------------------------------------------
frappe.ui.form.on('Trip Waybill', {
	waybill: function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.waybill) return;

		// Auto-fill customer, weight, volume from linked waybill
		frappe.db.get_doc('Waybill', row.waybill)
			.then(wb => {
				frappe.model.set_value(cdt, cdn, 'customer', wb.customer);
				frappe.model.set_value(cdt, cdn, 'weight',   wb.weight);
				frappe.model.set_value(cdt, cdn, 'volume',   wb.volume);
			})
			.then(() => {
				// Re-validate cargo load totals after each waybill is added
				frm.trigger('validate_cargo_totals');
			});
	}
});

// -----------------------------------------------------------------------
// Client-side cargo load summary display
// -----------------------------------------------------------------------
frappe.ui.form.on('Trip', {
	validate_cargo_totals: function(frm) {
		if (!frm.doc.waybills || !frm.doc.vehicle) return;

		const totalWeight = frm.doc.waybills.reduce(
			(sum, row) => sum + (row.weight || 0), 0
		);
		const totalVolume = frm.doc.waybills.reduce(
			(sum, row) => sum + (row.volume || 0), 0
		);

		frappe.db.get_value(
			'Vehicle',
			frm.doc.vehicle,
			['capacity_kg', 'volume_m3']
		).then(r => {
			if (!r || !r.message) return;
			const cap = r.message;

			let warnings = [];

			if (cap.capacity_kg && totalWeight > cap.capacity_kg) {
				warnings.push(
					__('⚠️ Weight {0} kg exceeds vehicle capacity {1} kg.',
						[totalWeight.toFixed(2), cap.capacity_kg])
				);
			}
			if (cap.volume_m3 && totalVolume > cap.volume_m3) {
				warnings.push(
					__('⚠️ Volume {0} m³ exceeds vehicle capacity {1} m³.',
						[totalVolume.toFixed(2), cap.volume_m3])
				);
			}

			if (warnings.length) {
				frappe.msgprint({
					message: warnings.join('<br>'),
					indicator: 'orange',
					title: __('Cargo Capacity Warning')
				});
			}
		});
	}
});
