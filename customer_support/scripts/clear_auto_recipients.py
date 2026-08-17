#!/usr/bin/env python3

"""
Clear automatic recipients and allow manual recipient selection
"""

import frappe


def clear_automatic_recipients():
    """Remove all automatic recipients so user can choose manually"""
    
    print("🧹 CLEARING AUTOMATIC RECIPIENTS")
    print("=" * 40)
    
    try:
        # Get all notification recipients that belong to our notification rules
        settings = frappe.get_single("Customer Support Notification Settings")
        
        rule_names = [rule.name for rule in settings.notification_rules]
        
        # Delete existing recipients
        existing_recipients = frappe.get_all("Notification Recipient", 
            filters={"parent": ["in", rule_names]},
            pluck="name"
        )
        
        print(f"🗑️  Found {len(existing_recipients)} automatic recipients to remove")
        
        for recipient_name in existing_recipients:
            frappe.delete_doc("Notification Recipient", recipient_name, ignore_permissions=True)
            print(f"   Deleted: {recipient_name}")
        
        frappe.db.commit()
        
        print("✅ All automatic recipients cleared!")
        print("\n💡 Now you can manually add recipients in the UI:")
        print("   1. Go to: Customer Support Notification Settings")
        print("   2. Click on each notification rule")
        print("   3. Add recipients manually as needed")
        print("   4. Choose To/CC/BCC and recipient types")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to clear recipients: {str(e)}")
        return False


def update_notification_settings():
    """Update settings to remove company requirement"""
    
    print("\n🔧 UPDATING NOTIFICATION SETTINGS")
    print("=" * 40)
    
    try:
        # Reload the DocType to pick up changes
        frappe.reload_doctype("Customer Support Notification Settings")
        
        # Get settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        # Clear company if needed (now optional)
        if not settings.company:
            settings.company = ""
        
        # Save without company validation
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("✅ Settings updated - Company is now optional")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update settings: {str(e)}")
        return False


def show_current_rules():
    """Show current notification rules without recipients"""
    
    print("\n📋 CURRENT NOTIFICATION RULES")
    print("=" * 35)
    
    try:
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📧 Notifications enabled: {settings.enable_notifications}")
        print(f"🏢 Company: {settings.company or '(Optional - not set)'}")
        print(f"📬 Default email: {settings.default_from_email}")
        
        print(f"\n📋 Rules ({len(settings.notification_rules)}):")
        
        for i, rule in enumerate(settings.notification_rules, 1):
            print(f"\n   {i}. {rule.notification_type}")
            print(f"      Trigger: {rule.trigger_event}")
            print(f"      Enabled: {rule.enabled}")
            print(f"      Template: {rule.email_template}")
            
            if rule.delay_minutes:
                print(f"      Delay: {rule.delay_minutes} minutes")
            
            # Count recipients
            recipient_count = frappe.db.count("Notification Recipient", 
                filters={"parent": rule.name})
            
            print(f"      Recipients: {recipient_count} (manually configured)")
        
        print(f"\n💡 To add recipients:")
        print(f"   • Go to Customer Support Notification Settings")
        print(f"   • Click on each rule to add recipients")
        print(f"   • Choose who should receive emails for each notification type")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to show rules: {str(e)}")
        return False


def create_example_recipients():
    """Create example recipient configurations (optional)"""
    
    print("\n🎯 EXAMPLE RECIPIENT SETUP")
    print("=" * 30)
    
    print("Here are some example recipient configurations you can set up:")
    
    print("\n📧 New Ticket notifications:")
    print("   To: Custom Email → support@teambackoffice.com")
    print("   CC: Customer (if you want customer to get copy)")
    
    print("\n⏰ Escalation notifications:")  
    print("   To: Custom Email → manager@teambackoffice.com")
    print("   CC: Custom Email → support@teambackoffice.com")
    
    print("\n✅ Resolved notifications:")
    print("   To: Customer")
    print("   CC: Custom Email → support@teambackoffice.com")
    
    print("\n💡 Available recipient types:")
    print("   • Customer - Gets ticket contact email")
    print("   • Assigned Agent - Gets assigned user email") 
    print("   • Ticket Owner - Gets ticket creator email")
    print("   • Support Team - Gets all users with Support Team role")
    print("   • Custom Email - Enter specific email addresses")
    
    return True


def main():
    """Main function to clear recipients and update settings"""
    
    print("🚀 CUSTOMIZING NOTIFICATION RECIPIENT SELECTION")
    print("=" * 55)
    
    # Step 1: Clear automatic recipients
    if clear_automatic_recipients():
        print("\n✅ Step 1: Automatic recipients cleared")
    else:
        print("\n❌ Step 1: Failed to clear recipients")
        return
    
    # Step 2: Update settings 
    if update_notification_settings():
        print("✅ Step 2: Settings updated (Company optional)")
    else:
        print("❌ Step 2: Failed to update settings")
    
    # Step 3: Show current state
    if show_current_rules():
        print("\n✅ Step 3: Current rules displayed")
    
    # Step 4: Show examples
    create_example_recipients()
    
    print(f"\n🎉 CUSTOMIZATION COMPLETE!")
    print(f"=" * 30)
    print(f"✅ Company field is now optional")
    print(f"✅ No automatic recipients - you choose who gets emails")
    print(f"✅ All notification rules preserved")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Go to: Customer Support Notification Settings")
    print(f"   2. Add recipients manually for each rule")
    print(f"   3. Choose To/CC/BCC as needed") 
    print(f"   4. Test with a real HD Ticket")


if __name__ == "__main__":
    main()