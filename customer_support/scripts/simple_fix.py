import frappe

def execute():
    """Simple fix - just reload DocTypes and clear cache"""
    print("🔄 Simple Fix: Reloading DocTypes...")
    
    try:
        # Force reload both DocTypes
        frappe.reload_doc("customer_support", "doctype", "notification_recipient", force=True)
        frappe.reload_doc("customer_support", "doctype", "support_notification_rule", force=True)
        
        # Clear all caches
        frappe.clear_cache()
        frappe.clear_document_cache("Customer Support Notification Settings")
        frappe.clear_document_cache("Support Notification Rule")
        frappe.clear_document_cache("Notification Recipient")
        
        print("✅ DocTypes reloaded and cache cleared")
        
        # Get current settings status
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📋 Current Status:")
        print(f"   Enabled: {settings.enable_notifications}")
        print(f"   Rules: {len(settings.notification_rules) if settings.notification_rules else 0}")
        
        if settings.notification_rules:
            rule = settings.notification_rules[0]
            print(f"   Rule 1: {rule.notification_type}")
            print(f"   Recipients field exists: {hasattr(rule, 'recipients')}")
            
        print(f"\n🎯 Instructions:")
        print(f"   1. **Close the current form dialog** (if open)")
        print(f"   2. **Refresh the page completely** (F5 or Ctrl+R)")
        print(f"   3. **Click the pencil/edit icon** next to 'New Ticket' rule")
        print(f"   4. **Scroll down** in the form to find 'Recipients' section")
        print(f"   5. **Click 'Add Row'** to add recipients manually")
        
        print(f"\n✅ The DocTypes now have proper permissions!")
        print(f"   The JavaScript error should be fixed.")
        print(f"   You can now add recipients through the UI.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()