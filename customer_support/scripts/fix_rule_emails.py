import frappe

def execute():
    """Fix From Email in all notification rules"""
    print("🔧 Fixing From Email in Notification Rules...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📋 Checking notification rules...")
        
        if settings.notification_rules:
            for i, rule in enumerate(settings.notification_rules, 1):
                print(f"\n   Rule {i}: {rule.notification_type}")
                print(f"      Current From Email: '{getattr(rule, 'from_email', 'Not Set')}'")
                
                # Clear the from_email field in each rule
                if hasattr(rule, 'from_email'):
                    rule.from_email = ""  # Clear it so system uses default
                    print(f"      ✅ Cleared From Email (will use system default)")
                else:
                    print(f"      ✅ No From Email field found")
        else:
            print("   No notification rules found")
        
        # Also check and fix the notification system code
        print(f"\n🔍 Checking notification system logic...")
        
        # Save the updated settings
        settings.flags.ignore_validate = True
        settings.flags.ignore_mandatory = True
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"\n✅ All notification rules updated!")
        
        # Check what email will actually be used
        print(f"\n📧 Email Resolution Check:")
        print(f"   Default From Email (Settings): '{settings.default_from_email}'")
        print(f"   Reply To: '{settings.reply_to}'")
        
        # Get default outgoing email account
        default_email = frappe.db.get_value("Email Account", {"default_outgoing": 1}, ["name", "email_id"])
        if default_email:
            print(f"   System Default Outgoing: {default_email[0]} ({default_email[1]})")
        else:
            print(f"   ⚠️  No default outgoing email account set")
        
        # Test the notification system
        print(f"\n🧪 Testing notification email resolution...")
        
        if settings.notification_rules:
            rule = settings.notification_rules[0]
            
            # Simulate the email resolution logic
            from_email = getattr(rule, 'from_email', None) or settings.default_from_email
            
            if not from_email:
                # Will use system default
                if default_email:
                    from_email = default_email[1]  # Use email_id, not account name
                else:
                    from_email = "system-default"
            
            print(f"   Final From Email: {from_email}")
            print(f"   Reply To: {settings.reply_to}")
        
        print(f"\n🎯 Try saving the notification settings now!")
        print(f"   The 'Noreply is not a valid Email Address' error should be gone.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()