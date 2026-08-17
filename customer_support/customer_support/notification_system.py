# Copyright (c) 2023, WeBeaz and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, add_to_date, validate_email_address
from frappe.core.doctype.communication.email import make


class NotificationSystem:
    """Customer Support Notification System"""
    
    @staticmethod
    def get_notification_settings(company=None):
        """Get notification settings (Single DocType)"""
        try:
            settings = frappe.get_single("Customer Support Notification Settings")
            
            # If no company specified or matches the settings company, return settings
            if not company or not settings.company or settings.company == company:
                return settings if settings.enable_notifications else None
            else:
                return None
                
        except frappe.DoesNotExistError:
            return None
    
    @staticmethod
    def get_notification_rule(notification_type, trigger_event, company=None):
        """Get specific notification rule"""
        settings = NotificationSystem.get_notification_settings(company)
        if not settings:
            return None
        
        for rule in settings.notification_rules:
            if (rule.enabled and 
                rule.notification_type == notification_type and 
                rule.trigger_event == trigger_event):
                return rule
        
        return None
    
    @staticmethod
    def build_recipient_list(rule, ticket):
        """Build email recipient list based on simple checkbox configuration"""
        recipients = {"to": [], "cc": [], "bcc": []}
        
        try:
            # Send to Customer (raised_by field)
            if getattr(rule, 'send_to_customer', 0):
                if ticket.raised_by and frappe.utils.validate_email_address(ticket.raised_by):
                    recipients["to"].append(ticket.raised_by)
            
            # Send to Assigned Agent
            if getattr(rule, 'send_to_assigned_agent', 0):
                if getattr(ticket, 'custom_assigned_to', None):
                    user_email = frappe.db.get_value("User", ticket.custom_assigned_to, "email")
                    if user_email:
                        recipients["cc"].append(user_email)
            
            # Send to Ticket Owner
            if getattr(rule, 'send_to_owner', 0):
                if ticket.owner:
                    recipients["cc"].append(ticket.owner)
            
            # CC Support Team
            if getattr(rule, 'cc_support_team', 0):
                support_users = frappe.get_all(
                    "Has Role", 
                    filters={"role": "Support Team"}, 
                    fields=["parent"]
                )
                for user in support_users:
                    user_email = frappe.db.get_value("User", user.parent, "email")
                    if user_email:
                        recipients["bcc"].append(user_email)
            
            # Custom Emails
            if getattr(rule, 'bcc_custom_emails', 0) and getattr(rule, 'custom_emails', None):
                custom_emails = [email.strip() for email in rule.custom_emails.split(",")]
                for email in custom_emails:
                    if email and frappe.utils.validate_email_address(email):
                        recipients["cc"].append(email)
        
        except Exception as e:
            frappe.log_error(f"Error building recipient list: {str(e)}", "Notification System")
        
        # Remove duplicates and empty emails
        for role in recipients:
            recipients[role] = list(set([email for email in recipients[role] if email]))
        
        return recipients
    
    @staticmethod
    def parse_recipient_emails(recipient_string, ticket):
        """Parse recipient string and resolve special keywords"""
        emails = []
        
        if not recipient_string:
            return emails
        
        # Split by commas and process each recipient
        for recipient in recipient_string.split(','):
            recipient = recipient.strip()
            
            if not recipient:
                continue
                
            # Handle special keywords
            if recipient.lower() == 'customer':
                if ticket.contact_email:
                    emails.append(ticket.contact_email)
            elif recipient.lower() == 'assigned_agent':
                if ticket.custom_assigned_to:
                    user_email = frappe.db.get_value("User", ticket.custom_assigned_to, "email")
                    if user_email:
                        emails.append(user_email)
            elif recipient.lower() == 'ticket_owner':
                if ticket.owner:
                    emails.append(ticket.owner)
            elif '@' in recipient:
                # Direct email address
                if frappe.utils.validate_email_address(recipient):
                    emails.append(recipient)
            else:
                # Try to treat as user name and get email
                user_email = frappe.db.get_value("User", {"full_name": recipient}, "email")
                if user_email:
                    emails.append(user_email)
        
        return emails
    
    @staticmethod
    def resolve_recipient_emails(recipient, ticket):
        """Resolve email addresses for a recipient configuration (ERPNext style)"""
        emails = []
        
        # Handle Document Field based recipients
        if recipient.receiver_by == "Document Field" and recipient.field_name:
            field_value = getattr(ticket, recipient.field_name, None)
            
            if recipient.field_name == "raised_by":
                # raised_by is already an email address
                if field_value and validate_email_address(field_value):
                    emails.append(field_value)
                    
            elif recipient.field_name in ["custom_assigned_to", "owner"]:
                if field_value:
                    user_email = frappe.db.get_value("User", field_value, "email")
                    if user_email:
                        emails.append(user_email)
                        
            elif recipient.field_name == "contact":
                if field_value:
                    contact_email = frappe.db.get_value("Contact", field_value, "email_id")
                    if contact_email and validate_email_address(contact_email):
                        emails.append(contact_email)
                        
            elif recipient.field_name == "customer":
                if field_value:
                    customer_email = frappe.db.get_value("Customer", field_value, "email_id")
                    if customer_email and validate_email_address(customer_email):
                        emails.append(customer_email)
                        
            elif recipient.field_name == "agent_group":
                # Get users in the agent group/team
                if field_value:
                    team_members = frappe.get_all(
                        "HD Team Member",
                        filters={"parent": field_value},
                        fields=["user"]
                    )
                    for member in team_members:
                        user_email = frappe.db.get_value("User", member.user, "email")
                        if user_email:
                            emails.append(user_email)
        
        # Handle Role based recipients
        elif recipient.receiver_by == "Role" and recipient.email_by_role:
            role_users = frappe.get_all(
                "Has Role", 
                filters={"role": recipient.email_by_role}, 
                fields=["parent"]
            )
            for user in role_users:
                user_email = frappe.db.get_value("User", user.parent, "email")
                if user_email:
                    emails.append(user_email)
        
        # Handle Email based recipients
        elif recipient.receiver_by == "Email" and recipient.email_by_document_field:
            custom_emails = [email.strip() for email in recipient.email_by_document_field.split(",")]
            for email in custom_emails:
                if validate_email_address(email):
                    emails.append(email)
        
        return emails
    
    @staticmethod
    def get_department_manager_email(user):
        """Get department manager email for a user"""
        try:
            employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
            if employee:
                department = frappe.db.get_value("Employee", employee, "department")
                if department:
                    # Get department manager
                    manager_employee = frappe.db.get_value("Department", department, "department_manager")
                    if manager_employee:
                        return frappe.db.get_value("Employee", manager_employee, "user_id")
        except Exception:
            pass
        return None

    @staticmethod
    def resolve_sender_email(from_email, settings=None):
        """Resolve ONLY Email Account references - no fallback to direct email address."""
        # PRIORITY 1: Check if from_email is already a valid email address
        if from_email and validate_email_address(from_email):
            return from_email

        # PRIORITY 2: Try to resolve from_email as Email Account name
        if from_email:
            # from_email may be an Email Account document name
            email_id = frappe.db.get_value("Email Account", from_email, "email_id")
            if email_id and validate_email_address(email_id):
                return email_id

            # from_email may also be stored in the email_id field directly
            email_id = frappe.db.get_value("Email Account", {"email_id": from_email}, "email_id")
            if email_id and validate_email_address(email_id):
                return email_id

        # NO FALLBACK TO direct email address - ONLY use Email Account
        return None

    @staticmethod
    def send_notification(ticket, notification_type, trigger_event):
        """Send notification for a ticket"""
        try:
            # Get notification rule
            rule = NotificationSystem.get_notification_rule(notification_type, trigger_event)
            if not rule:
                return False
            
            # Build recipients
            recipients = NotificationSystem.build_recipient_list(rule, ticket)
            
            # Check if we have recipients
            if not any(recipients.values()):
                frappe.log_error(
                    f"No recipients found for notification: {notification_type} for ticket {ticket.name}",
                    "Customer Support Notification"
                )
                return False
            
            # Get settings for default from email
            settings = NotificationSystem.get_notification_settings()
            
            # Determine sender email
            from_email = getattr(rule, 'from_email', None) or settings.default_from_email
            from_email = NotificationSystem.resolve_sender_email(from_email, settings)
            if not from_email:
                # Get default outgoing email account
                default_account = frappe.db.get_value("Email Account", {"default_outgoing": 1}, "email_id")
                from_email = default_account or "noreply@example.com"
            
            reply_to = settings.reply_to or from_email
            
            # Render subject
            subject = getattr(rule, 'subject', f"HD Ticket Notification: {ticket.name}")
            try:
                subject = frappe.render_template(subject, {"doc": ticket})
            except:
                subject = f"HD Ticket Notification: {ticket.name}"
            
            # Get email template content
            content = ""
            if getattr(rule, 'email_template', None):
                try:
                    template_doc = frappe.get_doc("Email Template", rule.email_template)
                    # Use response_html if it's an HTML template, otherwise fall back to response
                    if template_doc.use_html:
                        content = frappe.render_template(template_doc.response_html, {"doc": ticket})
                    else:
                        content = frappe.render_template(template_doc.response, {"doc": ticket})
                except:
                    content = f"<p>Ticket {ticket.name} notification</p>"
            
            # Send email using frappe.sendmail (more reliable)
            frappe.sendmail(
                recipients=recipients["to"],
                cc=recipients["cc"],
                bcc=recipients["bcc"],
                subject=subject,
                message=content,
                sender=from_email,
                reply_to=reply_to,
                delayed=True,  # Send in background
                now=False      # Don't send immediately
            )
            
            return True
            
        except Exception as e:
            # Log error but don't show to user or raise exception
            frappe.log_error(
                f"Failed to send notification for ticket {ticket.name}: {str(e)}",
                "Customer Support Notification System Error"
            )
            return False
    
    @staticmethod
    def render_template(template_string, ticket):
        """Render template with ticket context"""
        try:
            return frappe.render_template(template_string, {"doc": ticket})
        except Exception:
            return template_string


# Hook functions
def on_ticket_insert(doc, method=None):
    """Handle new ticket notifications"""
    try:
        # Check if notifications are enabled
        settings = frappe.get_single("Customer Support Notification Settings")
        if not settings.enable_notifications:
            return
            
        NotificationSystem.send_notification(doc, "New Ticket", "After Insert")
    except Exception as e:
        # Log error but don't show to user
        frappe.log_error(
            f"Error in new ticket notification for {doc.name}: {str(e)}",
            "Customer Support Notification Error"
        )


def on_ticket_update(doc, method=None):
    """Handle ticket status change notifications"""
    try:
        # Check if notifications are enabled
        settings = frappe.get_single("Customer Support Notification Settings")
        if not settings.enable_notifications:
            return
            
        if doc.has_value_changed("status"):
            if doc.status == "Resolved":
                NotificationSystem.send_notification(doc, "Resolved", "Status Change")
            elif doc.status == "Closed":
                NotificationSystem.send_notification(doc, "Closed", "Status Change")
    except Exception as e:
        # Log error but don't show to user
        frappe.log_error(
            f"Error in ticket update notification for {doc.name}: {str(e)}",
            "Customer Support Notification Error"
        )