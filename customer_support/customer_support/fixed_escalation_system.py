# Fixed Escalation System - Complete Working Implementation

import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date, validate_email_address
from frappe.core.doctype.communication.email import make
from .notification_system import NotificationSystem


def check_escalation_notifications_fixed():
    """
    FIXED: Improved escalation notification checker with better debugging
    """
    try:
        frappe.log_error("Starting escalation check...", "Escalation Debug")
        
        # Check if notifications are enabled first
        try:
            settings = frappe.get_single("Customer Support Notification Settings")
            if not settings.enable_notifications:
                frappe.log_error("Escalation check skipped - notifications disabled", "Escalation Debug")
                return
        except Exception as e:
            frappe.log_error(f"Could not get notification settings: {str(e)}", "Escalation Error")
            return
        
        # Get escalation rule
        rule = None
        for notification_rule in settings.notification_rules:
            if (notification_rule.notification_type == "Escalation" and 
                notification_rule.trigger_event == "Scheduler" and
                notification_rule.enabled):
                rule = notification_rule
                break
        
        if not rule:
            frappe.log_error("No enabled escalation rule found", "Escalation Error")
            return
        
        # Get escalation configuration from the rule itself
        escalation_condition = rule.get_escalation_condition() if hasattr(rule, 'get_escalation_condition') else None
        
        if escalation_condition:
            delay_minutes = escalation_condition.get('minutes_threshold', 15)
        else:
            delay_minutes = rule.delay_minutes or 15

        # Define the statuses that should NOT be escalated.
        excluded_statuses = {"Replied", "Resolved", "Closed", "Not Completed", "Completed"}
        
        frappe.log_error(f"Using escalation config: {delay_minutes} minutes, exclude statuses: {excluded_statuses}", "Escalation Debug")
        
        # Get tickets eligible for escalation using configurable conditions
        cutoff_time = add_to_date(now_datetime(), minutes=-delay_minutes)
        
        tickets = frappe.get_all(
            "HD Ticket",
            filters={
                "status": ["not in", list(excluded_statuses)],  # Use configurable excluded statuses
                "escalation_sent": 0,
                "creation": ["<", cutoff_time]
            },
            fields=["name", "creation", "custom_assigned_to", "raised_by", "owner", "subject", "status"]
        )
        
        frappe.log_error(f"Found {len(tickets)} tickets eligible for escalation", "Escalation Debug")
        
        for ticket_data in tickets:
            try:
                ticket = frappe.get_doc("HD Ticket", ticket_data.name)
                
                # Calculate how long ticket has been open
                minutes_open = (now_datetime() - ticket.creation).total_seconds() / 60
                frappe.log_error(f"Processing ticket {ticket.name} - {minutes_open:.1f} minutes old", "Escalation Debug")
                
                # Use the main, unified notification system to send the escalation.
                # This respects the modern recipient configuration in the UI.
                success = NotificationSystem.send_notification(ticket, "Escalation", "Scheduler")
                
                if success:
                    # Mark as escalated
                    ticket.db_set({
                        "escalation_sent": 1,
                        "escalated_at": now_datetime()
                    }, update_modified=False)
                    
                    frappe.log_error(
                        f"Escalation notification successfully sent for ticket {ticket.name}.",
                        "Escalation Success"
                    )
                else:
                    frappe.log_error(f"Failed to send escalation for ticket {ticket.name}", "Escalation Error")
            except Exception as e:
                frappe.log_error(f"Error processing ticket {ticket_data.name}: {str(e)}", "Escalation Error")
        
        if tickets:
            frappe.log_error(f"Escalation check complete - processed {len(tickets)} tickets", "Escalation Debug")
        
    except Exception as e:
        frappe.log_error(f"Escalation scheduler error: {str(e)}", "Escalation Error")