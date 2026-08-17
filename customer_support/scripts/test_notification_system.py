#!/usr/bin/env python3

"""
Customer Support Notification System Test Script

This script helps test the notification system functionality.

Usage:
    bench execute customer_support.scripts.test_notification_system.run_tests
"""

import frappe
from frappe.utils import now_datetime
from customer_support.customer_support.notification_system import NotificationSystem


def create_test_ticket():
    """Create a test ticket for notification testing"""
    
    # Create test ticket
    ticket = frappe.new_doc("HD Ticket")
    ticket.subject = f"Test Notification System - {now_datetime().strftime('%Y%m%d%H%M%S')}"
    ticket.description = "This is a test ticket to verify the notification system is working correctly."
    ticket.contact_email = "test.customer@example.com"
    ticket.status = "Open"
    
    # Set a test user as assigned if available
    test_users = frappe.get_all("User", 
        filters={"enabled": 1, "user_type": "System User"}, 
        limit=1, pluck="name"
    )
    if test_users:
        ticket.custom_assigned_to = test_users[0]
    
    ticket.insert(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"✅ Created test ticket: {ticket.name}")
    return ticket


def test_new_ticket_notification():
    """Test new ticket notification"""
    print("\n🧪 Testing New Ticket Notification...")
    
    # Create test ticket (this should trigger new ticket notification)
    ticket = create_test_ticket()
    
    # Check if notification was attempted
    # Note: We can't easily test actual email sending without SMTP config
    print(f"📧 New ticket notification should have been triggered for: {ticket.name}")
    
    return ticket


def test_escalation_notification():
    """Test escalation notification logic"""
    print("\n🧪 Testing Escalation Notification Logic...")
    
    # Create a test ticket
    ticket = frappe.new_doc("HD Ticket")
    ticket.subject = f"Test Escalation - {now_datetime().strftime('%Y%m%d%H%M%S')}"
    ticket.description = "Testing escalation notification on status change"
    ticket.contact_email = "test.escalation@example.com"
    ticket.status = "Open"
    ticket.escalation_sent = 0
    
    ticket.insert(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"✅ Created test ticket: {ticket.name} with status: {ticket.status}")
    
    # Change status from Open to Replied (this should trigger escalation)
    ticket.status = "Replied"
    ticket.save(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"📝 Changed ticket status to: {ticket.status}")
    
    # Check if ticket was escalated
    ticket.reload()
    if ticket.escalation_sent:
        print(f"✅ Escalation notification sent for: {ticket.name}")
        print(f"⏰ Escalated at: {ticket.escalated_at}")
    else:
        print(f"❌ Escalation notification was not sent for: {ticket.name}")
    
    # Test resetting escalation when status goes back to Open
    print("\n🔄 Testing escalation reset...")
    ticket.status = "Open"
    ticket.save(ignore_permissions=True)
    frappe.db.commit()
    
    ticket.reload()
    if not ticket.escalation_sent:
        print(f"✅ Escalation flag reset when ticket returned to Open status")
    else:
        print(f"❌ Escalation flag was not reset")
    
    return ticket


def test_resolved_notification():
    """Test resolved notification"""
    print("\n🧪 Testing Resolved Notification...")
    
    # Create and resolve a ticket
    ticket = create_test_ticket()
    
    # Update status to resolved (this should trigger resolved notification)
    ticket.status = "Resolved"
    ticket.save(ignore_permissions=True)
    frappe.db.commit()
    
    print(f"✅ Ticket {ticket.name} marked as resolved")
    print(f"📧 Resolved notification should have been triggered")
    
    return ticket


def test_notification_settings():
    """Test notification settings retrieval"""
    print("\n🧪 Testing Notification Settings...")
    
    # Check if settings exist (Single DocType)
    settings = NotificationSystem.get_notification_settings()
    
    if settings:
        print(f"✅ Notification settings found")
        print(f"📧 Notifications enabled: {settings.enable_notifications}")
        print(f"🏢 Company: {settings.company}")
        print(f"📬 Default from email: {settings.default_from_email}")
        print(f"📋 Number of notification rules: {len(settings.notification_rules)}")
        
        # List notification rules
        for i, rule in enumerate(settings.notification_rules, 1):
            print(f"   {i}. {rule.notification_type} - {rule.trigger_event} (Enabled: {rule.enabled})")
    else:
        print(f"❌ No notification settings found")
        print("💡 Run setup script to create default settings")
    
    return settings


def test_email_templates():
    """Test email template availability"""
    print("\n🧪 Testing Email Templates...")
    
    templates = [
        "HD Ticket - New Ticket",
        "HD Ticket - Escalation", 
        "HD Ticket - Resolved"
    ]
    
    for template_name in templates:
        if frappe.db.exists("Email Template", template_name):
            print(f"✅ Email template exists: {template_name}")
        else:
            print(f"❌ Email template missing: {template_name}")


def test_recipient_resolution():
    """Test recipient email resolution"""
    print("\n🧪 Testing Recipient Resolution...")
    
    # Create a test ticket
    ticket = create_test_ticket()
    
    # Test different recipient types
    test_recipients = [
        {"recipient_role": "To", "recipient_type": "Customer"},
        {"recipient_role": "CC", "recipient_type": "Support Team"},
        {"recipient_role": "BCC", "recipient_type": "Custom Email", "custom_email": "admin@test.com"}
    ]
    
    for recipient_data in test_recipients:
        # Create a mock recipient object
        recipient = frappe._dict(recipient_data)
        
        emails = NotificationSystem.resolve_recipient_emails(recipient, ticket)
        
        print(f"📧 {recipient.recipient_type}: {emails if emails else 'No emails found'}")
    
    return ticket


def cleanup_test_tickets():
    """Clean up test tickets created during testing"""
    print("\n🧹 Cleaning up test tickets...")
    
    # Find test tickets
    test_tickets = frappe.get_all("HD Ticket",
        filters={"subject": ["like", "%Test Notification System%"]},
        pluck="name"
    )
    
    test_escalation_tickets = frappe.get_all("HD Ticket",
        filters={"subject": ["like", "%Test Escalation%"]},
        pluck="name"
    )
    
    all_test_tickets = list(set(test_tickets + test_escalation_tickets))
    
    for ticket_name in all_test_tickets:
        try:
            frappe.delete_doc("HD Ticket", ticket_name, ignore_permissions=True)
            print(f"🗑️  Deleted test ticket: {ticket_name}")
        except Exception as e:
            print(f"⚠️  Could not delete {ticket_name}: {str(e)}")
    
    if all_test_tickets:
        frappe.db.commit()
        print(f"✅ Cleaned up {len(all_test_tickets)} test tickets")
    else:
        print("✅ No test tickets found to clean up")


def run_tests():
    """Run all notification system tests"""
    print("🚀 Starting Customer Support Notification System Tests")
    print("=" * 60)
    
    try:
        # Test 1: Check settings and templates
        test_notification_settings()
        test_email_templates()
        
        # Test 2: Test notification triggers
        test_new_ticket_notification()
        test_resolved_notification() 
        test_escalation_notification()
        
        # Test 3: Test recipient resolution
        test_recipient_resolution()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        
        # Ask if user wants to clean up test data
        print("\n🧹 Test tickets have been created. Run cleanup if needed:")
        print("   bench execute customer_support.scripts.test_notification_system.cleanup_test_tickets")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        frappe.log_error(f"Notification system test failed: {str(e)}", "Test Error")


if __name__ == "__main__":
    run_tests()