import frappe

def execute():
    """Add recipients directly to the notification rule"""
    print("📝 Adding Recipients Directly to Current Rule...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        if not settings.notification_rules:
            print("❌ No notification rules found!")
            return
        
        rule = settings.notification_rules[0]
        print(f"📋 Working with rule: {rule.notification_type}")
        
        # Ensure recipients field exists
        if not hasattr(rule, 'recipients') or rule.recipients is None:
            rule.recipients = []
        
        # Clear existing recipients
        rule.recipients = []
        
        print("🧹 Cleared existing recipients")
        
        # Add recipients one by one with error handling
        try:
            # Recipient 1: Customer email
            recipient1 = frappe._dict()
            recipient1.receiver_by = "Document Field"
            recipient1.receiver_type = "To"
            recipient1.field_name = "raised_by"
            rule.recipients.append(recipient1)
            print("✅ Added recipient 1: Customer email")
            
            # Recipient 2: Assigned agent
            recipient2 = frappe._dict()
            recipient2.receiver_by = "Document Field"
            recipient2.receiver_type = "CC"
            recipient2.field_name = "custom_assigned_to"
            rule.recipients.append(recipient2)
            print("✅ Added recipient 2: Assigned agent")
            
            # Recipient 3: Custom email
            recipient3 = frappe._dict()
            recipient3.receiver_by = "Email"
            recipient3.receiver_type = "CC"
            recipient3.email_by_document_field = "support@tboindia.com"
            rule.recipients.append(recipient3)
            print("✅ Added recipient 3: Custom email")
            
        except Exception as e:
            print(f"❌ Error adding recipients: {str(e)}")
        
        # Save settings
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"\n✅ Successfully added {len(rule.recipients)} recipients!")
        
        # Verify recipients were saved
        print(f"\n📋 Verification:")
        for i, recipient in enumerate(rule.recipients, 1):
            print(f"   {i}. {recipient.receiver_type}: {recipient.receiver_by}")
            if recipient.receiver_by == "Document Field":
                print(f"      → Field: {recipient.field_name}")
            elif recipient.receiver_by == "Email":
                print(f"      → Email: {recipient.email_by_document_field}")
        
        print(f"\n🔄 Now in your form:")
        print(f"   1. Look for 'Recipients' section (scroll down if needed)")
        print(f"   2. You should see a table with {len(rule.recipients)} rows")
        print(f"   3. Each row shows Receiver By, Receiver Type, and field/email")
        print(f"   4. You can click 'Add Row' to add more recipients")
        print(f"   5. You can edit existing recipients by clicking on them")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()