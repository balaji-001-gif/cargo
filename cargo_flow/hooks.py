app_name = "cargo_flow"
app_title = "Cargo Flow"
app_publisher = "Your Organization"
app_description = "Logistics and Transportation Management"
app_email = "info@yourorg.com"
app_license = "mit"

# ------------------------------------------------------------------
# Document Events — integrations with ERPNext core doctypes
# ------------------------------------------------------------------
doc_events = {
    "Delivery Note": {
        "on_submit": "cargo_flow.cargo_flow.doctype.waybill.waybill.create_waybill_from_dn"
    }
}

# ------------------------------------------------------------------
# Fixtures — export workspace so it ships with the app
# ------------------------------------------------------------------
fixtures = [
    {
        "dt": "Workspace",
        "filters": [["name", "=", "Cargo Flow Dashboard"]]
    }
]
