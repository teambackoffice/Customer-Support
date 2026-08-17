import frappe

def execute():
    """Create simple checkbox-based notification system"""
    print("🔄 Creating Simple Checkbox-Based Notification System...")
    
    try:
        # Reload the updated DocType
        frappe.reload_doc("customer_support", "doctype", "support_notification_rule", force=True)
        frappe.clear_cache()
        print("✅ Support Notification Rule DocType updated")
        
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        # Clear existing rules
        settings.notification_rules = []
        
        # Create New Ticket notification with simple checkboxes
        new_ticket_rule = settings.append("notification_rules", {})
        new_ticket_rule.enabled = 1
        new_ticket_rule.notification_type = "New Ticket"
        new_ticket_rule.trigger_event = "After Insert"
        new_ticket_rule.delay_minutes = 0
        new_ticket_rule.email_template = "HD Ticket - New Ticket"
        new_ticket_rule.subject = "New Support Ticket: {{ doc.name }}"
        
        # Set simple checkbox recipients
        new_ticket_rule.send_to_customer = 1  # Send to customer who raised ticket
        new_ticket_rule.send_to_assigned_agent = 1  # CC assigned agent
        new_ticket_rule.cc_support_team = 1  # BCC support team
        new_ticket_rule.bcc_custom_emails = 1  # Custom emails
        new_ticket_rule.custom_emails = "support@tboindia.com, admin@tboindia.com"
        
        # Create Escalation notification
        escalation_rule = settings.append("notification_rules", {})
        escalation_rule.enabled = 1
        escalation_rule.notification_type = "Escalation"
        escalation_rule.trigger_event = "Scheduler"
        escalation_rule.delay_minutes = 15
        escalation_rule.email_template = "HD Ticket - Escalation"
        escalation_rule.subject = "⚠️ ESCALATION: {{ doc.name }} - No response in 15 minutes"
        
        # Set escalation recipients
        escalation_rule.send_to_assigned_agent = 1  # Notify assigned agent
        escalation_rule.cc_support_team = 1  # Escalate to support team
        escalation_rule.bcc_custom_emails = 1
        escalation_rule.custom_emails = "manager@tboindia.com"
        
        # Create Resolved notification
        resolved_rule = settings.append("notification_rules", {})
        resolved_rule.enabled = 1
        resolved_rule.notification_type = "Resolved"
        resolved_rule.trigger_event = "Status Change"
        resolved_rule.delay_minutes = 0
        resolved_rule.email_template = "HD Ticket - Resolved"
        resolved_rule.subject = "✅ Ticket Resolved: {{ doc.name }}"
        
        # Set resolved recipients
        resolved_rule.send_to_customer = 1  # Notify customer
        resolved_rule.send_to_assigned_agent = 1  # CC agent
        
        # Save settings
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ Created {len(settings.notification_rules)} notification rules:")
        
        for i, rule in enumerate(settings.notification_rules, 1):
            print(f"\n   Rule {i}: {rule.notification_type}")
            print(f"      Trigger: {rule.trigger_event}")
            print(f"      Template: {rule.email_template}")
            
            # Show recipients
            recipients = []
            if getattr(rule, 'send_to_customer', 0):
                recipients.append("Customer")
            if getattr(rule, 'send_to_assigned_agent', 0):
                recipients.append("Assigned Agent")
            if getattr(rule, 'send_to_owner', 0):
                recipients.append("Owner")
            if getattr(rule, 'cc_support_team', 0):
                recipients.append("Support Team")
            if getattr(rule, 'bcc_custom_emails', 0):
                recipients.append(f"Custom: {getattr(rule, 'custom_emails', '')}")
                
            print(f"      Recipients: {', '.join(recipients) if recipients else 'None'}")
        
        print(f"\n🎯 Now you can:")
        print(f"   1. Refresh the Customer Support Notification Settings page")
        print(f"   2. Click the pencil icon to edit any rule")
        print(f"   3. You'll see simple checkboxes for recipients:")
        print(f"      ☑️ Send to Customer")
        print(f"      ☑️ Send to Assigned Agent") 
        print(f"      ☑️ Send to Ticket Owner")
        print(f"      ☑️ CC Support Team")
        print(f"      ☑️ Send to Custom Emails")
        print(f"   4. No complex tables - just simple checkboxes!")
        
        print(f"\n✅ Simple checkbox notification system is ready!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()