# Copyright (c) 2023, WeBeaz and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, add_to_date
from customer_support.customer_support.fixed_escalation_system import check_escalation_notifications_fixed
from customer_support.customer_support.sync_tickets import sync_remote_tickets


def check_escalation_notifications():
    """
    Scheduler function to check and send escalation notifications
    Uses the fixed escalation system with better debugging and recipient handling
    """
    try:
        # Use the fixed escalation system
        check_escalation_notifications_fixed()
        
    except Exception as e:
        frappe.log_error(
            f"Escalation scheduler failed: {str(e)}",
            "Escalation Scheduler Error"
        )


def handle_status_reply_reset(doc, method=None):
    """
    Handles the logic when a ticket's status changes to 'Replied'.
    If an agent replies, we should prevent any future escalation for this
    specific response cycle by setting the escalation_sent flag.
    
    Args:
        doc: HD Ticket document
        method: Hook method name
    """
    try:
        # If status changes to 'Replied' and no escalation has been sent yet,
        # mark it as handled to prevent the scheduler from picking it up.
        if (doc.has_value_changed("status") and
            doc.status == "Replied" and
            not doc.escalation_sent):
            
            # Set escalation_sent to 1 to prevent the scheduler from sending an escalation.
            # This effectively cancels the pending escalation for this response cycle.
            doc.db_set("escalation_sent", 1, update_modified=False)
            
            frappe.log_error(
                f"Agent replied to ticket {doc.name}. Pending escalation has been cancelled.",
                "Escalation Cancelled"
            )
                
    except Exception as e:
        frappe.log_error(
            f"Failed to handle status reply reset for ticket {doc.name}: {str(e)}",
            "Status Reply Reset Error"
        )



def sync_tickets_from_remote_sites():
	"""
	Scheduled function to automatically sync tickets from enabled remote sites.
	Runs on a schedule (configured in hooks.py).
	
	This will pull tickets from all enabled Ticket Sync Sources.
	Only tickets that are new or modified since last sync will be pulled.
	"""
	try:
		# Sync from all enabled sources
		results = sync_remote_tickets()
		
		# Log results
		for result in results:
			if result.get('status') == 'ok':
				frappe.logger().info(
					f"Ticket sync from {result['site']}: "
					f"{result['created']} created, {result['updated']} updated"
				)
			else:
				frappe.log_error(
					f"Ticket sync from {result['site']} failed: {result.get('error')}",
					"Ticket Sync Scheduler Error"
				)
				
	except Exception as e:
		frappe.log_error(
			f"Ticket sync scheduler failed: {str(e)}",
			"Ticket Sync Scheduler Error"
		)
