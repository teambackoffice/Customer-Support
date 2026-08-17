# Copyright (c) 2024, nehala and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class ExtraHourRequest(Document):
	def validate(self):
		"""Validate the extra hour request"""
		self.validate_task_link()
		self.set_employee_and_hd_ticket()
		
	def validate_task_link(self):
		"""Ensure task exists and is valid"""
		if not self.task:
			frappe.throw("Task is required")
			
		task_doc = frappe.get_doc("Task", self.task)
		if not task_doc.custom_hd_ticket:
			frappe.throw("Task must be linked to an HD Ticket to request extra hours")
			
	def set_employee_and_hd_ticket(self):
		"""Auto-populate employee and HD ticket from task"""
		if self.task:
			task_doc = frappe.get_doc("Task", self.task)
			
			# Set HD Ticket from task
			if task_doc.custom_hd_ticket:
				self.hd_ticket = task_doc.custom_hd_ticket
				
			# Set employee from task assignment (via ToDo)
			if not self.employee:
				# Get assigned user from ToDo
				todo = frappe.db.get_value("ToDo", 
					{
						"reference_type": "Task",
						"reference_name": self.task,
						"status": "Open"
					}, 
					"allocated_to"
				)
				
				if todo:
					# Get employee from user
					employee = frappe.db.get_value("Employee", {"user_id": todo}, "name")
					if employee:
						self.employee = employee
			
	def on_update(self):
		"""Handle status changes"""
		if self.has_value_changed("status") and self.status in ["Approved", "Rejected"]:
			self.approved_by = frappe.session.user
			self.approval_date = now()
			
			if self.status == "Approved":
				self.update_task_hours()
				self.send_approval_notification()
			elif self.status == "Rejected":
				self.send_rejection_notification()
				
	def update_task_hours(self):
		"""Update task with approved extra hours"""
		if self.status == "Approved" and self.requested_hours:
			task_doc = frappe.get_doc("Task", self.task)
			
			# Update extra approved hours
			current_extra = task_doc.get("custom_extra_approved_hours", 0)
			task_doc.custom_extra_approved_hours = float(current_extra) + float(self.requested_hours)

			# Also update the total estimated and expected time for the task
			current_estimated = task_doc.get("custom_estimated_hours", 0)
			task_doc.custom_estimated_hours = float(current_estimated) + float(self.requested_hours)

			current_expected = task_doc.get("expected_time", 0)
			task_doc.expected_time = float(current_expected) + float(self.requested_hours)
			
			# Set the custom workflow status on the task to show extra hours were approved
			task_doc.custom_workflow_status = "Extra Hour Requested"
			
			task_doc.save(ignore_permissions=True)
			
			frappe.msgprint(f"Task {self.task} updated with {self.requested_hours} additional hours")
			
	def send_approval_notification(self):
		"""Send notification when request is approved"""
		if self.employee:
			employee_user = frappe.db.get_value("Employee", self.employee, "user_id")
			if employee_user:
				frappe.sendmail(
					recipients=[employee_user],
					subject=f"Extra Hour Request Approved - {self.name}",
					message=f"""
					<p>Your request for {self.requested_hours} extra hours has been approved.</p>
					<p><strong>Task:</strong> {self.task}</p>
					<p><strong>HD Ticket:</strong> {self.hd_ticket}</p>
					<p><strong>Approved By:</strong> {self.approved_by}</p>
					<p><strong>Manager Comments:</strong> {self.comments or 'No comments'}</p>
					"""
				)
				
	def send_rejection_notification(self):
		"""Send notification when request is rejected"""
		if self.employee:
			employee_user = frappe.db.get_value("Employee", self.employee, "user_id")
			if employee_user:
				frappe.sendmail(
					recipients=[employee_user],
					subject=f"Extra Hour Request Rejected - {self.name}",
					message=f"""
					<p>Your request for {self.requested_hours} extra hours has been rejected.</p>
					<p><strong>Task:</strong> {self.task}</p>
					<p><strong>HD Ticket:</strong> {self.hd_ticket}</p>
					<p><strong>Rejected By:</strong> {self.approved_by}</p>
					<p><strong>Manager Comments:</strong> {self.comments or 'No comments provided'}</p>
					"""
				)


@frappe.whitelist()
def create_extra_hour_request(task, requested_hours, reason):
	"""Create a new extra hour request from task"""
	doc = frappe.new_doc("Extra Hour Request")
	doc.task = task
	doc.requested_hours = float(requested_hours)
	doc.reason = reason
	doc.insert()
	
	return doc.name


def send_manager_notification(doc, method=None):
	"""Send notification to managers when new request is created"""
	# Get users with Support Manager role
	managers = frappe.get_all("Has Role", 
		filters={"role": "Support Manager", "parenttype": "User"},
		fields=["parent as user"]
	)
	
	if managers:
		manager_emails = [m.user for m in managers]
		frappe.sendmail(
			recipients=manager_emails,
			subject=f"New Extra Hour Request - {doc.name}",
			message=f"""
			<p>A new extra hour request has been submitted:</p>
			<p><strong>Request ID:</strong> {doc.name}</p>
			<p><strong>Employee:</strong> {doc.employee}</p>
			<p><strong>Task:</strong> {doc.task}</p>
			<p><strong>HD Ticket:</strong> {doc.hd_ticket}</p>
			<p><strong>Requested Hours:</strong> {doc.requested_hours}</p>
			<p><strong>Reason:</strong> {doc.reason}</p>
			<p><a href="/app/extra-hour-request/{doc.name}">Review Request</a></p>
			"""
		)