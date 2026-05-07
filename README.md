# Cargo Flow – Logistics & Transportation Management for ERPNext v15+

Cargo Flow extends ERPNext with comprehensive logistics capabilities:

- **Waybill** generation from Delivery Notes
- **Trip** management with vehicle and driver assignment
- **Fleet utilization** reporting
- **Real-time status notifications**

## Installation

```bash
bench get-app https://github.com/balaji-001-gif/cargo.git
bench --site yoursite.local install-app cargo_flow
bench --site yoursite.local migrate
```

## Features
- Auto-generate Waybills on Delivery Note submission
- Validate driver and vehicle availability before trip creation
- Enforce vehicle weight and volume capacity limits
- Track odometer readings per trip
- Fleet utilization script report
- Email notifications on trip status changes
- Cargo Flow workspace dashboard
