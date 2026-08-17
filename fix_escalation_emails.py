#!/usr/bin/env python3
"""
Escalation Email Fix Script
This script will identify and fix common issues preventing escalation emails

Usage:
    bench --site [site-name] console
    >>> exec(open('fix_escalation_emails.py').read())
"""

import frappe
from frappe.utils import now_datetime

def fix_escalation_email_system():
    """Complete fix for escalation email system"""
    
    print("\n" + "🔧"*50)
    print("FIXING ESCALATION EMAIL SYSTEM")
    print("🔧"*50 + "\n")
    
    fixed_items = []
    
    # Fix 1: Ensure escalation fields exist
    print("1️⃣ Checking escalation fields...")
    try:
        meta = frappe.get_meta("HD Ticket")
        if not meta.get_field("escalation_sent") or not meta.get_field("escalated_at"):
            print("   Creating escalation fields...")
            
            # Create escalation fields
            from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
            
            custom_fields = {
                "HD Ticket": [
                    {
                        "fieldname": "escalation_sent",
                        "fieldtype": "Check",
                        "label": "Escalation Sent",
                        "default": "0",
                        "read_only": 1,
                        "insert_after": "status",
                        "description": "Indicates if escalation notification has been sent"
                    },
                    {
                        "fieldname": "escalated_at", 
                        "fieldtype": "Datetime",
                        "label": "Escalated At",
                        "read_only": 1,
                        "insert_after": "escalation_sent",
                        "description": "When escalation notification was sent"
                    }
                ]
            }
            
            create_custom_fields(custom_fields, update=True)
            fixed_items.append("Created escalation fields")
            print("   ✅ Escalation fields created")
        else:
            print("   ✅ Escalation fields already exist")
    except Exception as e:
        print(f"   ❌ Error creating fields: {e}")
    
    # Fix 2: Create/fix notification settings
    print("\n2️⃣ Fixing notification settings...")
    try:
        if not frappe.db.exists("Customer Support Notification Settings", "Customer Support Notification Settings"):
            print("   Creating notification settings...")
            
            settings = frappe.new_doc("Customer Support Notification Settings")
            settings.enable_notifications = 1
            settings.company = frappe.defaults.get_user_default("Company") or "TBO TEAM BACK OFFICE INTERNATIONAL LLP"
            settings.default_from_email = "support@teambackoffice.com"  # Update this
            settings.reply_to = "support@teambackoffice.com"  # Update this
            settings.insert(ignore_permissions=True)
            
            fixed_items.append("Created notification settings")
            print("   ✅ Created notification settings")
        else:
            settings = frappe.get_single("Customer Support Notification Settings")
            if not settings.enable_notifications:
                settings.enable_notifications = 1
                settings.save(ignore_permissions=True)
                fixed_items.append("Enabled notifications")
                print("   ✅ Enabled notifications")
            else:
                print("   ✅ Notification settings exist and enabled")
    except Exception as e:
        print(f"   ❌ Error with settings: {e}")
    
    # Fix 3: Create/fix escalation rule
    print("\n3️⃣ Fixing escalation rule...")
    try:
        settings = frappe.get_single("Customer Support Notification Settings")
        
        # Check if escalation rule exists
        escalation_rule_exists = False
        for rule in settings.notification_rules:
            if rule.notification_type == "Escalation" and rule.trigger_event == "Scheduler":
                escalation_rule_exists = True
                if not rule.enabled:
                    rule.enabled = 1
                    settings.save(ignore_permissions=True)
                    fixed_items.append("Enabled escalation rule")
                    print("   ✅ Enabled existing escalation rule")
                else:
                    print("   ✅ Escalation rule exists and enabled")
                break
        
        if not escalation_rule_exists:
            print("   Creating escalation rule...")
            settings.append("notification_rules", {
                "enabled": 1,
                "notification_type": "Escalation",
                "trigger_event": "Scheduler", 
                "delay_minutes": 15,
                "email_template": "HD Ticket - Escalation",
                "subject": "🚨 ESCALATION: Ticket {{ doc.name }} needs attention",
                "send_to_customer": 0,
                "send_to_assigned_agent": 1,
                "send_to_owner": 0,
                "cc_support_team": 1,
                "bcc_custom_emails": 1,
                "custom_emails": "nahala@teambackoffice.com"  # Update this
            })
            settings.save(ignore_permissions=True)
            fixed_items.append("Created escalation rule")
            print("   ✅ Created escalation rule")
    except Exception as e:
        print(f"   ❌ Error with escalation rule: {e}")
    
    # Fix 4: Create/fix email template
    print("\n4️⃣ Fixing email template...")
    try:
        if not frappe.db.exists("Email Template", "HD Ticket - Escalation"):
            print("   Creating email template...")
            
            template = frappe.new_doc("Email Template")
            template.name = "HD Ticket - Escalation"
            template.subject = "🚨 ESCALATION ALERT: Ticket {{ doc.name }} - {{ doc.subject }}"
            template.response = """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f8f9fa; padding: 20px;">
    <div style="background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        
        <!-- Header -->
        <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 25px;">
            <h1 style="margin: 0; font-size: 24px;">🚨 TICKET ESCALATION ALERT</h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                Immediate attention required for ticket {{ doc.name }}
            </p>
        </div>
        
        <!-- Ticket Details -->
        <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 20px; margin-bottom: 25px;">
            <h3 style="color: #856404; margin: 0 0 15px 0;">📋 Ticket Information</h3>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #495057; width: 30%;">Ticket ID:</td>
                    <td style="padding: 8px 0; color: #212529;">{{ doc.name }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #495057;">Subject:</td>
                    <td style="padding: 8px 0; color: #212529;">{{ doc.subject }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #495057;">Status:</td>
                    <td style="padding: 8px 0;">
                        <span style="background-color: #dc3545; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                            {{ doc.status }}
                        </span>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #495057;">Priority:</td>
                    <td style="padding: 8px 0; color: #212529;">{{ doc.priority or "Medium" }}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #495057;">Created:</td>
                    <td style="padding: 8px 0; color: #212529;">{{ frappe.utils.format_datetime(doc.creation, "dd MMM yyyy, hh:mm a") }}</td>
                </tr>
                {% if doc.custom_assigned_to %}
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #495057;">Assigned To:</td>
                    <td style="padding: 8px 0; color: #212529;">{{ doc.custom_assigned_to }}</td>
                </tr>
                {% endif %}
                {% if doc.custom_customer %}
                <tr>
                    <td style="padding: 8px 0; font-weight: bold; color: #495057;">Customer:</td>
                    <td style="padding: 8px 0; color: #212529;">{{ doc.custom_customer }}</td>
                </tr>
                {% endif %}
            </table>
        </div>
        
        <!-- Description -->
        {% if doc.description %}
        <div style="margin-bottom: 25px;">
            <h4 style="color: #495057; margin-bottom: 10px;">📝 Description</h4>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6;">
                {{ doc.description }}
            </div>
        </div>
        {% endif %}
        
        <!-- Escalation Warning -->
        <div style="background-color: #f8d7da; border: 2px solid #dc3545; padding: 20px; border-radius: 8px; text-align: center;">
            <h3 style="color: #721c24; margin: 0 0 10px 0;">⚠️ ESCALATION REASON</h3>
            <p style="color: #721c24; margin: 0; font-size: 16px; line-height: 1.5;">
                This ticket has been <strong>open for more than 15 minutes</strong> without any agent response.<br>
                <strong>Immediate action is required!</strong>
            </p>
        </div>
        
        <!-- Action Button -->
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{ frappe.utils.get_url() }}/app/hd-ticket/{{ doc.name }}" 
               style="background-color: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; display: inline-block;">
                🎫 VIEW TICKET NOW
            </a>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; font-size: 14px;">
            <p style="margin: 0;">
                This escalation was automatically generated by the Customer Support System<br>
                Generated at: {{ frappe.utils.format_datetime(frappe.utils.now_datetime(), "dd MMM yyyy, hh:mm a") }}
            </p>
        </div>
        
    </div>
</div>
"""
            template.use_html = 1
            template.insert(ignore_permissions=True)
            fixed_items.append("Created email template")
            print("   ✅ Created email template")
        else:
            print("   ✅ Email template already exists")
    except Exception as e:
        print(f"   ❌ Error with email template: {e}")
    
    # Fix 5: Check email account
    print("\n5️⃣ Checking email accounts...")
    try:
        outgoing_accounts = frappe.get_all("Email Account", 
            filters={"enable_outgoing": 1}, 
            fields=["email_id", "default_outgoing"]
        )
        
        if outgoing_accounts:
            print(f"   ✅ Found {len(outgoing_accounts)} outgoing email account(s)")
            for acc in outgoing_accounts:
                print(f"      📧 {acc.email_id} (default: {acc.default_outgoing})")
        else:
            print("   ❌ No outgoing email accounts found")
            print("   ⚠️  You need to configure an Email Account with 'Enable Outgoing' checked")
    except Exception as e:
        print(f"   ❌ Error checking email accounts: {e}")
    
    # Fix 6: Test scheduler function
    print("\n6️⃣ Testing scheduler function...")
    try:
        from customer_support.customer_support.scheduler import check_escalation_notifications
        print("   ✅ Scheduler function is accessible")
        
        # Check scheduler status
        scheduler_enabled = frappe.utils.cint(frappe.db.get_single_value("System Settings", "enable_scheduler"))
        if scheduler_enabled:
            print("   ✅ Scheduler is enabled globally")
        else:
            print("   ❌ Scheduler is disabled - Enable in System Settings")
    except Exception as e:
        print(f"   ❌ Error with scheduler: {e}")
    
    # Summary
    print("\n" + "✅"*50)
    print("FIX SUMMARY")
    print("✅"*50)
    
    if fixed_items:
        print("🔧 ITEMS FIXED:")
        for i, item in enumerate(fixed_items, 1):
            print(f"   {i}. {item}")
    else:
        print("✨ No fixes needed - system was already configured!")
    
    print(f"\n🧪 TESTING STEPS:")
    print("1. Create a new HD Ticket (status: Open)")
    print("2. Wait 16+ minutes without agent response")  
    print("3. Check Email Queue for escalation emails")
    print("4. Or run manual test: force_test_escalation()")
    
    print(f"\n📊 MONITORING:")
    print("- Check Error Log for escalation errors")
    print("- Monitor Email Queue for failed sends")
    print("- Verify escalation_sent field updates on tickets")
    
    frappe.db.commit()
    print(f"\n🎉 ESCALATION FIX COMPLETE!")


def force_test_escalation():
    """Force test an escalation email"""
    print("\n🧪 FORCE TESTING ESCALATION...")
    
    try:
        # Find or create test ticket
        test_tickets = frappe.get_all("HD Ticket", 
            filters={"status": "Open", "escalation_sent": 0},
            limit=1
        )
        
        if test_tickets:
            ticket = frappe.get_doc("HD Ticket", test_tickets[0].name)
            print(f"   Using existing ticket: {ticket.name}")
        else:
            # Create test ticket
            ticket = frappe.new_doc("HD Ticket") 
            ticket.subject = "TEST: Escalation Email Test"
            ticket.description = "This is a test ticket to verify escalation emails work"
            ticket.status = "Open"
            ticket.priority = "High"
            ticket.raised_by = frappe.session.user
            ticket.insert(ignore_permissions=True)
            print(f"   Created test ticket: {ticket.name}")
        
        # Send escalation
        from customer_support.customer_support.notification_system import NotificationSystem
        
        result = NotificationSystem.send_notification(ticket, "Escalation", "Scheduler")
        
        if result:
            # Mark as escalated
            frappe.db.set_value("HD Ticket", ticket.name, {
                "escalation_sent": 1, 
                "escalated_at": frappe.utils.now_datetime()
            })
            frappe.db.commit()
            
            print("   ✅ Test escalation sent successfully!")
            print(f"   📧 Check Email Queue for escalation email")
            print(f"   🎫 Test ticket: {ticket.name}")
        else:
            print("   ❌ Test escalation failed - check Error Log")
            
    except Exception as e:
        print(f"   ❌ Test failed: {str(e)}")


def check_email_queue_status():
    """Check recent email queue for escalation emails"""
    print("\n📬 CHECKING EMAIL QUEUE...")
    
    try:
        from frappe.utils import add_to_date
        
        recent_emails = frappe.get_all("Email Queue",
            filters={
                "creation": [">", add_to_date(frappe.utils.now_datetime(), hours=-24)]
            },
            fields=["name", "subject", "status", "error", "creation", "recipients"],
            order_by="creation desc",
            limit=10
        )
        
        print(f"   📊 Found {len(recent_emails)} emails in last 24 hours")
        
        escalation_emails = []
        for email in recent_emails:
            if "escalation" in email.subject.lower() or "🚨" in email.subject:
                escalation_emails.append(email)
        
        print(f"   🚨 Found {len(escalation_emails)} escalation emails")
        
        if escalation_emails:
            for email in escalation_emails:
                status_icon = "✅" if email.status == "Sent" else "❌" if email.status == "Error" else "⏳"
                print(f"      {status_icon} {email.subject[:50]}... | {email.status} | {email.creation}")
                if email.error:
                    print(f"         Error: {email.error}")
        else:
            print("   ℹ️  No escalation emails found in queue")
            
    except Exception as e:
        print(f"   ❌ Error checking queue: {e}")


if __name__ == "__main__":
    fix_escalation_email_system()
    print(f"\n" + "-"*60)
    print("Available functions:")
    print("- force_test_escalation() - Send test escalation")
    print("- check_email_queue_status() - Check email queue")
    print("-"*60)