import frappe

def execute():
    """Add sample recipients to the existing notification rule"""
    print("📝 Adding Sample Recipients to New Ticket Rule...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        if not settings.notification_rules:
            print("❌ No notification rules found!")
            return
            
        # Get the first (New Ticket) rule
        rule = settings.notification_rules[0]
        
        print(f"📋 Working with rule: {rule.notification_type}")
        
        # Clear existing recipients
        rule.recipients = []
        
        # Add recipient 1: Send to customer (raised_by)
        recipient1 = rule.append("recipients", {})
        recipient1.receiver_by = "Document Field"
        recipient1.receiver_type = "To"
        recipient1.field_name = "raised_by"
        
        # Add recipient 2: CC to assigned agent
        recipient2 = rule.append("recipients", {})
        recipient2.receiver_by = "Document Field"
        recipient2.receiver_type = "CC"
        recipient2.field_name = "custom_assigned_to"
        
        # Add recipient 3: BCC to Support Team
        recipient3 = rule.append("recipients", {})
        recipient3.receiver_by = "Role"
        recipient3.receiver_type = "BCC"
        recipient3.email_by_role = "Support Team"
        
        # Add recipient 4: CC to custom email
        recipient4 = rule.append("recipients", {})
        recipient4.receiver_by = "Email"
        recipient4.receiver_type = "CC"
        recipient4.email_by_document_field = "admin@tboindia.com"
        
        # Save settings
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ Added {len(rule.recipients)} sample recipients:")
        for i, recipient in enumerate(rule.recipients, 1):
            print(f"   {i}. {recipient.receiver_type}: {recipient.receiver_by}", end="")
            if recipient.receiver_by == "Document Field":
                print(f" → {recipient.field_name}")
            elif recipient.receiver_by == "Role":
                print(f" → {recipient.email_by_role}")
            elif recipient.receiver_by == "Email":
                print(f" → {recipient.email_by_document_field}")
        
        print(f"\n🔄 Please refresh the page to see the recipients!")
        print(f"📋 Instructions:")
        print(f"   1. Refresh/reload the Customer Support Notification Settings page")
        print(f"   2. You should now see the Recipients column in the table")
        print(f"   3. Click on the New Ticket rule to edit and see all recipient details")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()