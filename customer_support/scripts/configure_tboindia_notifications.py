#!/usr/bin/env python3

"""
Configure notification system for tboindia site
"""

import frappe


def configure_notifications():
    """Configure notification system for tboindia"""
    
    print("🚀 Configuring Customer Support Notification System for tboindia...")
    
    try:
        # Get notification settings (Single DocType)
        settings = frappe.get_single("Customer Support Notification Settings")
        
        # Update basic settings
        settings.company = "TBO TEAM BACK OFFICE INTERNATIONAL LLP"
        settings.enable_notifications = 1
        settings.reply_to = "support@teambackoffice.com"
        
        # Set default from email if available
        email_accounts = frappe.get_all("Email Account", 
            filters={"enable_outgoing": 1}, 
            limit=1, pluck="name")
        if email_accounts:
            settings.default_from_email = email_accounts[0]
            print(f"📧 Set default email account: {email_accounts[0]}")
        else:
            print("⚠️  No outgoing email account found - please configure one")
        
        # Clear existing notification rules
        settings.notification_rules = []
        
        # Add New Ticket notification rule
        new_ticket_rule = settings.append("notification_rules", {})
        new_ticket_rule.enabled = 1
        new_ticket_rule.notification_type = "New Ticket"
        new_ticket_rule.trigger_event = "After Insert"
        new_ticket_rule.delay_minutes = 0
        new_ticket_rule.email_template = "HD Ticket - New Ticket"
        new_ticket_rule.subject = "New Support Ticket: {{ doc.name }} - {{ doc.subject }}"
        
        # Add recipients for new ticket
        customer_recipient = new_ticket_rule.append("recipients", {})
        customer_recipient.recipient_role = "To"
        customer_recipient.recipient_type = "Customer"
        
        support_recipient = new_ticket_rule.append("recipients", {})
        support_recipient.recipient_role = "CC"
        support_recipient.recipient_type = "Support Team"
        
        # Add Escalation notification rule
        escalation_rule = settings.append("notification_rules", {})
        escalation_rule.enabled = 1
        escalation_rule.notification_type = "Escalation"
        escalation_rule.trigger_event = "Status Change"
        escalation_rule.delay_minutes = 0
        escalation_rule.email_template = "HD Ticket - Escalation"
        escalation_rule.subject = "ESCALATION: Agent replied to ticket {{ doc.name }}"
        
        # Add recipients for escalation
        support_escalation = escalation_rule.append("recipients", {})
        support_escalation.recipient_role = "To"
        support_escalation.recipient_type = "Support Team"
        
        manager_escalation = escalation_rule.append("recipients", {})
        manager_escalation.recipient_role = "CC"
        manager_escalation.recipient_type = "Department Manager"
        
        # Add Resolved notification rule
        resolved_rule = settings.append("notification_rules", {})
        resolved_rule.enabled = 1
        resolved_rule.notification_type = "Resolved"
        resolved_rule.trigger_event = "Status Change"
        resolved_rule.delay_minutes = 0
        resolved_rule.email_template = "HD Ticket - Resolved"
        resolved_rule.subject = "✅ Ticket Resolved: {{ doc.name }} - {{ doc.subject }}"
        
        # Add recipient for resolved
        customer_resolved = resolved_rule.append("recipients", {})
        customer_resolved.recipient_role = "To"
        customer_resolved.recipient_type = "Customer"
        
        # Save settings
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("✅ Notification system configured successfully!")
        print(f"🏢 Company: {settings.company}")
        print(f"📧 Notifications enabled: {settings.enable_notifications}")
        print(f"📬 Default email: {settings.default_from_email}")
        print(f"📋 Notification rules created: {len(settings.notification_rules)}")
        
        # List the rules
        for i, rule in enumerate(settings.notification_rules, 1):
            print(f"   {i}. {rule.notification_type} - {rule.trigger_event}")
            print(f"      Recipients: {len(rule.recipients)}")
        
        return settings
        
    except Exception as e:
        print(f"❌ Configuration failed: {str(e)}")
        frappe.log_error(f"Notification configuration failed: {str(e)}", "Configuration Error")
        return None


def test_configuration():
    """Test the notification configuration"""
    
    print("\n🧪 Testing Configuration...")
    
    try:
        settings = frappe.get_single("Customer Support Notification Settings")
        
        if settings.enable_notifications:
            print("✅ Notifications are enabled")
        else:
            print("❌ Notifications are disabled")
            
        if settings.company:
            print(f"✅ Company set: {settings.company}")
        else:
            print("❌ Company not set")
            
        if settings.notification_rules:
            print(f"✅ {len(settings.notification_rules)} notification rules configured")
            for rule in settings.notification_rules:
                if rule.enabled:
                    print(f"  ✅ {rule.notification_type} - {rule.trigger_event}")
                else:
                    print(f"  ⚠️  {rule.notification_type} - {rule.trigger_event} (disabled)")
        else:
            print("❌ No notification rules configured")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


def main():
    """Main function"""
    configure_notifications()
    test_configuration()
    
    print("\n🎉 Configuration complete!")
    print("\n📋 Next steps:")
    print("   1. Go to: Setup → Customer Support Notification Settings")
    print("   2. Review and adjust notification rules if needed")
    print("   3. Configure email accounts if not already done")
    print("   4. Test by creating an HD Ticket")


if __name__ == "__main__":
    main()