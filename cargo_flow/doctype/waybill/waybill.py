import frappe
from frappe.model.document import Document


class Waybill(Document):
    def validate(self):
        self.validate_weight_volume()
        self.sync_customer_from_delivery_note()

    def validate_weight_volume(self):
        if self.weight is not None and self.weight <= 0:
            frappe.throw(frappe._("Weight must be greater than zero."))
        if self.volume is not None and self.volume <= 0:
            frappe.throw(frappe._("Volume must be greater than zero."))

    def sync_customer_from_delivery_note(self):
        """Auto-populate customer from linked Delivery Note if not set."""
        if self.delivery_note and not self.customer:
            customer = frappe.db.get_value(
                "Delivery Note", self.delivery_note, "customer"
            )
            if customer:
                self.customer = customer


def create_waybill_from_dn(doc, method):
    """
    Hook handler called on Delivery Note on_submit.
    Registered in hooks.py → doc_events.
    """
    # Guard: prevent duplicate waybills for the same delivery note
    if frappe.db.exists("Waybill", {"delivery_note": doc.name}):
        return

    # Calculate total weight from item weight_per_unit
    total_weight = 0.0
    origin_warehouse = None

    for item in doc.items:
        weight_per_unit = (
            frappe.db.get_value("Item", item.item_code, "weight_per_unit") or 0.0
        )
        total_weight += float(weight_per_unit) * float(item.qty or 0)
        if not origin_warehouse:
            origin_warehouse = item.warehouse

    # Resolve destination address from shipping address name
    destination_address = "Not Specified"
    if doc.shipping_address_name:
        addr = frappe.db.get_value(
            "Address",
            doc.shipping_address_name,
            ["address_line1", "city", "country"],
            as_dict=True
        )
        if addr:
            destination_address = ", ".join(
                filter(None, [addr.address_line1, addr.city, addr.country])
            )
    elif doc.shipping_address:
        destination_address = doc.shipping_address

    waybill = frappe.get_doc({
        "doctype": "Waybill",
        "customer": doc.customer,
        "delivery_note": doc.name,
        "origin_warehouse": origin_warehouse,
        "destination_address": destination_address,
        "weight": total_weight if total_weight > 0 else 10.0,
        "volume": 1.0,  # Default placeholder — can be updated manually
        "status": "Draft"
    })

    waybill.insert(ignore_permissions=True)
    frappe.msgprint(
        frappe._(
            "Waybill {0} successfully generated for Delivery Note {1}."
        ).format(waybill.name, doc.name),
        indicator="green",
        title=frappe._("Waybill Created")
    )
