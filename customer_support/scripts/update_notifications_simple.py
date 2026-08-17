import frappe

def execute():
    """Simple function to reload DocTypes and update notification settings"""
    print("🔄 Reloading Notification Recipient DocType...")
    
    try:
        # Reload the updated DocTypes
        frappe.reload_doc("customer_support", "doctype", "notification_recipient")
        print("✅ Notification Recipient DocType reloaded")
        
        frappe.reload_doc("customer_support", "doctype", "support_notification_rule")  
        print("✅ Support Notification Rule DocType reloaded")
        
        # Get or update notification settings
        settings_name = "Customer Support Notification Settings"
        
        if frappe.db.exists("Customer Support Notification Settings", settings_name):
            settings = frappe.get_doc("Customer Support Notification Settings", settings_name)
            print(f"📋 Found existing notification settings")
            
            # Show current rules count
            print(f"   Current rules: {len(settings.notification_rules) if settings.notification_rules else 0}")
            
            # Test recipient structure
            if settings.notification_rules:
                for i, rule in enumerate(settings.notification_rules):
                    print(f"   Rule {i+1}: {rule.notification_type}")
                    if hasattr(rule, 'recipients') and rule.recipients:
                        print(f"      Recipients: {len(rule.recipients)}")
                        for j, recipient in enumerate(rule.recipients):
                            print(f"         {j+1}. {getattr(recipient, 'receiver_by', 'N/A')} - {getattr(recipient, 'receiver_type', 'N/A')}")
        else:
            print("⚠️  No notification settings found")
            
        frappe.db.commit()
        
        print("\n✅ Update completed!")
        print("\nℹ️  Go to 'Customer Support Notification Settings' in ERPNext to see the new recipient fields:")
        print("   - Receiver By: Document Field, Role, or Email")
        print("   - Field Name: Select from HD Ticket fields")
        print("   - Role: Select user roles")
        print("   - Email: Enter custom emails")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        raise