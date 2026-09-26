import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add custom_company field to User (used for HD Ticket naming)."""
	create_custom_fields(
		{
			"User": [
				{
					"fieldname": "custom_company",
					"fieldtype": "Link",
					"options": "Company",
					"label": "Company",
					"insert_after": "username",
					"description": "Default company for this user (used for HD Ticket naming)",
					"in_standard_filter": 1,
				}
			]
		},
		update=True,
	)
	frappe.db.commit()
	print("custom_company field added to User")
