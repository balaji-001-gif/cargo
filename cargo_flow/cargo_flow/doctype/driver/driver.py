import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_days


class Driver(Document):
    def validate(self):
        self.validate_license_expiry()

    def validate_license_expiry(self):
        if not self.license_expiry:
            return

        expiry_date = getdate(self.license_expiry)
        today_date = getdate(today())

        if expiry_date < today_date:
            frappe.throw(
                frappe._(
                    "Driver's license has already expired on {0}. "
                    "Please update the expiry date before saving."
                ).format(self.license_expiry)
            )

        # Warn if expiring within 30 days
        warning_threshold = add_days(today_date, 30)
        if expiry_date <= warning_threshold:
            frappe.msgprint(
                frappe._(
                    "Warning: Driver {0}'s license expires on {1} "
                    "(within 30 days). Please arrange renewal."
                ).format(self.driver_name, self.license_expiry),
                indicator="orange",
                title=frappe._("License Expiry Warning")
            )
