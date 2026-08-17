import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add custom fields to HD Ticket:
	- custom_assigned_to (Link to User)
	- custom_estimation_hours (Float)
	"""
	custom_fields = {
		"HD Ticket": [
			{
				"fieldname": "custom_assigned_to",
				"fieldtype": "Link",
				"options": "User",
				"label": "Assigned To",
				"insert_after": "custom_module",
				"description": "User assigned to handle this ticket",
				"in_list_view": 1,
				"in_standard_filter": 1,
				"bold": 0,
				"allow_on_submit": 0,
				"translatable": 0,
			},
			{
				"fieldname": "custom_estimation_hours",
				"fieldtype": "Float",
				"label": "Estimation Hours",
				"insert_after": "custom_assigned_to",
				"description": "Estimated hours to resolve this ticket",
				"in_list_view": 1,
				"in_standard_filter": 0,
				"bold": 0,
				"allow_on_submit": 0,
				"precision": "2",
				"translatable": 0,
			},
		]
	}

	create_custom_fields(custom_fields, update=True)

	frappe.db.commit()
	print("Custom fields 'custom_assigned_to' and 'custom_estimation_hours' added to HD Ticket DocType")
