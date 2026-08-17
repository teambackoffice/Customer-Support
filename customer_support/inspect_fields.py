import frappe

def run():
    fields = [
        "custom_module",
        "custom_screenshot_",
        "custom_assigned_to",
        "custom_estimation_hours",
        "custom_related_task",
        "custom_reference_document",
        "custom_reference_document_name",
        "custom_estimated_resolution_hour",
        "custom_customer"
    ]
    
    cfs = frappe.get_all(
        "Custom Field",
        filters={"dt": "HD Ticket", "fieldname": ["in", fields]},
        fields=["fieldname", "label", "fieldtype", "hidden", "read_only", "depends_on"]
    )
    for cf in cfs:
        print(cf)
