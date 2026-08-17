# Copyright (c) 2023, WeBeaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SupportNotificationRule(Document):
    def validate(self):
        """Validate notification rule"""
        # Update condition description for escalation rules
        if self.notification_type == "Escalation":
            self.update_condition_description()
        
        # Validate that scheduler events have a delay set in the new field
        if self.trigger_event == "Scheduler" and not self.condition_minutes:
            frappe.throw(_("Trigger After (Minutes) is required for Scheduler trigger events"))
    
    def update_condition_description(self):
        """Update the condition description for escalation rules"""
        if self.notification_type == "Escalation":
            minutes = self.condition_minutes or 15
            statuses = self.condition_exclude_statuses or "Replied, Resolved, Closed"
            
            # Clean up the status list
            status_list = [s.strip() for s in statuses.split(',')]
            status_text = ", ".join(status_list)
            
            self.condition_description = f"Escalate if ticket is NOT in status [{status_text}] after {minutes} minutes"
    
    def get_escalation_condition(self):
        """Get escalation condition for this rule"""
        if self.notification_type == "Escalation":
            minutes = self.condition_minutes or 15
            statuses = self.condition_exclude_statuses or "Replied, Resolved, Closed"
            
            # Parse status list
            status_list = [s.strip() for s in statuses.split(',') if s.strip()]
            
            return {
                "minutes_threshold": minutes,
                "statuses_to_exclude": status_list
            }
        return None