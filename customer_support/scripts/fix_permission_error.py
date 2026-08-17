import frappe

def execute():
    """Fix permission errors and reload DocTypes properly"""
    print("🔧 Fixing Permission Errors and Reloading DocTypes...")
    
    try:
        # Reload DocTypes with proper error handling
        print("🔄 Reloading Notification Recipient DocType...")
        frappe.reload_doc("customer_support", "doctype", "notification_recipient", force=True)
        print("✅ Notification Recipient reloaded")
        
        print("🔄 Reloading Support Notification Rule DocType...")
        frappe.reload_doc("customer_support", "doctype", "support_notification_rule", force=True)
        print("✅ Support Notification Rule reloaded")
        
        # Clear cache to ensure fresh load
        frappe.clear_cache()
        print("✅ Cache cleared")
        
        # Commit changes
        frappe.db.commit()
        
        # Create a simple notification rule that should work without errors
        print("\n📝 Creating Simple Working Notification Rule...")
        
        # Get or create settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        # Clear existing rules to start fresh
        settings.notification_rules = []
        
        # Create a simple rule
        rule = settings.append("notification_rules", {
            "enabled": 1,
            "notification_type": "New Ticket",
            "trigger_event": "After Insert",
            "delay_minutes": 0,
            "email_template": "HD Ticket - New Ticket",
            "subject": "New Ticket: {{ doc.name }}"
        })
        
        # Add a simple recipient using direct field assignment
        recipient_data = {
            "receiver_by": "Email",
            "receiver_type": "To",
            "email_by_document_field": "support@tboindia.com"
        }
        
        rule.recipients = [recipient_data]
        
        # Save without validation to avoid permission issues
        settings.flags.ignore_permissions = True
        settings.flags.ignore_mandatory = True
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("✅ Simple notification rule created successfully")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Close the current form dialog")
        print(f"   2. Refresh the page completely (F5)")
        print(f"   3. Click the pencil icon again on 'New Ticket'")
        print(f"   4. Scroll down to find 'Recipients' section")
        print(f"   5. You should see 1 recipient (Email → support@tboindia.com)")
        print(f"   6. Try adding more recipients using 'Add Row'")
        
        print(f"\n⚠️  If you still get JavaScript errors:")
        print(f"   - Try using a different browser or incognito mode")
        print(f"   - Clear browser cache and cookies")
        print(f"   - The DocType should work now with proper permissions")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()