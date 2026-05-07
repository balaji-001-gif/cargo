import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, now_datetime


class Trip(Document):
    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def validate(self):
        self.validate_driver_vehicle_availability()
        self.validate_cargo_load()
        self.set_start_odometer_from_vehicle()

    def before_submit(self):
        """Final guard before submit — re-validate availability."""
        self.validate_driver_vehicle_availability()

    def on_submit(self):
        self.db_set("status", "Active")
        frappe.db.set_value("Vehicle", self.vehicle, "status", "On Trip")
        frappe.db.set_value("Driver", self.driver, "status", "On Trip")

        for row in self.waybills:
            frappe.db.set_value("Waybill", row.waybill, "status", "Scheduled")

        frappe.msgprint(
            frappe._("Trip {0} is now Active. Vehicle and Driver statuses updated.").format(
                self.name
            ),
            indicator="blue",
            title=frappe._("Trip Activated")
        )

    def on_cancel(self):
        self.db_set("status", "Cancelled")
        frappe.db.set_value("Vehicle", self.vehicle, "status", "Available")
        frappe.db.set_value("Driver", self.driver, "status", "Available")

        for row in self.waybills:
            current_status = frappe.db.get_value("Waybill", row.waybill, "status")
            # Only revert waybills that were set to Scheduled by this trip
            if current_status == "Scheduled":
                frappe.db.set_value("Waybill", row.waybill, "status", "Draft")

        frappe.msgprint(
            frappe._("Trip {0} has been Cancelled. Resources have been released.").format(
                self.name
            ),
            indicator="red",
            title=frappe._("Trip Cancelled")
        )

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def validate_driver_vehicle_availability(self):
        """
        On creation, ensure both the driver and vehicle are Available.
        On amendment/edit of existing docs, skip this check (db_set handles state).
        """
        if not self.is_new():
            return

        driver_status = frappe.db.get_value("Driver", self.driver, "status")
        vehicle_status = frappe.db.get_value("Vehicle", self.vehicle, "status")

        if driver_status != "Available":
            frappe.throw(
                frappe._(
                    "Driver {0} is currently not Available (Status: {1}). "
                    "Please select an available driver."
                ).format(self.driver, driver_status)
            )

        if vehicle_status != "Available":
            frappe.throw(
                frappe._(
                    "Vehicle {0} is currently not Available (Status: {1}). "
                    "Please select an available vehicle."
                ).format(self.vehicle, vehicle_status)
            )

    def validate_cargo_load(self):
        """Check that waybill totals do not exceed vehicle capacity."""
        if not self.waybills:
            return

        total_weight = sum(float(row.weight or 0) for row in self.waybills)
        total_volume = sum(float(row.volume or 0) for row in self.waybills)

        vehicle_cap = frappe.db.get_value(
            "Vehicle",
            self.vehicle,
            ["capacity_kg", "volume_m3"],
            as_dict=True
        )

        if not vehicle_cap:
            return

        if vehicle_cap.capacity_kg and total_weight > vehicle_cap.capacity_kg:
            frappe.throw(
                frappe._(
                    "Total cargo weight ({0} kg) exceeds vehicle {1} capacity "
                    "({2} kg). Please remove some waybills."
                ).format(total_weight, self.vehicle, vehicle_cap.capacity_kg)
            )

        if vehicle_cap.volume_m3 and total_volume > vehicle_cap.volume_m3:
            frappe.throw(
                frappe._(
                    "Total cargo volume ({0} m³) exceeds vehicle {1} capacity "
                    "({2} m³). Please remove some waybills."
                ).format(total_volume, self.vehicle, vehicle_cap.volume_m3)
            )

    def set_start_odometer_from_vehicle(self):
        """Auto-populate start odometer from vehicle current reading on new doc."""
        if self.is_new() and self.vehicle and not self.start_odometer:
            odometer = frappe.db.get_value(
                "Vehicle", self.vehicle, "current_odometer"
            )
            if odometer:
                self.start_odometer = odometer

    # ------------------------------------------------------------------
    # Custom method — called via frm.call() from JavaScript
    # called via frm.call({doc: frm.doc, method: 'complete_trip'})
    # ------------------------------------------------------------------

    def complete_trip(self, current_odometer, arrival_time):
        """
        Mark trip as Completed, update odometer, release driver and vehicle,
        and mark all linked waybills as Delivered.
        """
        if self.status != "Active":
            frappe.throw(
                frappe._("Only Active trips can be marked as Completed.")
            )

        current_odometer = float(current_odometer)
        start_odometer = float(self.start_odometer or 0)

        if current_odometer < start_odometer:
            frappe.throw(
                frappe._(
                    "End odometer ({0} km) cannot be less than start odometer ({1} km)."
                ).format(current_odometer, start_odometer)
            )

        # Update trip fields
        self.db_set("end_odometer", current_odometer)
        self.db_set("actual_arrival_time", arrival_time)
        self.db_set("status", "Completed")

        # Update vehicle odometer and release
        frappe.db.set_value(
            "Vehicle", self.vehicle,
            {
                "current_odometer": current_odometer,
                "status": "Available"
            }
        )

        # Release driver
        frappe.db.set_value("Driver", self.driver, "status", "Available")

        # Mark all waybills as Delivered and update linked Delivery Notes
        for row in self.waybills:
            frappe.db.set_value("Waybill", row.waybill, "status", "Delivered")

            delivery_note = frappe.db.get_value(
                "Waybill", row.waybill, "delivery_note"
            )
            if delivery_note:
                # Store the trip reference in Delivery Note's transporter doc no field
                frappe.db.set_value(
                    "Delivery Note", delivery_note, "lr_no", self.name
                )

        frappe.msgprint(
            frappe._(
                "Trip {0} completed successfully. "
                "Distance covered: {1} km."
            ).format(self.name, current_odometer - start_odometer),
            indicator="green",
            title=frappe._("Trip Completed")
        )

    def get_indicator(self):
        status_colors = {
            "Planned": "gray",
            "Active": "blue",
            "Completed": "green",
            "Cancelled": "red"
        }
        return status_colors.get(self.status, "gray"), self.status

