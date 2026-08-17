import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add custom fields to Task DocType for HD Ticket integration"""
	
	custom_fields = {
		"Task": [
			{
				"fieldname": "custom_hd_ticket",
				"label": "HD Ticket", 
				"fieldtype": "Link",
				"options": "HD Ticket",
				"insert_after": "subject",
				"in_list_view": 1,
				"read_only": 1
			},
			{
				"fieldname": "custom_allocated_hours",
				"label": "Allocated Hours",
				"fieldtype": "Float",
				"precision": "2",
				"insert_after": "expected_end_date",
				"in_list_view": 1
			},
			{
				"fieldname": "custom_extra_approved_hours", 
				"label": "Extra Approved Hours",
				"fieldtype": "Float",
				"precision": "2",
				"insert_after": "custom_allocated_hours",
				"default": "0"
			},
			{
				"fieldname": "custom_total_hours",
				"label": "Total Hours",
				"fieldtype": "Float", 
				"precision": "2",
				"insert_after": "custom_extra_approved_hours",
				"read_only": 1,
				"in_list_view": 1,
				"description": "Allocated Hours + Extra Approved Hours"
			}
		]
	}
	
	create_custom_fields(custom_fields)
	print("✅ Task custom fields created successfully")