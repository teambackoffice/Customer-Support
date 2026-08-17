import frappe

def execute():
    """Check current recipients in the notification rule"""
    print("🔍 Checking Current Recipients Configuration...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        if not settings.notification_rules:
            print("❌ No notification rules found!")
            return
        
        rule = settings.notification_rules[0]
        
        print(f"📋 Rule Details:")
        print(f"   Name: {rule.notification_type}")
        print(f"   Enabled: {rule.enabled}")
        print(f"   Trigger: {rule.trigger_event}")
        print(f"   Template: {getattr(rule, 'email_template', 'None')}")
        
        # Check recipients
        if hasattr(rule, 'recipients'):
            print(f"\n👥 Recipients (Total: {len(rule.recipients)}):")
            
            if rule.recipients:
                for i, recipient in enumerate(rule.recipients, 1):
                    print(f"   {i}. {recipient.receiver_type}:")
                    print(f"      Receiver By: {recipient.receiver_by}")
                    
                    if recipient.receiver_by == "Document Field":
                        print(f"      Field Name: {getattr(recipient, 'field_name', 'Not Set')}")
                    elif recipient.receiver_by == "Role":
                        print(f"      Role: {getattr(recipient, 'email_by_role', 'Not Set')}")
                    elif recipient.receiver_by == "Email":
                        print(f"      Email: {getattr(recipient, 'email_by_document_field', 'Not Set')}")
                    
                    print()
            else:
                print("   ⚠️  No recipients found in the rule!")
        else:
            print("\n❌ Recipients field not found in rule!")
        
        # Show what the user should see in the form
        print(f"\n📝 What You Should See in Form:")
        print(f"   1. Basic fields (Enabled, Notification Type, etc.)")
        print(f"   2. Recipients section with a table containing {len(rule.recipients) if hasattr(rule, 'recipients') and rule.recipients else 0} rows")
        print(f"   3. Each row should show: Receiver By, Receiver Type, and field/role/email")
        
        # Check if form might be missing fields
        print(f"\n🔧 If Recipients section is not visible:")
        print(f"   1. Make sure you scrolled down in the form")
        print(f"   2. Look for a section titled 'Recipients'")
        print(f"   3. There should be a table/grid below it")
        print(f"   4. The table should have 'Add Row' button if empty")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()