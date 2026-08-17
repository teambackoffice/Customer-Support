import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add ticket-sync provenance fields to HD Ticket."""
	custom_fields = {
		"HD Ticket": [
			{
				"fieldname": "custom_ticket_source",
				"label": "Ticket Source",
				"fieldtype": "Data",
				"insert_after": "custom_customer",
				"read_only": 1,
				"in_list_view": 1,
				"no_copy": 1,
				"description": "Site this ticket was synced from (empty for native tickets)",
			},
			{
				"fieldname": "custom_remote_ticket",
				"label": "Remote Ticket",
				"fieldtype": "Data",
				"insert_after": "custom_ticket_source",
				"read_only": 1,
				"no_copy": 1,
				"description": "Original ticket name on the source site",
			},
			{
				"fieldname": "custom_synced_on",
				"label": "Synced On",
				"fieldtype": "Datetime",
				"insert_after": "custom_remote_ticket",
				"read_only": 1,
				"no_copy": 1,
				"description": "When this ticket was last synced",
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()
	print("Ticket sync provenance fields added to HD Ticket")
