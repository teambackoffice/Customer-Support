import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    """Add reference document and reference document name fields to HD Ticket"""
    
    # Check if fields already exist
    if frappe.db.exists("Custom Field", {"dt": "HD Ticket", "fieldname": "custom_reference_document"}):
        print("Custom fields already exist, skipping...")
        return
    
    # Create Reference Document field (DocType selector)
    create_custom_field("HD Ticket", {
        "fieldname": "custom_reference_document",
        "label": "Reference Document",
        "fieldtype": "Link",
        "options": "DocType",
        "insert_after": "custom_module",
        "description": "The DocType from which this ticket was created (e.g., Sales Invoice, Sales Order)",
        "read_only": 1,
        "in_list_view": 1,
        "in_standard_filter": 1,
        "allow_on_submit": 0,
        "translatable": 0
    })
    
    # Create Reference Document Name field (Dynamic Link)
    create_custom_field("HD Ticket", {
        "fieldname": "custom_reference_document_name", 
        "label": "Reference Document Name",
        "fieldtype": "Dynamic Link",
        "options": "custom_reference_document",
        "insert_after": "custom_reference_document",
        "description": "The specific document name (e.g., SINV-2024-00001, SO-2024-00001)",
        "read_only": 1,
        "in_list_view": 1,
        "in_standard_filter": 1,
        "allow_on_submit": 0,
        "translatable": 0
    })
    
    frappe.db.commit()
    print("Successfully added HD Ticket reference fields!")