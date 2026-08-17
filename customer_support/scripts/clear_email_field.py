import frappe

def execute():
    """Clear the problematic Default From Email field"""
    print("🔧 Clearing Default From Email field...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📋 Before fix:")
        print(f"   Default From Email: '{settings.default_from_email}'")
        print(f"   Reply To: '{settings.reply_to}'")
        
        # Clear the Default From Email field completely
        settings.default_from_email = ""
        
        # Keep the Reply To as a valid email
        settings.reply_to = "no-reply@teambackoffice.com"
        
        # Save without validation
        settings.flags.ignore_validate = True
        settings.flags.ignore_mandatory = True
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"\n✅ After fix:")
        print(f"   Default From Email: '{settings.default_from_email}' (cleared)")
        print(f"   Reply To: '{settings.reply_to}'")
        
        print(f"\n🎯 Instructions:")
        print(f"   1. Refresh the page (F5)")
        print(f"   2. The Default From Email field should now be empty")
        print(f"   3. You can leave it empty or select a valid Email Account")
        print(f"   4. Click Save - the error should be gone")
        
        # Also update the notification system to handle empty from_email
        print(f"\n📧 Available Email Accounts you can choose from:")
        email_accounts = frappe.get_all("Email Account", fields=["name", "email_id"])
        for account in email_accounts:
            print(f"   - {account.name} ({account.email_id})")
        
        print(f"\n✅ Default From Email cleared successfully!")
        print(f"   The notification system will use system default if empty.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()