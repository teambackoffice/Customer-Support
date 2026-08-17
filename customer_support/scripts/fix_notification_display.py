import frappe

def execute():
    """Fix notification rules and show how to access recipients properly"""
    print("🔧 Fixing Notification Rules Display...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📋 Current rules: {len(settings.notification_rules) if settings.notification_rules else 0}")
        
        if settings.notification_rules:
            for i, rule in enumerate(settings.notification_rules):
                print(f"   Rule {i+1}: {rule.notification_type} - {len(rule.recipients) if hasattr(rule, 'recipients') and rule.recipients else 0} recipients")
        
        # Clean up - keep only one New Ticket rule with recipients
        if settings.notification_rules and len(settings.notification_rules) > 1:
            print("🧹 Cleaning up duplicate rules...")
            
            # Find the rule with recipients
            rule_with_recipients = None
            for rule in settings.notification_rules:
                if hasattr(rule, 'recipients') and rule.recipients:
                    rule_with_recipients = rule
                    break
            
            # Clear all rules and add back the one with recipients
            settings.notification_rules = []
            
            if rule_with_recipients:
                settings.append("notification_rules", rule_with_recipients)
                print("✅ Kept rule with recipients")
            else:
                # Create a new rule with recipients
                new_rule = settings.append("notification_rules", {})
                new_rule.enabled = 1
                new_rule.notification_type = "New Ticket"
                new_rule.trigger_event = "After Insert"
                new_rule.delay_minutes = 0
                new_rule.email_template = "HD Ticket - New Ticket"
                new_rule.subject = "New Ticket: {{ doc.name }}"
                
                # Add recipients
                recipient1 = new_rule.append("recipients", {})
                recipient1.receiver_by = "Document Field"
                recipient1.receiver_type = "To"
                recipient1.field_name = "raised_by"
                
                recipient2 = new_rule.append("recipients", {})
                recipient2.receiver_by = "Email"
                recipient2.receiver_type = "CC"
                recipient2.email_by_document_field = "support@tboindia.com"
                
                print("✅ Created new rule with recipients")
            
            settings.save(ignore_permissions=True)
            frappe.db.commit()
        
        # Show final status
        print(f"\n📊 Final Configuration:")
        if settings.notification_rules:
            rule = settings.notification_rules[0]
            print(f"   Rule: {rule.notification_type}")
            print(f"   Enabled: {rule.enabled}")
            print(f"   Template: {rule.email_template}")
            
            if hasattr(rule, 'recipients') and rule.recipients:
                print(f"   Recipients ({len(rule.recipients)}):")
                for i, recipient in enumerate(rule.recipients, 1):
                    print(f"      {i}. {recipient.receiver_type}: {recipient.receiver_by}", end="")
                    if recipient.receiver_by == "Document Field":
                        print(f" → {recipient.field_name}")
                    elif recipient.receiver_by == "Role":
                        print(f" → {recipient.email_by_role}")
                    elif recipient.receiver_by == "Email":
                        print(f" → {recipient.email_by_document_field}")
            else:
                print(f"   ⚠️  No recipients configured")
        
        print(f"\n📋 How to Access Recipients in UI:")
        print(f"   1. Look at the Notification Rules table")
        print(f"   2. Click on the row number (1) OR click on 'New Ticket' text")
        print(f"   3. The row will expand to show details")
        print(f"   4. Scroll down in the expanded area to see 'Recipients' section")
        print(f"   5. Recipients will be shown as a child table")
        
        print(f"\n💡 Note: Recipients cannot be shown as a column because")
        print(f"   it's a child table. You must expand the row to see them.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()