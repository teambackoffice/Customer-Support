import frappe
from frappe import _
from frappe.utils import now_datetime
from frappe.model.document import Document


class HDTicket(Document):
	def validate(self):
		"""
		Validate that if estimation hours are provided, the ticket is assigned.
		"""
		if self.custom_estimation_hours and not self.custom_assigned_to:
			frappe.throw(_("Please assign the ticket to a user before adding estimation hours."))


def get_company_abbreviation(user):
	"""
	Fetch company abbreviation from User's custom_company field
	
	Data Flow:
	User (Logged-in User)
	  ↓ custom_company (Link to Company)
	  ↓ Company.abbr
	
	Args:
	    user: User email/name
	
	Returns:
	    str: Company abbreviation
	"""
	# Get the custom_company field from User DocType
	user_doc = frappe.get_doc("User", user)

	if not hasattr(user_doc, "custom_company") or not user_doc.custom_company:
		frappe.throw(
			_(
				"No company assigned to user {0}. Please set the custom_company field in the User record."
			).format(user)
		)

	# Get the company abbreviation from Company DocType
	company = frappe.get_doc("Company", user_doc.custom_company)

	return company.abbr


def get_next_sequence(company_abbr):
	"""
	Get the next sequence number for the given company abbreviation.
	The sequence is maintained per company and continues incrementing (does not reset daily).
	
	Args:
	    company_abbr: Company abbreviation (e.g., 'HYD', 'ABC')
	
	Returns:
	    int: Next sequence number
	"""
	# Query for the latest non-follow-up HD Ticket with the same company abbreviation.
	# The custom_naming_series field format is: <CompanyAbbr><DDMMYY><Sequence>
	# Follow-up tickets have a "-R<n>" suffix (e.g. TBO08082615-R1) and must be
	# excluded, otherwise their suffix digits corrupt the extracted sequence.

	existing_tickets = frappe.get_all(
		"HD Ticket",
		filters=[
			["custom_naming_series", "like", f"{company_abbr}%"],
			["custom_naming_series", "not like", "%-R%"],
			["custom_is_follow_up", "!=", 1],
		],
		fields=["custom_naming_series"],
		order_by="creation desc",
		limit=1,
	)

	if not existing_tickets:
		# First ticket for this company
		return 1

	# Extract the sequence number from the last ticket
	last_naming_series = existing_tickets[0].custom_naming_series

	# The sequence is everything after the abbreviation and the 6-digit date.
	# Example: HYD26062601 -> sequence is 01
	# Example: TBO05082649 -> sequence is 49
	try:
		sequence_str = last_naming_series[len(company_abbr) + 6:]
		last_sequence = int(sequence_str)
		return last_sequence + 1
	except (ValueError, IndexError):
		# If we can't parse the sequence, start from 1
		frappe.log_error(
			f"Could not parse sequence from naming series: {last_naming_series}",
			"HD Ticket Naming Series Error",
		)
		return 1


def set_custom_naming_series(doc, method=None):
	"""
	Hook function to set custom naming series for HD Ticket
	This is called via document event hook before insert
	
	Args:
	    doc: HD Ticket document
	    method: Hook method name (unused but required by Frappe)
	"""
	# Check if this is a follow-up ticket
	if doc.get("custom_is_follow_up") and doc.get("custom_parent_ticket"):
		# Generate follow-up ticket name
		set_follow_up_naming_series(doc)
	else:
		# Generate regular ticket name
		set_regular_naming_series(doc)


def set_regular_naming_series(doc):
	"""Generate naming series for regular (non-follow-up) tickets"""
	# Get the logged-in user
	user = frappe.session.user

	# Fetch company abbreviation from User's custom_company field
	company_abbr = get_company_abbreviation(user)

	if not company_abbr:
		frappe.throw(
			_("Company abbreviation not found. Please ensure the user has a company assigned.")
		)

	# Generate date portion in DDMMYY format
	date_portion = now_datetime().strftime("%d%m%y")

	# Generate the sequence number for this company
	sequence = get_next_sequence(company_abbr)

	# Format: <CompanyAbbr><DDMMYY><Sequence>
	naming_series = f"{company_abbr}{date_portion}{sequence:02d}"

	# Store in custom_naming_series field
	doc.custom_naming_series = naming_series

	# Set as document name
	doc.name = naming_series


def set_follow_up_naming_series(doc):
	"""Generate naming series for follow-up tickets"""
	if not doc.custom_parent_ticket:
		frappe.throw("Parent ticket is required for follow-up tickets")
	
	# Get parent ticket details
	parent_doc = frappe.get_doc("HD Ticket", doc.custom_parent_ticket)
	parent_ticket_id = parent_doc.custom_naming_series or parent_doc.name
	
	# Get next follow-up sequence number
	follow_up_sequence = get_next_follow_up_sequence(doc.custom_parent_ticket)
	
	# Format: <ParentTicketID>-R<Sequence>
	naming_series = f"{parent_ticket_id}-R{follow_up_sequence}"
	
	# Store sequence and naming series
	doc.custom_follow_up_sequence = follow_up_sequence
	doc.custom_naming_series = naming_series
	doc.name = naming_series


def get_next_follow_up_sequence(parent_ticket):
	"""
	Get the next follow-up sequence number for a parent ticket
	
	Args:
	    parent_ticket: Parent ticket name/ID
	    
	Returns:
	    int: Next sequence number (1, 2, 3, etc.)
	"""
	try:
		# Find all follow-up tickets for this parent
		existing_follow_ups = frappe.get_all(
			"HD Ticket",
			filters={
				"custom_parent_ticket": parent_ticket,
				"custom_is_follow_up": 1
			},
			fields=["custom_follow_up_sequence"],
			order_by="custom_follow_up_sequence desc",
			limit=1
		)
		
		if existing_follow_ups:
			# Get the highest sequence and add 1
			return existing_follow_ups[0].custom_follow_up_sequence + 1
		else:
			# First follow-up ticket
			return 1
			
	except Exception as e:
		frappe.log_error(
			f"Error getting follow-up sequence for parent {parent_ticket}: {str(e)}",
			"HD Ticket Follow-up Sequence Error"
		)
		return 1


def set_default_values(doc, method=None):
	"""
	Hook function to set default values for HD Ticket on creation
	
	Args:
	    doc: HD Ticket document
	    method: Hook method name (unused but required by Frappe)
	"""
	# Safely set the custom created datetime to now if the field exists and is empty.
	if hasattr(doc, "custom_created_datetime") and not doc.custom_created_datetime:
		doc.custom_created_datetime = now_datetime()

	# Set status to "Open" if not already set
	if not doc.status:
		doc.status = "Open"

	# Auto-populate customer field with company name from ticket creator
	if not doc.get("custom_customer"):
		set_customer_from_user_company(doc)

	# Fetch module automatically based on reference document
	if hasattr(doc, "custom_module") and not doc.custom_module:
		module = get_module_from_reference(doc)
		if module:
			doc.custom_module = module
	
	# Set custom reference fields from reference_* fields or form context
	reference_doctype = None
	reference_name = None
	
	# Try to get reference from various sources
	if hasattr(doc, "reference_doctype") and doc.reference_doctype:
		reference_doctype = doc.reference_doctype
		reference_name = doc.reference_name
	elif frappe.form_dict.get("reference_doctype"):
		reference_doctype = frappe.form_dict.get("reference_doctype")
		reference_name = frappe.form_dict.get("reference_name")
	
	# Set the custom reference fields if we have the data
	if reference_doctype:
		doc.custom_reference_document = reference_doctype
		if reference_name:
			doc.custom_reference_document_name = reference_name


def set_customer_from_user_company(doc):
	"""
	Set the custom_customer field based on the ticket creator's company
	
	Priority:
	1. Current session user's custom_company
	2. Document owner's custom_company (if different)
	3. Default company from Global Defaults
	
	Args:
	    doc: HD Ticket document
	"""
	try:
		company_name = None
		
		# First try: Get current session user's company
		current_user = frappe.session.user
		if current_user and current_user != "Guest":
			company_name = get_company_name_from_user(current_user)
			
		# Second try: If no company found and doc has owner, try owner's company
		if not company_name and hasattr(doc, 'owner') and doc.owner:
			company_name = get_company_name_from_user(doc.owner)
			
		# Third try: If still no company, try default company
		if not company_name:
			default_company = frappe.db.get_single_value("Global Defaults", "default_company")
			if default_company:
				company_name = frappe.db.get_value("Company", default_company, "company_name")
				
		# Set the customer field if we found a company name
		if company_name:
			doc.custom_customer = company_name
			frappe.logger().info(f"HD Ticket {doc.name or 'New'}: Set customer to '{company_name}'")
		else:
			frappe.logger().warning(f"HD Ticket {doc.name or 'New'}: Could not determine customer company")
			
	except Exception as e:
		frappe.log_error(
			f"Error setting customer field for HD Ticket: {str(e)}",
			"HD Ticket Customer Field Error"
		)


def get_company_name_from_user(user_email):
	"""
	Get company name from user's custom_company field
	
	Args:
	    user_email: User email/ID
	    
	Returns:
	    str: Company name or None if not found
	"""
	try:
		if not user_email or user_email == "Guest":
			return None
			
		# Get user document
		user_doc = frappe.get_doc("User", user_email)
		
		# Check if user has custom_company field set
		if hasattr(user_doc, "custom_company") and user_doc.custom_company:
			# Get company name from company document
			company_name = frappe.db.get_value("Company", user_doc.custom_company, "company_name")
			if company_name:
				return company_name
				
		return None
		
	except Exception as e:
		frappe.logger().error(f"Error getting company for user {user_email}: {str(e)}")
		return None


def prevent_auto_assignment(doc, method=None):
	"""
	Hook function to prevent automatic assignment to employees
	
	This clears any automatic assignments that may have been set by
	assignment rules or other automated processes.
	
	Note: This prevents AUTO-assignment only. Manual assignment via
	custom_assigned_to field still works.
	
	Args:
	    doc: HD Ticket document
	    method: Hook method name (unused but required by Frappe)
	"""
	# Clear the _assign field that Frappe uses for assignments
	if hasattr(doc, "_assign") and doc._assign:
		doc._assign = None

	# Note: We do NOT clear custom_assigned_to field
	# That field is for manual assignment and should be preserved

	# Remove any ToDo assignments that were auto-created
	try:
		# Get any ToDos assigned for this ticket
		todos = frappe.get_all(
			"ToDo",
			filters={
				"reference_type": "HD Ticket",
				"reference_name": doc.name,
				"status": "Open",
			},
			pluck="name",
		)

		# Delete auto-created ToDos (not manually created ones)
		for todo_name in todos:
			todo = frappe.get_doc("ToDo", todo_name)
			# Only delete if it was auto-created (not manually assigned)
			if todo.get("allocated_to") and not todo.get("manually_assigned"):
				frappe.delete_doc("ToDo", todo_name, ignore_permissions=True)

	except Exception as e:
		# Log error but don't stop ticket creation
		frappe.log_error(
			f"Could not clear auto-assignments for {doc.name}: {str(e)}",
			"HD Ticket Auto-Assignment Prevention",
		)


def get_module_from_reference(doc):
	"""
	Determine module based on reference document type
	
	Maps common doctypes to their respective modules:
	- Attendance → HR
	- Sales Order → Accounts
	- Sales Invoice → Accounts
	- Purchase Order → Buying/Accounts
	- Employee → HR
	- Leave Application → HR
	- etc.
	
	Args:
	    doc: HD Ticket document
	
	Returns:
	    str: Module name or None
	"""
	# Module mapping: DocType → Module
	doctype_module_mapping = {
		# HR Module
		"Attendance": "HR",
		"Employee": "HR",
		"Leave Application": "HR",
		"Leave Type": "HR",
		"Salary Slip": "HR",
		"Salary Structure": "HR",
		"Appraisal": "HR",
		"Training Event": "HR",
		"Job Applicant": "HR",
		"Job Opening": "HR",
		"Payroll Entry": "HR",
		"Shift Type": "HR",
		"Shift Assignment": "HR",
		# Accounts Module
		"Sales Order": "Accounts",
		"Sales Invoice": "Accounts",
		"Purchase Order": "Accounts",
		"Purchase Invoice": "Accounts",
		"Payment Entry": "Accounts",
		"Journal Entry": "Accounts",
		"Customer": "Accounts",
		"Supplier": "Accounts",
		"Account": "Accounts",
		"Cost Center": "Accounts",
		"Payment Request": "Accounts",
		"POS Invoice": "Accounts",
		# Stock Module
		"Item": "Stock",
		"Stock Entry": "Stock",
		"Delivery Note": "Stock",
		"Purchase Receipt": "Stock",
		"Material Request": "Stock",
		"Warehouse": "Stock",
		"Stock Reconciliation": "Stock",
		"Packing Slip": "Stock",
		# CRM Module
		"Lead": "CRM",
		"Opportunity": "CRM",
		"Campaign": "CRM",
		"Prospect": "CRM",
		# Projects Module
		"Project": "Projects",
		"Task": "Projects",
		"Timesheet": "Projects",
		"Project Template": "Projects",
		# Manufacturing Module
		"Work Order": "Manufacturing",
		"BOM": "Manufacturing",
		"Production Plan": "Manufacturing",
		"Job Card": "Manufacturing",
		# Support Module
		"Issue": "Support",
		"Warranty Claim": "Support",
		# Selling Module
		"Quotation": "Selling",
		"Sales Partner": "Selling",
		# Buying Module
		"Supplier Quotation": "Buying",
		"Request for Quotation": "Buying",
		# Asset Module
		"Asset": "Assets",
		"Asset Maintenance": "Assets",
		"Asset Repair": "Assets",
		# Quality Module
		"Quality Inspection": "Quality",
		"Quality Goal": "Quality",
	}

	# Try to find reference from various possible fields
	reference_doctype = None
	reference_fields = [
		"reference_doctype",
		"ref_doctype",
		"custom_reference_doctype",
		"custom_ref_doctype",
	]

	for field in reference_fields:
		if hasattr(doc, field) and doc.get(field):
			reference_doctype = doc.get(field)
			break

	# If reference doctype found, map it to module
	if reference_doctype and reference_doctype in doctype_module_mapping:
		return doctype_module_mapping[reference_doctype]

	# Fallback: Check if ticket was created from a specific form context
	# This checks frappe.form_dict for context
	if frappe.form_dict.get("reference_doctype"):
		ref_dt = frappe.form_dict.get("reference_doctype")
		if ref_dt in doctype_module_mapping:
			return doctype_module_mapping[ref_dt]


def auto_create_task_on_assignment(doc, method=None):
	"""
	Automatically create a Task when an employee is assigned to HD Ticket
	
	Args:
	    doc: HD Ticket document
	    method: Hook method name (unused but required by Frappe)
	"""
	# Check if custom_assigned_to has been set or changed
	if doc.custom_assigned_to and doc.has_value_changed("custom_assigned_to"):
		
		# Check if task already exists for this ticket
		existing_task = frappe.db.exists("Task", {"custom_hd_ticket": doc.name})
		
		if not existing_task:
			try:
				# Get default allocated hours from estimation or use default
				default_hours = doc.get("custom_estimation_hours", 8.0)  # Default to 8 hours
				
				# Create the task
				task = frappe.new_doc("Task")
				task.subject = f"Task for HD Ticket: {doc.name} - {doc.subject}"
				task.custom_hd_ticket = doc.name
				task.custom_allocated_hours = default_hours
				task.expected_time = default_hours  # Set standard expected_time field
				task.custom_estimated_hours = default_hours 
				task.custom_extra_approved_hours = 0
				task.status = "Open"
				
				# Set assigned user and employee on the Task
				task.custom_assigned_to = doc.custom_assigned_to
				if doc.custom_assigned_to:
					employee_name = frappe.db.get_value("Employee", {"user_id": doc.custom_assigned_to}, "name")
					if employee_name:
						task.custom_assigned_employee = employee_name


				task.priority = doc.get("priority", "Medium")
				
				# Set project if HD Ticket has project reference
				if hasattr(doc, 'project') and doc.project:
					task.project = doc.project
				elif hasattr(doc, 'custom_project') and doc.custom_project:
					task.project = doc.custom_project
					
				# Save the task
				task.insert(ignore_permissions=True)
				
				# Assign task to the assigned user using ERPNext's assignment system
				try:
					frappe.get_doc({
						"doctype": "ToDo",
						"allocated_to": doc.custom_assigned_to,
						"reference_type": "Task",
						"reference_name": task.name,
						"description": f"Auto-assigned from HD Ticket: {doc.name}",
						"status": "Open"
					}).insert(ignore_permissions=True)
				except Exception as e:
					frappe.log_error(f"Could not assign task to user: {str(e)}")
				
				# Update HD Ticket with task reference
				frappe.db.set_value("HD Ticket", doc.name, "custom_related_task", task.name, update_modified=False)
				
				frappe.msgprint(
					f"Task {task.name} automatically created and assigned to {doc.custom_assigned_to}",
					indicator="green",
					title="Task Auto-Created"
				)
				
			except Exception as e:
				frappe.log_error(
					f"Failed to auto-create task for HD Ticket {doc.name}: {str(e)}",
					"HD Ticket Auto Task Creation Error"
				)
				
		else:
			# Task exists, optionally update assignment info
			frappe.msgprint(
				f"Task already exists for this HD Ticket: {existing_task}",
				indicator="blue",
				title="Task Exists"
			)


@frappe.whitelist()
def refresh_customer_field(hd_ticket_name):
	"""Manually refresh the customer field for an HD Ticket"""
	try:
		doc = frappe.get_doc("HD Ticket", hd_ticket_name)
		
		# Get company name using the same logic as ticket creation
		company_name = None
		
		# Try current user first
		current_user = frappe.session.user
		if current_user and current_user != "Guest":
			company_name = get_company_name_from_user(current_user)
			
		# If no company from current user, try ticket owner
		if not company_name and doc.owner:
			company_name = get_company_name_from_user(doc.owner)
			
		# If still no company, try default
		if not company_name:
			default_company = frappe.db.get_single_value("Global Defaults", "default_company")
			if default_company:
				company_name = frappe.db.get_value("Company", default_company, "company_name")
		
		if company_name:
			doc.custom_customer = company_name
			doc.save()
			
			return {
				"success": True,
				"message": f"Customer field updated to: {company_name}",
				"company_name": company_name
			}
		else:
			return {
				"success": False,
				"message": "No company found for current user or ticket owner"
			}
			
	except Exception as e:
		frappe.log_error(f"Error refreshing customer field: {str(e)}")
		return {
			"success": False,
			"message": f"Error: {str(e)}"
		}


@frappe.whitelist()
def get_user_company_info():
	"""Get current user's company information for debugging"""
	try:
		user = frappe.session.user
		user_doc = frappe.get_doc("User", user)
		
		company_info = {
			"user": user,
			"has_custom_company": hasattr(user_doc, "custom_company"),
			"custom_company": getattr(user_doc, "custom_company", None),
			"company_name": None
		}
		
		if company_info["custom_company"]:
			company_info["company_name"] = frappe.db.get_value("Company", company_info["custom_company"], "company_name")
			
		return company_info
		
	except Exception as e:
		return {"error": str(e)}


@frappe.whitelist()
def create_follow_up_ticket(parent_ticket_name, reason=None):
	"""
	Create a follow-up ticket from an existing ticket
	
	Args:
	    parent_ticket_name: Name of the parent ticket
	    reason: Optional reason for creating follow-up ticket
	    
	Returns:
	    dict: Success status and new ticket name
	"""
	try:
		# Get parent ticket
		parent_doc = frappe.get_doc("HD Ticket", parent_ticket_name)
		
		# Create new follow-up ticket
		follow_up_doc = frappe.new_doc("HD Ticket")
		
		# Copy relevant fields from parent
		fields_to_copy = [
			"subject",
			"description", 
			"priority",
			"custom_customer",
			"custom_module",
			"custom_assigned_to",
			"custom_estimation_hours",
			"custom_reference_document",
			"custom_reference_document_name"
		]
		
		for field in fields_to_copy:
			if hasattr(parent_doc, field) and parent_doc.get(field):
				follow_up_doc.set(field, parent_doc.get(field))
		
		# Set follow-up specific fields
		follow_up_doc.custom_is_follow_up = 1
		follow_up_doc.custom_parent_ticket = parent_ticket_name
		follow_up_doc.status = "Open"
		
		# Modify subject to indicate follow-up
		if reason:
			follow_up_doc.subject = f"{parent_doc.subject} - Follow-up: {reason}"
		else:
			follow_up_doc.subject = f"{parent_doc.subject} - Follow-up"
		
		# Add note to description
		follow_up_note = f"\n\n--- FOLLOW-UP TICKET ---\nParent Ticket: {parent_ticket_name}\nReason: {reason or 'Not specified'}\nCreated by: {frappe.session.user}\n"
		
		if follow_up_doc.description:
			follow_up_doc.description += follow_up_note
		else:
			follow_up_doc.description = f"Follow-up ticket for {parent_ticket_name}{follow_up_note}"
		
		# Save the follow-up ticket
		follow_up_doc.insert()
		
		# Update parent ticket with follow-up reference
		update_parent_ticket_status(parent_ticket_name, follow_up_doc.name)
		
		frappe.msgprint(
			f"Follow-up ticket {follow_up_doc.name} created successfully",
			indicator="green",
			title="Follow-up Ticket Created"
		)
		
		return {
			"success": True,
			"follow_up_ticket": follow_up_doc.name,
			"message": f"Follow-up ticket created: {follow_up_doc.name}"
		}
		
	except Exception as e:
		frappe.log_error(f"Error creating follow-up ticket: {str(e)}")
		return {
			"success": False,
			"message": f"Error: {str(e)}"
		}


def update_parent_ticket_status(parent_ticket_name, follow_up_ticket_name):
	"""Update parent ticket to indicate follow-up was created"""
	try:
		# Add a comment to parent ticket
		frappe.get_doc({
			"doctype": "Comment",
			"comment_type": "Info",
			"reference_doctype": "HD Ticket",
			"reference_name": parent_ticket_name,
			"content": f"Follow-up ticket created: {follow_up_ticket_name}",
			"comment_by": frappe.session.user
		}).insert(ignore_permissions=True)
		
	except Exception as e:
		frappe.log_error(f"Error updating parent ticket status: {str(e)}")


@frappe.whitelist()
def get_ticket_relationships(ticket_name):
	"""
	Get parent and child tickets for a given ticket
	
	Args:
	    ticket_name: Name of the ticket
	    
	Returns:
	    dict: Parent ticket and list of follow-up tickets
	"""
	try:
		ticket_doc = frappe.get_doc("HD Ticket", ticket_name)
		
		parent_ticket = None
		follow_up_tickets = []
		
		# Check if this is a follow-up ticket
		if ticket_doc.get("custom_is_follow_up") and ticket_doc.get("custom_parent_ticket"):
			parent_ticket = frappe.get_doc("HD Ticket", ticket_doc.custom_parent_ticket)
			
		# Get all follow-up tickets (either for this ticket or its parent)
		parent_for_search = ticket_doc.custom_parent_ticket if ticket_doc.custom_is_follow_up else ticket_name
		
		follow_up_tickets = frappe.get_all("HD Ticket",
			filters={
				"custom_parent_ticket": parent_for_search,
				"custom_is_follow_up": 1
			},
			fields=["name", "subject", "status", "creation", "custom_follow_up_sequence"],
			order_by="custom_follow_up_sequence asc"
		)
		
		return {
			"success": True,
			"current_ticket": ticket_name,
			"is_follow_up": ticket_doc.get("custom_is_follow_up", 0),
			"parent_ticket": {
				"name": parent_ticket.name if parent_ticket else None,
				"subject": parent_ticket.subject if parent_ticket else None,
				"status": parent_ticket.status if parent_ticket else None
			} if parent_ticket else None,
			"follow_up_tickets": follow_up_tickets
		}
		
	except Exception as e:
		return {
			"success": False,
			"message": str(e)
		}

@frappe.whitelist()
def send_estimate_resolution_time(ticket_name, estimation_hours, force_send=False):
    """
    Updates estimation hours on an HD Ticket and sends a notification email.
    Includes "Send Once" logic to prevent duplicate emails.
    """
    ticket = frappe.get_doc("HD Ticket", ticket_name)

    if not estimation_hours or float(estimation_hours) <= 0:
        frappe.throw(_("Estimation hours must be a positive number."))

    from customer_support.customer_support.notification_system import NotificationSystem
    rule = NotificationSystem.get_notification_rule("Resolution Estimate", "Manual Action")

    if not rule:
        frappe.msgprint(_("Resolution Estimate notification rule is not configured or disabled."), indicator="orange")
        return {"status": "fail", "message": "Notification rule not found."}

    # "Send Once" logic
    if rule.get("send_once") and ticket.get("resolution_estimate_sent") and not force_send:
        return {"status": "already_sent"}

    try:
        # Update the ticket with the new estimation hours
        ticket.db_set("custom_estimated_resolution_hour", float(estimation_hours))

        # Reload the document to ensure the notification context has the latest data
        ticket.reload()

        # Send the notification
        NotificationSystem.send_notification(ticket, "Resolution Estimate", "Manual Action")

        # Mark the estimate as sent
        ticket.db_set("resolution_estimate_sent", 1)

        # Add a comment to the ticket's timeline
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "HD Ticket",
            "reference_name": ticket.name,
            "content": _("Resolution estimate of {0} hours sent to the customer.").format(estimation_hours),
            "comment_by": frappe.session.user
        }).insert(ignore_permissions=True)

        frappe.msgprint(
            _("Resolution estimate email has been queued for sending."),
            title=_("Success"),
            indicator="green"
        )
        return {"status": "success"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "send_estimate_resolution_time Error")
        frappe.throw(_("Failed to send resolution estimate. Error: {0}").format(str(e)))
