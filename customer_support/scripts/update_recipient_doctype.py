#!/usr/bin/env python3
"""
Script to reload the Notification Recipient DocType with ERPNext-style field selection
"""

import frappe
import json
import os

def reload_notification_recipient_doctype():
    """Reload the Notification Recipient DocType"""
    print("🔄 Reloading Notification Recipient DocType...")
    
    try:
        # Import the updated DocType
        frappe.reload_doc("customer_support", "doctype", "notification_recipient")
        print("✅ Notification Recipient DocType reloaded successfully")
        
        # Also reload Support Notification Rule to ensure table link is updated
        frappe.reload_doc("customer_support", "doctype", "support_notification_rule")
        print("✅ Support Notification Rule DocType reloaded successfully")
        
        frappe.db.commit()
        
    except Exception as e:
        print(f"❌ Error reloading DocTypes: {str(e)}")
        frappe.db.rollback()
        raise

def create_test_notification_rule():
    """Create a test notification rule with the new recipient structure"""
    print("\n📝 Creating test notification rule...")
    
    try:
        # Get or create notification settings
        settings_name = "Customer Support Notification Settings"
        
        if not frappe.db.exists("Customer Support Notification Settings", settings_name):
            settings = frappe.new_doc("Customer Support Notification Settings")
            settings.enable_notifications = 1
            settings.company = ""  # Optional as requested
            settings.insert(ignore_permissions=True)
        else:
            settings = frappe.get_doc("Customer Support Notification Settings", settings_name)
        
        # Clear existing rules
        settings.notification_rules = []
        
        # Create New Ticket notification rule
        new_ticket_rule = {
            "enabled": 1,
            "notification_type": "New Ticket",
            "trigger_event": "After Insert",
            "delay_minutes": 0,
            "email_template": "HD Ticket New",
            "subject": "New Support Ticket: {{ doc.name }} - {{ doc.subject }}",
            "recipients": [
                {
                    "receiver_by": "Document Field",
                    "receiver_type": "To", 
                    "field_name": "contact_email"
                },
                {
                    "receiver_by": "Document Field",
                    "receiver_type": "CC",
                    "field_name": "custom_assigned_to"
                }
            ]
        }
        
        # Create Escalation notification rule
        escalation_rule = {
            "enabled": 1,
            "notification_type": "Escalation",
            "trigger_event": "Scheduler",
            "delay_minutes": 15,
            "email_template": "HD Ticket Escalation",
            "subject": "Ticket Escalation: {{ doc.name }} - {{ doc.subject }}",
            "recipients": [
                {
                    "receiver_by": "Document Field",
                    "receiver_type": "To",
                    "field_name": "custom_assigned_to"
                },
                {
                    "receiver_by": "Role",
                    "receiver_type": "CC",
                    "email_by_role": "Support Team"
                }
            ]
        }
        
        # Add rules to settings
        settings.append("notification_rules", new_ticket_rule)
        settings.append("notification_rules", escalation_rule)
        
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ Test notification rules created with {len(settings.notification_rules)} rules")
        
        return settings
        
    except Exception as e:
        print(f"❌ Error creating test rules: {str(e)}")
        frappe.db.rollback()
        raise

def test_recipient_resolution():
    """Test the new recipient resolution system"""
    print("\n🧪 Testing recipient resolution...")
    
    try:
        # Get a sample HD Ticket for testing
        sample_ticket = frappe.get_all("HD Ticket", limit=1)
        
        if not sample_ticket:
            print("⚠️  No HD Ticket found for testing. Creating a test ticket...")
            
            # Create a test ticket
            test_ticket = frappe.new_doc("HD Ticket")
            test_ticket.subject = "Test Ticket for Notification System"
            test_ticket.contact_email = "customer@test.com"
            test_ticket.custom_assigned_to = "Administrator"
            test_ticket.description = "This is a test ticket for notification system"
            test_ticket.insert(ignore_permissions=True)
            
            ticket_name = test_ticket.name
        else:
            ticket_name = sample_ticket[0].name
        
        # Load the ticket
        ticket = frappe.get_doc("HD Ticket", ticket_name)
        print(f"📋 Using ticket: {ticket.name}")
        print(f"   Contact Email: {ticket.contact_email}")
        print(f"   Assigned To: {getattr(ticket, 'custom_assigned_to', 'None')}")
        print(f"   Owner: {ticket.owner}")
        
        # Get notification settings and test recipient resolution
        from customer_support.customer_support.notification_system import NotificationSystem
        
        settings = NotificationSystem.get_notification_settings()
        if settings and settings.notification_rules:
            
            for rule in settings.notification_rules:
                print(f"\n📬 Testing rule: {rule.notification_type}")
                
                recipients = NotificationSystem.build_recipient_list(rule, ticket)
                
                print(f"   To: {recipients['to']}")
                print(f"   CC: {recipients['cc']}")
                print(f"   BCC: {recipients['bcc']}")
                
                total_recipients = len(recipients['to']) + len(recipients['cc']) + len(recipients['bcc'])
                print(f"   Total Recipients: {total_recipients}")
        
        print("✅ Recipient resolution test completed")
        
    except Exception as e:
        print(f"❌ Error testing recipient resolution: {str(e)}")
        raise

def main():
    """Main execution function"""
    print("🚀 Starting Notification Recipient DocType Update...")
    
    try:
        frappe.init(site="tboindia")
        frappe.connect()
        
        # Step 1: Reload DocTypes
        reload_notification_recipient_doctype()
        
        # Step 2: Create test rules with new recipient structure
        create_test_notification_rule()
        
        # Step 3: Test recipient resolution
        test_recipient_resolution()
        
        print("\n✅ All tasks completed successfully!")
        print("\nℹ️  Next steps:")
        print("1. Go to Customer Support Notification Settings in ERPNext")
        print("2. Check the Recipients section in notification rules")
        print("3. You should now see ERPNext-style field selection:")
        print("   - Receiver By: Document Field / Role / Email")
        print("   - Field Name: contact_email, custom_assigned_to, owner, etc.")
        print("   - Role: Support Team, etc.")
        print("   - Email: Custom email addresses")
        
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()