import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add custom fields to HD Ticket DocType for Task integration"""
	
	custom_fields = {
		"HD Ticket": [
			{
				"fieldname": "custom_related_task",
				"label": "Related Task", 
				"fieldtype": "Link",
				"options": "Task",
				"insert_after": "custom_assigned_to",
				"read_only": 1,
				"description": "Task created from this HD Ticket"
			}
		]
	}
	
	create_custom_fields(custom_fields)
	print("✅ HD Ticket task-related custom field created successfully")