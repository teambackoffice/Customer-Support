#!/usr/bin/env python3
"""
Complete Escalation System Test & Fix Script

This script will:
1. Diagnose current escalation system issues
2. Apply all necessary fixes
3. Test the escalation system
4. Provide detailed feedback

Usage:
    bench --site tboindia console
    >>> exec(open('test_and_fix_escalation_complete.py').read())
"""

import frappe
from frappe.utils import now_datetime, add_to_date

def complete_escalation_system_fix():
    """Complete diagnosis, fix, and test of escalation system"""
    
    print("\n" + "🔧" * 80)
    print("COMPLETE ESCALATION SYSTEM FIX & TEST")
    print("🔧" * 80 + "\n")
    
    issues_found = []
    fixes_applied = []
    
    # === STEP 1: DIAGNOSIS ===
    print("1️⃣ DIAGNOSING SYSTEM...\n")
    
    # Check escalation fields
    try:
        meta = frappe.get_meta("HD Ticket")
        if not meta.get_field("escalation_sent"):
            issues_found.append("Missing escalation_sent field")
        if not meta.get_field("escalated_at"):
            issues_found.append("Missing escalated_at field")
        
        if issues_found:
            print("   ❌ Missing escalation fields")
        else:
            print("   ✅ Escalation fields exist")
    except Exception as e:
        print(f"   ❌ Error checking fields: {e}")
        issues_found.append("Field check error")
    
    # Check notification settings
    try:
        if frappe.db.exists("Customer Support Notification Settings", "Customer Support Notification Settings"):
            settings = frappe.get_single("Customer Support Notification Settings")
            if settings.enable_notifications:
                print("   ✅ Notifications enabled")
            else:
                print("   ❌ Notifications disabled")
                issues_found.append("Notifications disabled")
        else:
            print("   ❌ Notification settings missing")
            issues_found.append("No notification settings")
    except Exception as e:
        print(f"   ❌ Settings error: {e}")
        issues_found.append("Settings error")
    
    # Check escalation rule
    try:
        settings = frappe.get_single("Customer Support Notification Settings")
        escalation_rule = None
        for rule in settings.notification_rules:
            if rule.notification_type == "Escalation" and rule.trigger_event == "Scheduler":
                escalation_rule = rule
                break
        
        if escalation_rule and escalation_rule.enabled:
            print(f"   ✅ Escalation rule active (delay: {escalation_rule.delay_minutes} min)")
        else:
            print("   ❌ No active escalation rule")
            issues_found.append("Missing/disabled escalation rule")
    except Exception as e:
        print(f"   ❌ Rule check error: {e}")
        issues_found.append("Rule check error")
    
    # Check email accounts
    try:
        email_accounts = frappe.get_all("Email Account", 
            filters={"enable_outgoing": 1}, 
            fields=["email_id", "default_outgoing"]
        )
        if email_accounts:
            print(f"   ✅ Found {len(email_accounts)} email account(s)")
        else:
            print("   ❌ No outgoing email accounts")
            issues_found.append("No email accounts")
    except Exception as e:
        print(f"   ❌ Email check error: {e}")
    
    # === STEP 2: APPLY FIXES ===
    print("\n2️⃣ APPLYING FIXES...\n")
    
    # Fix 1: Create escalation fields if missing
    if any("escalation" in issue.lower() and "field" in issue.lower() for issue in issues_found):
        try:
            from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
            
            custom_fields = {
                "HD Ticket": [
                    {
                        "fieldname": "escalation_sent",
                        "fieldtype": "Check",
                        "label": "Escalation Sent",
                        "default": "0",
                        "read_only": 1,
                        "insert_after": "status"
                    },
                    {
                        "fieldname": "escalated_at",
                        "fieldtype": "Datetime", 
                        "label": "Escalated At",
                        "read_only": 1,
                        "insert_after": "escalation_sent"
                    }
                ]
            }
            
            create_custom_fields(custom_fields, update=True)
            fixes_applied.append("Created escalation fields")
            print("   ✅ Created escalation fields")
        except Exception as e:
            print(f"   ❌ Field creation error: {e}")
    
    # Fix 2: Enable notifications if disabled
    if "notifications disabled" in issues_found:
        try:
            settings = frappe.get_single("Customer Support Notification Settings")
            settings.enable_notifications = 1
            settings.save()
            fixes_applied.append("Enabled notifications")
            print("   ✅ Enabled notifications")
        except Exception as e:
            print(f"   ❌ Enable notifications error: {e}")
    
    # Fix 3: Create/fix escalation rule
    if any("rule" in issue.lower() for issue in issues_found):
        try:
            settings = frappe.get_single("Customer Support Notification Settings")
            
            # Remove any existing escalation rules
            settings.notification_rules = [r for r in settings.notification_rules 
                                         if not (r.notification_type == "Escalation" and r.trigger_event == "Scheduler")]
            
            # Add new working escalation rule
            settings.append("notification_rules", {
                "enabled": 1,
                "notification_type": "Escalation",
                "trigger_event": "Scheduler",
                "delay_minutes": 15,
                "email_template": "HD Ticket - Escalation",
                "subject": "🚨 URGENT ESCALATION: Ticket {{ doc.name }} needs attention"
            })
            
            settings.save()
            fixes_applied.append("Created escalation rule")
            print("   ✅ Created/fixed escalation rule")
        except Exception as e:
            print(f"   ❌ Rule fix error: {e}")
    
    # Fix 4: Update email template subject
    try:
        if frappe.db.exists("Email Template", "HD Ticket - Escalation"):
            template = frappe.get_doc("Email Template", "HD Ticket - Escalation")
            if "agent replied" in template.subject.lower():
                template.subject = "🚨 URGENT ESCALATION: Ticket {{ doc.name }} needs immediate attention - {{ doc.subject }}"
                template.save()
                fixes_applied.append("Fixed email template subject")
                print("   ✅ Fixed email template subject")
    except Exception as e:
        print(f"   ❌ Template fix error: {e}")
    
    # === STEP 3: TEST SYSTEM ===
    print("\n3️⃣ TESTING ESCALATION SYSTEM...\n")
    
    try:
        # Import and use the fixed escalation system
        from customer_support.customer_support.fixed_escalation_system import (
            check_escalation_notifications_fixed, 
            force_create_test_escalation
        )
        
        print("   Creating test ticket and triggering escalation...")
        test_ticket = force_create_test_escalation()
        
        if test_ticket:
            print(f"   ✅ Test completed - Ticket: {test_ticket}")
        else:
            print("   ❌ Test failed")
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        print("   Running basic test...")
        
        # Basic test - check for old tickets
        try:
            old_tickets = frappe.get_all("HD Ticket",
                filters={
                    "status": "Open", 
                    "escalation_sent": 0,
                    "creation": ["<", add_to_date(now_datetime(), minutes=-16)]
                },
                fields=["name", "creation"]
            )
            
            print(f"   📊 Found {len(old_tickets)} tickets eligible for escalation")
            
            if old_tickets:
                print("   🔥 These tickets should receive escalation emails:")
                for ticket in old_tickets[:3]:
                    minutes_old = (now_datetime() - ticket.creation).total_seconds() / 60
                    print(f"      - {ticket.name} ({minutes_old:.0f} minutes old)")
                    
        except Exception as e:
            print(f"   ❌ Basic test error: {e}")
    
    # === STEP 4: CHECK RESULTS ===
    print("\n4️⃣ CHECKING RESULTS...\n")
    
    # Check error logs for escalation messages
    try:
        recent_logs = frappe.get_all("Error Log",
            filters={
                "creation": [">", add_to_date(now_datetime(), minutes=-10)],
                "error": ["like", "%escalation%"]
            },
            fields=["error", "creation"],
            order_by="creation desc",
            limit=5
        )
        
        print(f"   📋 Recent escalation logs: {len(recent_logs)}")
        for log in recent_logs[:3]:
            status = "✅" if "success" in log.error.lower() else "ℹ️"
            print(f"      {status} {log.error[:80]}...")
            
    except Exception as e:
        print(f"   ❌ Log check error: {e}")
    
    # Check email queue
    try:
        recent_emails = frappe.get_all("Email Queue",
            filters={
                "creation": [">", add_to_date(now_datetime(), minutes=-10)]
            },
            fields=["subject", "status", "recipients"],
            order_by="creation desc",
            limit=3
        )
        
        escalation_emails = [e for e in recent_emails if "escalation" in e.subject.lower() or "🚨" in e.subject]
        
        print(f"   📧 Recent escalation emails: {len(escalation_emails)}")
        for email in escalation_emails:
            status_icon = "✅" if email.status == "Sent" else "⏳" if email.status == "Not Sent" else "❌"
            print(f"      {status_icon} {email.subject[:60]}... ({email.status})")
            
    except Exception as e:
        print(f"   ❌ Email check error: {e}")
    
    # === SUMMARY ===
    print("\n" + "📋" * 80)
    print("SUMMARY")
    print("📋" * 80)
    
    if issues_found:
        print(f"\n❌ ISSUES FOUND ({len(issues_found)}):")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
    
    if fixes_applied:
        print(f"\n🔧 FIXES APPLIED ({len(fixes_applied)}):")
        for i, fix in enumerate(fixes_applied, 1):
            print(f"   {i}. {fix}")
    
    print(f"\n🎯 NEXT STEPS:")
    print("1. Create a real HD Ticket and set status to 'Open'")
    print("2. Wait 16+ minutes (or use force_create_test_escalation())")
    print("3. Check Error Log for escalation success messages")
    print("4. Check Email Queue for escalation emails")
    print("5. Verify emails are delivered to recipients")
    
    print(f"\n📊 MONITORING:")
    print("- Watch Error Log for 'Escalation Success' messages")
    print("- Monitor Email Queue for escalation emails") 
    print("- Check escalation_sent field updates on tickets")
    
    frappe.db.commit()
    
    print(f"\n🎉 ESCALATION SYSTEM FIX COMPLETE!")
    print("📧 Check your email for test escalation notifications")


def quick_escalation_test():
    """Quick test to verify escalation is working"""
    
    print("\n🚀 QUICK ESCALATION TEST\n")
    
    try:
        # Use the fixed escalation system
        from customer_support.customer_support.fixed_escalation_system import check_escalation_notifications_fixed
        
        print("Running escalation check...")
        check_escalation_notifications_fixed()
        
        print("✅ Escalation check completed")
        print("📧 Check Error Log and Email Queue for results")
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")


def show_escalation_status():
    """Show current status of escalation system"""
    
    print("\n📊 ESCALATION SYSTEM STATUS\n")
    
    try:
        # Check eligible tickets
        eligible = frappe.get_all("HD Ticket",
            filters={
                "status": "Open",
                "escalation_sent": 0,
                "creation": ["<", add_to_date(now_datetime(), minutes=-15)]
            },
            fields=["name", "creation", "subject"]
        )
        
        print(f"🎫 Tickets eligible for escalation: {len(eligible)}")
        for ticket in eligible[:5]:
            minutes_old = (now_datetime() - ticket.creation).total_seconds() / 60
            print(f"   - {ticket.name}: {minutes_old:.0f} minutes old")
        
        # Check already escalated
        escalated = frappe.get_all("HD Ticket",
            filters={"escalation_sent": 1},
            fields=["name", "escalated_at"]
        )
        
        print(f"\n🚨 Previously escalated tickets: {len(escalated)}")
        for ticket in escalated[-3:]:
            print(f"   - {ticket.name}: {ticket.escalated_at}")
        
    except Exception as e:
        print(f"❌ Status check error: {e}")


if __name__ == "__main__":
    print("🔧 ESCALATION SYSTEM TOOLS LOADED")
    print("Available functions:")
    print("1. complete_escalation_system_fix() - Full diagnosis & fix")
    print("2. quick_escalation_test() - Quick test")
    print("3. show_escalation_status() - Show current status")
    print("\nRun: complete_escalation_system_fix() to start")