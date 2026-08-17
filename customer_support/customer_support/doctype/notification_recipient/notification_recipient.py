# Copyright (c) 2023, WeBeaz and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NotificationRecipient(Document):
    def validate(self):
        """Validate notification recipient"""
        if self.recipient_type == "Custom Email" and not self.custom_email:
            frappe.throw("Custom Email is required when Recipient Type is 'Custom Email'")
        
        # Validate email format for custom emails
        if self.custom_email:
            emails = [email.strip() for email in self.custom_email.split(",")]
            for email in emails:
                if email and not frappe.utils.validate_email_address(email):
                    frappe.throw(f"Invalid email address: {email}")