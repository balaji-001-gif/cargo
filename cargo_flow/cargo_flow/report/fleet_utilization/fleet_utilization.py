import frappe
from frappe import _


def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Vehicle"),
            "fieldname": "vehicle",
            "fieldtype": "Link",
            "options": "Vehicle",
            "width": 160
        },
        {
            "label": _("Model"),
            "fieldname": "model",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("Current Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 130
        },
        {
            "label": _("Total Trips"),
            "fieldname": "total_trips",
            "fieldtype": "Int",
            "width": 110
        },
        {
            "label": _("Completed Trips"),
            "fieldname": "completed_trips",
            "fieldtype": "Int",
            "width": 130
        },
        {
            "label": _("Total Distance (km)"),
            "fieldname": "total_distance",
            "fieldtype": "Float",
            "precision": 2,
            "width": 160
        },
        {
            "label": _("Current Odometer (km)"),
            "fieldname": "current_odometer",
            "fieldtype": "Float",
            "precision": 2,
            "width": 170
        }
    ]


def get_data(filters):
    """
    Aggregate trip statistics per vehicle.
    Joins Vehicle with submitted Trips only (docstatus = 1).
    """
    query = """
        SELECT
            v.license_plate          AS vehicle,
            v.model                  AS model,
            v.status                 AS status,
            v.current_odometer       AS current_odometer,
            COUNT(t.name)            AS total_trips,
            SUM(
                CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END
            )                        AS completed_trips,
            SUM(
                CASE
                    WHEN t.status = 'Completed'
                    THEN IFNULL(t.end_odometer, 0) - IFNULL(t.start_odometer, 0)
                    ELSE 0
                END
            )                        AS total_distance
        FROM
            `tabVehicle` v
        LEFT JOIN
            `tabTrip` t
            ON  t.vehicle   = v.name
            AND t.docstatus = 1
        GROUP BY
            v.license_plate,
            v.model,
            v.status,
            v.current_odometer
        ORDER BY
            total_trips DESC
    """
    return frappe.db.sql(query, as_dict=True)
