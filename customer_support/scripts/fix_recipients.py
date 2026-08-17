#!/usr/bin/env python3

"""
Fix recipients in notification rules
"""

import frappe


def fix_recipients():
    """Add recipients to existing notification rules"""
    
    print("🔧 Fixing recipients in notification rules...")
    
    try:
        # Get settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📋 Found {len(settings.notification_rules)} notification rules")
        
        # Fix each rule
        for rule in settings.notification_rules:
            print(f"\n🔧 Fixing rule: {rule.notification_type}")
            
            # Clear existing recipients
            rule.recipients = []
            
            if rule.notification_type == "New Ticket":
                # Add customer recipient
                customer_recipient = frappe.new_doc("Notification Recipient")
                customer_recipient.recipient_role = "To"
                customer_recipient.recipient_type = "Customer"
                customer_recipient.parent = rule.name
                customer_recipient.parentfield = "recipients"
                customer_recipient.parenttype = "Support Notification Rule"
                customer_recipient.insert(ignore_permissions=True)
                
                # Add support team recipient
                support_recipient = frappe.new_doc("Notification Recipient")
                support_recipient.recipient_role = "CC"
                support_recipient.recipient_type = "Custom Email"
                support_recipient.custom_email = "support@teambackoffice.com"
                support_recipient.parent = rule.name
                support_recipient.parentfield = "recipients"
                support_recipient.parenttype = "Support Notification Rule"
                support_recipient.insert(ignore_permissions=True)
                
                print("   ✅ Added Customer (To) and Support Team (CC)")
                
            elif rule.notification_type == "Escalation":
                # Add support team recipient
                support_recipient = frappe.new_doc("Notification Recipient")
                support_recipient.recipient_role = "To"
                support_recipient.recipient_type = "Custom Email"
                support_recipient.custom_email = "support@teambackoffice.com, manager@teambackoffice.com"
                support_recipient.parent = rule.name
                support_recipient.parentfield = "recipients"
                support_recipient.parenttype = "Support Notification Rule"
                support_recipient.insert(ignore_permissions=True)
                
                # Add customer as CC
                customer_recipient = frappe.new_doc("Notification Recipient")
                customer_recipient.recipient_role = "CC"
                customer_recipient.recipient_type = "Customer"
                customer_recipient.parent = rule.name
                customer_recipient.parentfield = "recipients"
                customer_recipient.parenttype = "Support Notification Rule"
                customer_recipient.insert(ignore_permissions=True)
                
                print("   ✅ Added Support Team (To) and Customer (CC)")
                
            elif rule.notification_type == "Resolved":
                # Add customer recipient
                customer_recipient = frappe.new_doc("Notification Recipient")
                customer_recipient.recipient_role = "To"
                customer_recipient.recipient_type = "Customer"
                customer_recipient.parent = rule.name
                customer_recipient.parentfield = "recipients"
                customer_recipient.parenttype = "Support Notification Rule"
                customer_recipient.insert(ignore_permissions=True)
                
                print("   ✅ Added Customer (To)")
        
        frappe.db.commit()
        
        print("\n✅ Recipients fixed successfully!")
        
        # Verify the fix
        print("\n🔍 Verifying recipients...")
        settings.reload()
        
        for rule in settings.notification_rules:
            recipients_count = frappe.db.count("Notification Recipient", 
                filters={"parent": rule.name})
            print(f"   {rule.notification_type}: {recipients_count} recipients")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix recipients: {str(e)}")
        frappe.log_error(f"Failed to fix recipients: {str(e)}", "Fix Recipients Error")
        return False


def test_notification_manually():
    """Test notification system manually"""
    
    print("\n🧪 Testing notification system manually...")
    
    try:
        # Create a simple test ticket
        ticket = frappe.new_doc("HD Ticket")
        ticket.subject = "Manual Test Ticket"
        ticket.description = "Testing notifications manually"
        ticket.contact_email = "test@example.com"
        ticket.status = "Open"
        
        ticket.insert(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ Created test ticket: {ticket.name}")
        
        # Test notification system
        from customer_support.customer_support.notification_system import NotificationSystem
        
        # Test new ticket notification
        success = NotificationSystem.send_notification(ticket, "New Ticket", "After Insert")
        print(f"📧 New ticket notification: {'✅ Success' if success else '❌ Failed'}")
        
        return ticket
        
    except Exception as e:
        print(f"❌ Manual test failed: {str(e)}")
        return None


def main():
    """Main function"""
    print("🚀 Fixing Notification System Recipients")
    print("=" * 45)
    
    if fix_recipients():
        test_notification_manually()
        print("\n🎉 Recipients fix completed!")
    else:
        print("\n❌ Recipients fix failed!")


if __name__ == "__main__":
    main()