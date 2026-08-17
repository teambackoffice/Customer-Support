import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """Add escalation tracking fields to HD Ticket"""
    
    # Define custom fields for HD Ticket
    custom_fields = {
        "HD Ticket": [
            {
                "fieldname": "escalation_sent",
                "fieldtype": "Check",
                "label": "Escalation Sent",
                "default": "0",
                "read_only": 1,
                "description": "Indicates if escalation notification has been sent for this ticket"
            },
            {
                "fieldname": "escalated_at",
                "fieldtype": "Datetime",
                "label": "Escalated At",
                "read_only": 1,
                "description": "Date and time when escalation notification was sent"
            }
        ]
    }
    
    # Create custom fields
    create_custom_fields(custom_fields, update=True)
    
    frappe.db.commit()
    
    print("Added escalation fields to HD Ticket")