import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add custom_workflow_status field to Task DocType"""
	
	custom_fields = {
		"Task": [
			{
				"fieldname": "custom_workflow_status",
				"label": "Workflow Status",
				"fieldtype": "Data",
				"insert_after": "status",
				"in_list_view": 1,
				"read_only": 1,
				"description": "Indicates custom workflow states like 'Extra Hour Requested'."
			}
		]
	}
	
	# Check if the field already exists before creating it
	if not frappe.db.exists("Custom Field", {"dt": "Task", "fieldname": "custom_workflow_status"}):
		create_custom_fields(custom_fields)
		frappe.db.commit()
		print("✅ Task workflow status field created successfully")