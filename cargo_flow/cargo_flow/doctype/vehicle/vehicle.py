import frappe
from frappe.model.document import Document


class Vehicle(Document):
    def validate(self):
        self.validate_capacity()

    def validate_capacity(self):
        if self.capacity_kg is not None and self.capacity_kg < 0:
            frappe.throw(frappe._("Capacity (Kg) cannot be negative."))
        if self.volume_m3 is not None and self.volume_m3 < 0:
            frappe.throw(frappe._("Volume (m³) cannot be negative."))
        if self.current_odometer is not None and self.current_odometer < 0:
            frappe.throw(frappe._("Current Odometer cannot be negative."))
