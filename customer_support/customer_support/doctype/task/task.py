# Copyright (c) 2024, nehala and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

# Extend ERPNext's Task so its validation, progress and tree logic still run.
from erpnext.projects.doctype.task.task import Task as ERPNextTask


class Task(ERPNextTask):
	def validate(self):
		"""Validate task and calculate total hours"""
		super().validate()
		self.calculate_total_hours()
		
	def calculate_total_hours(self):
		"""Calculate total hours as allocated + extra approved hours"""
		allocated = flt(self.get("custom_allocated_hours", 0))
		extra_approved = flt(self.get("custom_extra_approved_hours", 0))
		self.custom_total_hours = allocated + extra_approved


@frappe.whitelist()
def create_task_from_hd_ticket(hd_ticket, assigned_to, allocated_hours, subject=None):
	"""Create a task from HD Ticket with allocated hours"""
	
	# Get HD Ticket details
	hd_ticket_doc = frappe.get_doc("HD Ticket", hd_ticket)
	
	# Create new task
	task = frappe.new_doc("Task")
	task.subject = subject or f"Task for HD Ticket: {hd_ticket}"
	task.custom_hd_ticket = hd_ticket
	task.custom_allocated_hours = float(allocated_hours)
	task.custom_extra_approved_hours = 0
	task.status = "Open"
	task.priority = "Medium"
	
	# Set project if HD Ticket has project
	if hasattr(hd_ticket_doc, 'project') and hd_ticket_doc.project:
		task.project = hd_ticket_doc.project
		
	task.insert()
	
	# After task creation, assign it to the user using ERPNext's assignment system
	try:
		frappe.get_doc({
			"doctype": "ToDo",
			"allocated_to": assigned_to,
			"reference_type": "Task",
			"reference_name": task.name,
			"description": f"Task assigned from HD Ticket: {hd_ticket}",
			"status": "Open"
		}).insert(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(f"Could not assign task to user: {str(e)}")
	
	# Update HD Ticket with task reference (if custom field exists)
	try:
		hd_ticket_doc.reload()
		if hasattr(hd_ticket_doc, 'custom_related_task'):
			hd_ticket_doc.custom_related_task = task.name
			hd_ticket_doc.save()
	except Exception as e:
		frappe.log_error(f"Could not update HD Ticket with task reference: {str(e)}")
		
	frappe.msgprint(f"Task {task.name} created successfully and assigned to {assigned_to}")
	
	return task.name


@frappe.whitelist()
def get_task_hours_summary(task):
	"""Get hours summary for a task"""
	task_doc = frappe.get_doc("Task", task)
	
	return {
		"allocated_hours": task_doc.get("custom_allocated_hours", 0),
		"extra_approved_hours": task_doc.get("custom_extra_approved_hours", 0), 
		"total_hours": task_doc.get("custom_total_hours", 0),
		"hd_ticket": task_doc.get("custom_hd_ticket")
	}