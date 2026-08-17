# Copyright (c) 2023, WeBeaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerSupportNotificationSettings(Document):
    def validate(self):
        """Validate notification settings"""
        # Update escalation condition display if fields exist
        if hasattr(self, 'escalation_minutes') and hasattr(self, 'escalation_excluded_statuses'):
            self.update_escalation_condition_display()
        
        # Validate notification rules
        self.validate_notification_rules()
    
    def update_escalation_condition_display(self):
        """Update the escalation condition display based on simple fields"""
        try:
            minutes = self.escalation_minutes or 15
            statuses = self.escalation_excluded_statuses or "Replied, Resolved, Closed"
            
            # Clean up the status list
            status_list = [s.strip() for s in statuses.split(',')]
            status_text = ", ".join(status_list)
            
            self.escalation_condition = f"Send escalation for tickets NOT in status [{status_text}] after {minutes} minutes"
        except:
            pass  # Don't fail validation if there's an issue with display field
    
    def get_escalation_config(self):
        """Get escalation configuration from simple fields"""
        try:
            minutes = getattr(self, 'escalation_minutes', None) or 15
            statuses = getattr(self, 'escalation_excluded_statuses', None) or "Replied, Resolved, Closed"
            
            # Parse status list
            status_list = [s.strip() for s in statuses.split(',') if s.strip()]
            
            return {
                "statuses_to_exclude": status_list,
                "minutes_threshold": minutes
            }
        except:
            # Return default config if there's any issue
            return {
                "statuses_to_exclude": ["Replied", "Resolved", "Closed"],
                "minutes_threshold": 15
            }
    
    def validate_notification_rules(self):
        """Validate notification rules for duplicates and conflicts"""
        if not hasattr(self, 'notification_rules') or not self.notification_rules:
            return
        
        notification_types = []
        
        for rule in self.notification_rules:
            if rule.enabled:
                key = f"{rule.notification_type}_{rule.trigger_event}"
                if key in notification_types:
                    frappe.throw(f"Duplicate notification rule found for {rule.notification_type} - {rule.trigger_event}")
                notification_types.append(key)