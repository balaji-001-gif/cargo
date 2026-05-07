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
        "on_submit": "cargo_flow.doctype.waybill.waybill.create_waybill_from_dn"
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

# ------------------------------------------------------------------
# Client Scripts
# ------------------------------------------------------------------
doctype_js = {
    "Delivery Note": "public/js/delivery_note_ui.js"
}

# ------------------------------------------------------------------
# Branding
# ------------------------------------------------------------------
app_logo_url = "/assets/cargo_flow/images/cargo_flow_logo.png"
app_icon = "truck"
app_color = "#3498db"

