import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add custom fields for HD Ticket follow-up/escalation functionality"""
	
	custom_fields = {
		"HD Ticket": [
			{
				"fieldname": "custom_parent_ticket",
				"label": "Parent Ticket", 
				"fieldtype": "Link",
				"options": "HD Ticket",
				"insert_after": "custom_customer",
				"read_only": 1,
				"description": "Original ticket if this is a follow-up"
			},
			{
				"fieldname": "custom_follow_up_sequence",
				"label": "Follow-up Sequence",
				"fieldtype": "Int",
				"insert_after": "custom_parent_ticket",
				"read_only": 1,
				"default": 0,
				"description": "Sequence number for follow-up tickets (0 = original)"
			},
			{
				"fieldname": "custom_is_follow_up",
				"label": "Is Follow-up Ticket",
				"fieldtype": "Check",
				"insert_after": "custom_follow_up_sequence",
				"read_only": 1,
				"default": 0
			}
		]
	}
	
	create_custom_fields(custom_fields)
	print("✅ HD Ticket follow-up fields created successfully")