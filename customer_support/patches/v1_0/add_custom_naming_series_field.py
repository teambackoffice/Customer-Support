import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add custom_naming_series field to HD Ticket DocType
	"""
	custom_fields = {
		"HD Ticket": [
			{
				"fieldname": "custom_naming_series",
				"fieldtype": "Data",
				"label": "Custom Naming Series",
				"insert_after": "name",
				"read_only": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"description": "Auto-generated ticket ID in format: <CompanyAbbr><DDMMYY><Sequence>",
				"allow_on_submit": 0,
				"bold": 1,
				"unique": 0,
				"no_copy": 1,
				"translatable": 0,
			}
		]
	}

	create_custom_fields(custom_fields, update=True)

	frappe.db.commit()
	print("Custom field 'custom_naming_series' added to HD Ticket DocType")
