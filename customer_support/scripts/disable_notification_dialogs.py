import frappe

def execute():
    """Disable notification system to prevent template dialogs and check what's triggering them"""
    print("🔧 Investigating Jinja Template Error Source...")
    
    try:
        # First, let's temporarily disable notifications to see what's causing the dialog
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📋 Current Notification Settings:")
        print(f"   Notifications Enabled: {settings.enable_notifications}")
        print(f"   Rules Count: {len(settings.notification_rules) if settings.notification_rules else 0}")
        
        # Disable notifications temporarily
        settings.enable_notifications = 0
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ Temporarily disabled notifications")
        
        # Check if there are any hooks that might be triggering the template error
        print(f"\n🔍 Checking for notification hooks...")
        
        # Check the hooks.py file to see what's registered
        try:
            from customer_support import hooks
            if hasattr(hooks, 'doc_events'):
                print(f"   Doc Events Found: {hooks.doc_events}")
            else:
                print(f"   No doc_events found in hooks")
        except Exception as e:
            print(f"   Error checking hooks: {str(e)}")
        
        # Check if there are any auto-notification settings in ERPNext
        print(f"\n📧 Checking ERPNext Auto Email Settings...")
        
        # Check for any auto email reports or notifications
        auto_emails = frappe.get_all("Auto Email Report", fields=["name", "report", "enabled"])
        if auto_emails:
            print(f"   Found {len(auto_emails)} Auto Email Reports")
            for email in auto_emails:
                print(f"      - {email.name}: {email.report} (Enabled: {email.enabled})")
        else:
            print(f"   No Auto Email Reports found")
        
        # Check for ERPNext notifications
        notifications = frappe.get_all("Notification", 
                                     filters={"document_type": "HD Ticket"},
                                     fields=["name", "subject", "enabled"])
        if notifications:
            print(f"   Found {len(notifications)} ERPNext Notifications for HD Ticket:")
            for notif in notifications:
                print(f"      - {notif.name}: {notif.subject} (Enabled: {notif.enabled})")
        else:
            print(f"   No ERPNext Notifications for HD Ticket found")
        
        # Check for any email templates that might be auto-triggered
        print(f"\n🔍 Checking HD Ticket DocType for auto email settings...")
        
        # Get HD Ticket meta to check for any auto email configurations
        hd_ticket_meta = frappe.get_meta("HD Ticket")
        
        # Check if there are any print formats or email templates linked
        print(f"   HD Ticket has {len(hd_ticket_meta.fields)} fields")
        
        # Look for any communication or email-related customizations
        customizations = frappe.get_all("Property Setter", 
                                       filters={"doc_type": "HD Ticket"},
                                       fields=["property", "value"])
        
        if customizations:
            print(f"   Found {len(customizations)} HD Ticket customizations")
            for custom in customizations[:5]:  # Show first 5
                print(f"      - {custom.property}: {custom.value}")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Try creating a ticket now - should not show template error")
        print(f"   2. If error still shows, it's coming from ERPNext default notifications")
        print(f"   3. If no error, we can re-enable with fixed configuration")
        
        print(f"\n⚠️  Notifications temporarily disabled for testing")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()