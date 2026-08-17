#!/usr/bin/env python3

"""
Customer Support Notification System Setup Script

This script helps set up the notification system with default configurations.

Usage:
    bench execute customer_support.scripts.setup_notification_system.setup_default_notifications --kwargs "{'company': 'WeBeaz Technologies'}"
"""

import frappe
from frappe import _


def setup_default_notifications(company="WeBeaz Technologies"):
    """Set up default notification configurations (Single DocType)"""
    
    # Get or create notification settings (Single DocType)
    try:
        settings = frappe.get_single("Customer Support Notification Settings")
        if settings.company:
            print(f"Notification settings already configured for {settings.company}")
            return settings
    except:
        pass
    
    # Create/update notification settings
    settings = frappe.get_single("Customer Support Notification Settings")
    settings.company = company
    settings.enable_notifications = 1
    
    # Set default email account if available
    email_accounts = frappe.get_all("Email Account", 
        filters={"enable_outgoing": 1}, 
        limit=1, pluck="name")
    if email_accounts:
        settings.default_from_email = email_accounts[0]
    
    settings.reply_to = f"support@{company.lower().replace(' ', '')}.com"
    
    # Clear existing rules
    settings.notification_rules = []
    
    # Add default notification rules
    notification_rules = [
        {
            "enabled": 1,
            "notification_type": "New Ticket",
            "trigger_event": "After Insert",
            "delay_minutes": 0,
            "email_template": "HD Ticket - New Ticket",
            "subject": "New Support Ticket: {{ doc.name }} - {{ doc.subject }}",
            "recipients": [
                {
                    "recipient_role": "To",
                    "recipient_type": "Customer"
                },
                {
                    "recipient_role": "CC",
                    "recipient_type": "Support Team"
                }
            ]
        },
        {
            "enabled": 1,
            "notification_type": "Escalation",
            "trigger_event": "Status Change",
            "delay_minutes": 0,
            "email_template": "HD Ticket - Escalation",
            "subject": "ESCALATION: Ticket {{ doc.name }} requires attention",
            "recipients": [
                {
                    "recipient_role": "To",
                    "recipient_type": "Support Team"
                },
                {
                    "recipient_role": "CC",
                    "recipient_type": "Department Manager"
                }
            ]
        },
        {
            "enabled": 1,
            "notification_type": "Resolved",
            "trigger_event": "Status Change",
            "delay_minutes": 0,
            "email_template": "HD Ticket - Resolved",
            "subject": "✅ Ticket Resolved: {{ doc.name }} - {{ doc.subject }}",
            "recipients": [
                {
                    "recipient_role": "To",
                    "recipient_type": "Customer"
                }
            ]
        },
        {
            "enabled": 1,
            "notification_type": "Resolution Estimate",
            "trigger_event": "Manual Action",
            "delay_minutes": 0,
            "email_template": "HD Ticket - Estimate Resolution Time",
            "subject": "Resolution Estimate for your Support Ticket {{ doc.name }}",
            "recipients": [
                {
                    "recipient_role": "To",
                    "recipient_type": "Customer"
                }
            ]
        }
    ]
    
    # Add notification rules to settings
    for rule_data in notification_rules:
        rule = settings.append("notification_rules", {})
        for field, value in rule_data.items():
            if field == "recipients":
                for recipient_data in value:
                    recipient = rule.append("recipients", {})
                    for rec_field, rec_value in recipient_data.items():
                        setattr(recipient, rec_field, rec_value)
            else:
                setattr(rule, field, value)
    
    # Save the settings
    settings.save(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"✅ Notification system set up successfully for {company}")
    print("📧 Default notification rules created:")
    print("   - New Ticket (immediate)")
    print("   - Escalation (on status change: Open → Replied)")
    print("   - Resolved (immediate)")
    
    return settings


def create_sample_email_templates():
    """Create sample email templates if they don't exist"""
    
    templates = [
        "HD Ticket - New Ticket", 
        "HD Ticket - Estimate Resolution Time",
        "HD Ticket - Escalation", 
        "HD Ticket - Resolved"
    ]
    
    created_templates = []
    
    for template_name in templates:
        if not frappe.db.exists("Email Template", template_name):
            # Templates will be created via fixtures
            print(f"📧 Email template '{template_name}' will be created via fixtures")
            created_templates.append(template_name)
    
    if created_templates:
        print(f"✅ {len(created_templates)} email templates ready to be created")
    else:
        print("✅ All email templates already exist")


def validate_setup():
    """Validate the notification system setup"""
    
    print("🔍 Validating notification system setup...")
    
    issues = []
    
    # Check if Email Account is configured
    email_accounts = frappe.get_all("Email Account", filters={"enable_outgoing": 1})
    if not email_accounts:
        issues.append("❌ No outgoing email account configured")
    else:
        print(f"✅ {len(email_accounts)} outgoing email account(s) found")
    
    # Check if email templates exist
    templates = ["HD Ticket - New Ticket", "HD Ticket - Estimate Resolution Time", "HD Ticket - Escalation", "HD Ticket - Resolved"]
    for template in templates:
        if frappe.db.exists("Email Template", template):
            print(f"✅ Email template '{template}' exists")
        else:
            issues.append(f"❌ Email template '{template}' missing")
    
    # Check if Support Team role exists
    if frappe.db.exists("Role", "Support Team"):
        print("✅ Support Team role exists")
    else:
        issues.append("❌ Support Team role missing")
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("\n🎉 All validations passed! Notification system is ready to use.")
        return True


def main():
    """Main setup function"""
    print("🚀 Setting up Customer Support Notification System...")
    
    # Validate prerequisites
    if not validate_setup():
        print("\n⚠️  Please fix the issues above before proceeding")
        return
    
    # Create email templates
    create_sample_email_templates()
    
    # Set up default notifications for default company
    company = frappe.defaults.get_user_default("Company") or "WeBeaz Technologies"
    setup_default_notifications(company)
    
    print(f"\n🎉 Customer Support Notification System setup complete!")
    print(f"📋 Next steps:")
    print(f"   1. Go to: Customer Support Notification Settings")
    print(f"   2. Configure your email accounts and recipients")
    print(f"   3. Test the system by creating a sample HD Ticket and changing its status")


if __name__ == "__main__":
    main()