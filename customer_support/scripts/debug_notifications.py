#!/usr/bin/env python3

"""
Debug notification system
"""

import frappe
from customer_support.customer_support.notification_system import NotificationSystem


def debug_notification_system():
    """Debug the notification system"""
    
    print("🔍 Debugging Customer Support Notification System...")
    
    # Test 1: Check notification settings
    print("\n1. Testing notification settings...")
    settings = NotificationSystem.get_notification_settings()
    
    if settings:
        print(f"✅ Settings found: Enabled = {settings.enable_notifications}")
        print(f"📧 Company: {settings.company}")
        print(f"📬 Default email: {settings.default_from_email}")
        print(f"📋 Rules count: {len(settings.notification_rules)}")
        
        # Check each rule
        for i, rule in enumerate(settings.notification_rules, 1):
            print(f"\n   Rule {i}: {rule.notification_type}")
            print(f"   - Enabled: {rule.enabled}")
            print(f"   - Trigger: {rule.trigger_event}")
            print(f"   - Template: {rule.email_template}")
            print(f"   - Recipients: {len(rule.recipients)}")
            
            # Check recipients
            for j, recipient in enumerate(rule.recipients, 1):
                print(f"     Recipient {j}: {recipient.recipient_role} - {recipient.recipient_type}")
    else:
        print("❌ No notification settings found")
        return
    
    # Test 2: Check escalation rule specifically
    print("\n2. Testing escalation rule...")
    escalation_rule = NotificationSystem.get_notification_rule("Escalation", "Status Change")
    
    if escalation_rule:
        print(f"✅ Escalation rule found: Enabled = {escalation_rule.enabled}")
        print(f"📧 Template: {escalation_rule.email_template}")
        print(f"📋 Recipients: {len(escalation_rule.recipients)}")
    else:
        print("❌ No escalation rule found")
    
    # Test 3: Check email templates
    print("\n3. Testing email templates...")
    templates = ["HD Ticket - New Ticket", "HD Ticket - Escalation", "HD Ticket - Resolved"]
    
    for template_name in templates:
        if frappe.db.exists("Email Template", template_name):
            print(f"✅ Template exists: {template_name}")
        else:
            print(f"❌ Template missing: {template_name}")
    
    # Test 4: Check recent tickets
    print("\n4. Checking recent tickets...")
    recent_tickets = frappe.get_all("HD Ticket", 
        filters={"creation": [">", "2026-08-04 00:00:00"]},
        fields=["name", "status", "escalation_sent", "escalated_at"],
        order_by="creation desc",
        limit=5
    )
    
    for ticket in recent_tickets:
        print(f"   Ticket: {ticket.name} | Status: {ticket.status} | Escalated: {ticket.escalation_sent}")
        if ticket.escalated_at:
            print(f"     Escalated at: {ticket.escalated_at}")


def test_manual_escalation():
    """Test escalation manually"""
    
    print("\n🧪 Testing Manual Escalation...")
    
    # Create a test ticket
    ticket = frappe.new_doc("HD Ticket")
    ticket.subject = "Manual Escalation Test"
    ticket.description = "Testing manual escalation notification"
    ticket.contact_email = "test@example.com"
    ticket.status = "Open"
    ticket.escalation_sent = 0
    
    ticket.insert(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"✅ Created ticket: {ticket.name}")
    
    # Manually trigger escalation
    try:
        from customer_support.customer_support.scheduler import handle_status_escalation
        
        # Change status to Replied
        ticket.status = "Replied"
        
        # Call escalation handler directly
        handle_status_escalation(ticket)
        
        # Reload ticket to see changes
        ticket.reload()
        
        if ticket.escalation_sent:
            print(f"✅ Escalation triggered: {ticket.escalated_at}")
        else:
            print("❌ Escalation not triggered")
            
    except Exception as e:
        print(f"❌ Error during manual escalation: {str(e)}")


def check_email_queue():
    """Check email queue for recent emails"""
    
    print("\n📧 Checking Email Queue...")
    
    recent_emails = frappe.get_all("Email Queue",
        filters={"creation": [">", "2026-08-04 00:00:00"]},
        fields=["name", "status", "recipient", "subject", "creation"],
        order_by="creation desc",
        limit=10
    )
    
    if recent_emails:
        print(f"Found {len(recent_emails)} recent emails:")
        for email in recent_emails:
            print(f"   {email.creation} | {email.status} | To: {email.recipient}")
            print(f"   Subject: {email.subject}")
    else:
        print("No recent emails found in queue")


def main():
    """Main debug function"""
    debug_notification_system()
    test_manual_escalation()
    check_email_queue()


if __name__ == "__main__":
    main()