#!/usr/bin/env python3

"""
Setup simple recipient fields for easy email configuration
"""

import frappe


def setup_simple_recipients():
    """Setup simple recipient fields in notification rules"""
    
    print("📧 SETTING UP SIMPLE RECIPIENTS")
    print("=" * 40)
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📋 Found {len(settings.notification_rules)} notification rules")
        
        # Setup recipients for each rule type
        for rule in settings.notification_rules:
            print(f"\n🔧 Setting up: {rule.notification_type}")
            
            if rule.notification_type == "New Ticket":
                # New ticket: Send to support team and customer
                rule.to_recipients = "support@teambackoffice.com"
                rule.cc_recipients = "Customer"  # Special keyword for ticket contact email
                rule.bcc_recipients = ""
                print("   ✅ To: support@teambackoffice.com")
                print("   ✅ CC: Customer (ticket contact email)")
                
            elif rule.notification_type == "Escalation":
                # Escalation: Send to management with support in CC
                rule.to_recipients = "manager@teambackoffice.com, support@teambackoffice.com"
                rule.cc_recipients = "Customer"
                rule.bcc_recipients = ""
                print("   ✅ To: manager@teambackoffice.com, support@teambackoffice.com")
                print("   ✅ CC: Customer")
                
            elif rule.notification_type == "Resolved":
                # Resolved: Mainly to customer with support in CC
                rule.to_recipients = "Customer"
                rule.cc_recipients = "support@teambackoffice.com"
                rule.bcc_recipients = ""
                print("   ✅ To: Customer")
                print("   ✅ CC: support@teambackoffice.com")
        
        # Save the updated settings
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("\n✅ Simple recipients configured successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return False


def show_recipient_instructions():
    """Show instructions for using the recipient fields"""
    
    print("\n📋 HOW TO USE RECIPIENT FIELDS")
    print("=" * 35)
    
    print("\n🎯 Available Recipient Types:")
    print("   📧 Email addresses: user@domain.com")
    print("   👤 Customer: Use 'Customer' keyword for ticket contact email")
    print("   👨‍💼 Assigned Agent: Use 'Assigned_Agent' for assigned user")
    print("   🏢 Ticket Owner: Use 'Ticket_Owner' for ticket creator")
    print("   📝 Multiple emails: Separate with commas")
    
    print("\n💡 Examples:")
    print("   To Recipients:")
    print("     support@teambackoffice.com")
    print("     Customer, manager@teambackoffice.com")
    print("     support@teambackoffice.com, admin@teambackoffice.com")
    
    print("\n   CC Recipients:")
    print("     Customer")
    print("     Assigned_Agent")
    print("     manager@teambackoffice.com")
    
    print("\n🔧 Where to Edit:")
    print("   1. Go to: Customer Support Notification Settings")
    print("   2. Click on any notification rule row")
    print("   3. You'll see the recipient fields in the form")
    print("   4. Enter emails or keywords as shown above")


def test_simple_recipients():
    """Test the simple recipient system"""
    
    print("\n🧪 TESTING SIMPLE RECIPIENTS")
    print("=" * 30)
    
    try:
        # Create a test ticket
        from frappe.utils import now_datetime
        
        timestamp = now_datetime().strftime("%Y%m%d_%H%M%S")
        
        ticket = frappe.new_doc("HD Ticket")
        ticket.subject = f"Simple Recipients Test {timestamp}"
        ticket.description = "Testing simple recipient fields"
        ticket.contact_email = "testcustomer@example.com"
        ticket.status = "Open"
        ticket.custom_assigned_to = "Administrator"
        
        # Don't save to DB, just test parsing
        print(f"📝 Test ticket created (not saved)")
        print(f"   Customer email: {ticket.contact_email}")
        print(f"   Assigned to: {ticket.custom_assigned_to}")
        
        # Test recipient parsing
        from customer_support.customer_support.notification_system import NotificationSystem
        
        # Get new ticket rule
        settings = frappe.get_single("Customer Support Notification Settings")
        new_ticket_rule = None
        
        for rule in settings.notification_rules:
            if rule.notification_type == "New Ticket":
                new_ticket_rule = rule
                break
        
        if new_ticket_rule:
            print(f"\n📧 Testing New Ticket rule recipients:")
            print(f"   To: {new_ticket_rule.to_recipients}")
            print(f"   CC: {new_ticket_rule.cc_recipients}")
            
            # Parse recipients
            to_emails = NotificationSystem.parse_recipient_emails(new_ticket_rule.to_recipients, ticket)
            cc_emails = NotificationSystem.parse_recipient_emails(new_ticket_rule.cc_recipients, ticket)
            
            print(f"\n✅ Parsed Results:")
            print(f"   To emails: {to_emails}")
            print(f"   CC emails: {cc_emails}")
            
            if to_emails or cc_emails:
                print(f"✅ Simple recipients working correctly!")
                return True
            else:
                print(f"❌ No emails parsed - check configuration")
                return False
        else:
            print("❌ No New Ticket rule found")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


def main():
    """Main setup function"""
    
    print("🚀 SIMPLE RECIPIENTS SETUP")
    print("=" * 30)
    
    # Step 1: Setup simple recipients
    if setup_simple_recipients():
        print("\n✅ Step 1: Recipients configured")
    else:
        print("\n❌ Step 1: Setup failed")
        return
    
    # Step 2: Show instructions
    show_recipient_instructions()
    
    # Step 3: Test the system
    if test_simple_recipients():
        print("\n✅ Step 3: Testing successful")
    else:
        print("\n❌ Step 3: Testing failed")
    
    print(f"\n🎉 SETUP COMPLETE!")
    print(f"=" * 20)
    print(f"✅ Simple recipient fields are now configured")
    print(f"✅ You can easily edit recipients in the UI")
    print(f"✅ Use keywords like 'Customer' for dynamic emails")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Refresh your browser page")
    print(f"   2. Go to Customer Support Notification Settings")
    print(f"   3. Click on any notification rule to edit recipients")
    print(f"   4. Test with a real HD Ticket")


if __name__ == "__main__":
    main()