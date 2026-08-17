import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add custom customer field to HD Ticket DocType"""
	
	custom_fields = {
		"HD Ticket": [
			{
				"fieldname": "custom_customer",
				"label": "Customer", 
				"fieldtype": "Data",
				"insert_after": "subject",
				"in_list_view": 1,
				"read_only": 1,
				"description": "Auto-populated with company name from user"
			}
		]
	}
	
	create_custom_fields(custom_fields)
	print("✅ HD Ticket customer field created successfully")