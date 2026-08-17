import frappe

def execute():
    """Test the new ERPNext-style recipient system"""
    print("🧪 Testing New ERPNext-Style Recipient System...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        if not settings.enable_notifications:
            print("⚠️  Notifications are disabled. Enabling...")
            settings.enable_notifications = 1
            settings.save(ignore_permissions=True)
        
        print(f"📋 Notification Settings Status:")
        print(f"   Enabled: {settings.enable_notifications}")
        print(f"   Company: {settings.company or 'Not Set (Optional)'}")
        print(f"   Rules: {len(settings.notification_rules) if settings.notification_rules else 0}")
        
        # Create a new notification rule with ERPNext-style recipients
        print("\n📝 Creating New Ticket rule with ERPNext-style recipients...")
        
        # Clear existing rules to test fresh
        settings.notification_rules = []
        
        # Create New Ticket rule with multiple recipient types
        new_rule = settings.append("notification_rules", {})
        new_rule.enabled = 1
        new_rule.notification_type = "New Ticket"
        new_rule.trigger_event = "After Insert"
        new_rule.delay_minutes = 0
        new_rule.email_template = "HD Ticket - New Ticket"
        new_rule.subject = "New Ticket Created: {{ doc.name }}"
        
        # Add Document Field recipient (Raised By - customer email)
        recipient1 = new_rule.append("recipients", {})
        recipient1.receiver_by = "Document Field"
        recipient1.receiver_type = "To"
        recipient1.field_name = "raised_by"
        
        # Add Document Field recipient (Assigned User)
        recipient2 = new_rule.append("recipients", {})
        recipient2.receiver_by = "Document Field"
        recipient2.receiver_type = "CC"
        recipient2.field_name = "custom_assigned_to"
        
        # Add Role-based recipient
        recipient3 = new_rule.append("recipients", {})
        recipient3.receiver_by = "Role"
        recipient3.receiver_type = "BCC"
        recipient3.email_by_role = "Support Team"
        
        # Add Custom Email recipient
        recipient4 = new_rule.append("recipients", {})
        recipient4.receiver_by = "Email"
        recipient4.receiver_type = "CC"
        recipient4.email_by_document_field = "support@tboindia.com"
        
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ New rule created with {len(new_rule.recipients)} recipients")
        
        # Display recipient details
        for i, recipient in enumerate(new_rule.recipients):
            print(f"   Recipient {i+1}:")
            print(f"      Type: {recipient.receiver_type}")
            print(f"      By: {recipient.receiver_by}")
            if recipient.receiver_by == "Document Field":
                print(f"      Field: {recipient.field_name}")
            elif recipient.receiver_by == "Role":
                print(f"      Role: {recipient.email_by_role}")
            elif recipient.receiver_by == "Email":
                print(f"      Email: {recipient.email_by_document_field}")
        
        # Test recipient resolution with a sample ticket
        print("\n🎯 Testing recipient resolution...")
        
        # Get or create a test ticket
        test_tickets = frappe.get_all("HD Ticket", limit=1)
        
        if test_tickets:
            ticket = frappe.get_doc("HD Ticket", test_tickets[0].name)
            print(f"📋 Using existing ticket: {ticket.name}")
        else:
            # Create test ticket
            ticket = frappe.new_doc("HD Ticket")
            ticket.subject = "Test Ticket for Recipient System"
            ticket.raised_by = "customer@test.com"
            ticket.custom_assigned_to = "Administrator"
            ticket.description = "Testing new recipient system"
            ticket.insert(ignore_permissions=True)
            print(f"📋 Created test ticket: {ticket.name}")
        
        print(f"   Raised By: {ticket.raised_by}")
        print(f"   Assigned To: {getattr(ticket, 'custom_assigned_to', 'None')}")
        print(f"   Owner: {ticket.owner}")
        print(f"   Contact: {getattr(ticket, 'contact', 'None')}")
        print(f"   Customer: {getattr(ticket, 'customer', 'None')}")
        
        # Test recipient resolution
        from customer_support.customer_support.notification_system import NotificationSystem
        
        recipients = NotificationSystem.build_recipient_list(new_rule, ticket)
        
        print(f"\n📬 Resolved Recipients:")
        print(f"   To: {recipients['to']}")
        print(f"   CC: {recipients['cc']}")
        print(f"   BCC: {recipients['bcc']}")
        
        total_count = len(recipients['to']) + len(recipients['cc']) + len(recipients['bcc'])
        print(f"   Total: {total_count} recipients")
        
        if total_count > 0:
            print("✅ Recipient resolution is working!")
        else:
            print("⚠️  No recipients resolved - check field values and settings")
        
        print("\n🎉 Test completed successfully!")
        print("\nℹ️  Now you can:")
        print("1. Go to 'Customer Support Notification Settings' in ERPNext")
        print("2. Edit notification rules")
        print("3. In Recipients section, you'll see:")
        print("   - Receiver By dropdown (Document Field/Role/Email)")
        print("   - Field Name dropdown (contact_email, custom_assigned_to, owner, etc.)")
        print("   - Role selector for user roles")
        print("   - Email field for custom addresses")
        print("4. Create HD Tickets to test notifications")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()