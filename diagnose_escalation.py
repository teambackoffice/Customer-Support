#!/usr/bin/env python3
"""
Quick Escalation Email Diagnosis Script
Run this in bench console to identify why escalation emails aren't working

Usage:
    bench --site [site-name] console
    >>> exec(open('diagnose_escalation.py').read())
"""

import frappe
from frappe.utils import now_datetime, add_to_date

def diagnose_escalation_system():
    """Complete diagnostic of escalation email system"""
    
    print("\n" + "="*80)
    print("🚨 ESCALATION EMAIL SYSTEM DIAGNOSIS")
    print("="*80 + "\n")
    
    issues_found = []
    fixes_needed = []
    
    # Test 1: Check if escalation fields exist
    print("1️⃣ Checking escalation fields...")
    try:
        meta = frappe.get_meta("HD Ticket")
        escalation_sent = meta.get_field("escalation_sent")
        escalated_at = meta.get_field("escalated_at")
        
        if escalation_sent and escalated_at:
            print("   ✅ Escalation fields exist")
        else:
            print("   ❌ Escalation fields missing")
            issues_found.append("Missing escalation fields")
            fixes_needed.append("Run: bench --site [site] migrate")
    except Exception as e:
        print(f"   ❌ Error checking fields: {e}")
        issues_found.append("Field check failed")
    
    # Test 2: Check notification settings
    print("\n2️⃣ Checking notification settings...")
    try:
        if frappe.db.exists("Customer Support Notification Settings", "Customer Support Notification Settings"):
            settings = frappe.get_single("Customer Support Notification Settings")
            print(f"   ✅ Settings found - Enabled: {settings.enable_notifications}")
            print(f"   📧 Default email: {settings.default_from_email or 'Not set'}")
            
            if not settings.enable_notifications:
                issues_found.append("Notifications disabled")
                fixes_needed.append("Enable notifications in Customer Support Notification Settings")
                
            if not settings.default_from_email:
                issues_found.append("No default from email")
                fixes_needed.append("Set default from email in notification settings")
        else:
            print("   ❌ Notification Settings not found")
            issues_found.append("Missing notification settings")
            fixes_needed.append("Create Customer Support Notification Settings")
    except Exception as e:
        print(f"   ❌ Error checking settings: {e}")
        issues_found.append("Settings check failed")
    
    # Test 3: Check escalation rule
    print("\n3️⃣ Checking escalation rule...")
    try:
        settings = frappe.get_single("Customer Support Notification Settings")
        escalation_rule = None
        
        for rule in settings.notification_rules:
            if rule.notification_type == "Escalation" and rule.trigger_event == "Scheduler":
                escalation_rule = rule
                break
        
        if escalation_rule:
            print(f"   ✅ Escalation rule found")
            print(f"   ⏰ Delay: {escalation_rule.delay_minutes} minutes")
            print(f"   🔔 Enabled: {escalation_rule.enabled}")
            print(f"   📧 Template: {escalation_rule.email_template}")
            
            if not escalation_rule.enabled:
                issues_found.append("Escalation rule disabled")
                fixes_needed.append("Enable escalation rule in notification settings")
        else:
            print("   ❌ Escalation rule not found")
            issues_found.append("Missing escalation rule")
            fixes_needed.append("Add escalation rule to notification settings")
    except Exception as e:
        print(f"   ❌ Error checking rule: {e}")
        issues_found.append("Rule check failed")
    
    # Test 4: Check email template
    print("\n4️⃣ Checking email template...")
    try:
        template_exists = frappe.db.exists("Email Template", "HD Ticket - Escalation")
        if template_exists:
            print("   ✅ Email template exists")
        else:
            print("   ❌ Email template missing")
            issues_found.append("Missing email template")
            fixes_needed.append("Run: bench --site [site] migrate to import template")
    except Exception as e:
        print(f"   ❌ Error checking template: {e}")
        issues_found.append("Template check failed")
    
    # Test 5: Check email accounts
    print("\n5️⃣ Checking email accounts...")
    try:
        email_accounts = frappe.get_all("Email Account", 
            filters={"enable_outgoing": 1}, 
            fields=["email_id", "default_outgoing", "enable_outgoing"]
        )
        
        if email_accounts:
            print(f"   ✅ Found {len(email_accounts)} outgoing email account(s)")
            for acc in email_accounts:
                print(f"      📧 {acc.email_id} (default: {acc.default_outgoing})")
        else:
            print("   ❌ No outgoing email accounts configured")
            issues_found.append("No email accounts")
            fixes_needed.append("Configure outgoing email account in Email Account doctype")
    except Exception as e:
        print(f"   ❌ Error checking email accounts: {e}")
        issues_found.append("Email account check failed")
    
    # Test 6: Check scheduler
    print("\n6️⃣ Checking scheduler...")
    try:
        from customer_support.customer_support.scheduler import check_escalation_notifications
        print("   ✅ Scheduler function accessible")
        
        # Check if scheduler is enabled
        scheduler_enabled = frappe.utils.cint(frappe.db.get_single_value("System Settings", "enable_scheduler"))
        if scheduler_enabled:
            print("   ✅ Scheduler is enabled")
        else:
            print("   ❌ Scheduler is disabled")
            issues_found.append("Scheduler disabled")
            fixes_needed.append("Enable scheduler in System Settings")
    except Exception as e:
        print(f"   ❌ Error checking scheduler: {e}")
        issues_found.append("Scheduler check failed")
    
    # Test 7: Check for tickets eligible for escalation
    print("\n7️⃣ Checking eligible tickets...")
    try:
        eligible_tickets = frappe.get_all("HD Ticket",
            filters={
                "status": "Open",
                "escalation_sent": 0,
                "creation": ["<", add_to_date(now_datetime(), minutes=-16)]
            },
            fields=["name", "creation", "status"]
        )
        
        print(f"   📊 Found {len(eligible_tickets)} tickets eligible for escalation")
        if eligible_tickets:
            for ticket in eligible_tickets[:3]:  # Show first 3
                minutes_old = (now_datetime() - ticket.creation).total_seconds() / 60
                print(f"      🎫 {ticket.name} - {minutes_old:.0f} minutes old")
    except Exception as e:
        print(f"   ❌ Error checking tickets: {e}")
    
    # Test 8: Check recent email queue
    print("\n8️⃣ Checking email queue...")
    try:
        recent_emails = frappe.get_all("Email Queue",
            filters={
                "creation": [">", add_to_date(now_datetime(), hours=-2)]
            },
            fields=["subject", "status", "error", "creation"],
            order_by="creation desc",
            limit=5
        )
        
        print(f"   📬 Found {len(recent_emails)} emails in queue (last 2 hours)")
        escalation_emails = [e for e in recent_emails if "escalation" in e.subject.lower()]
        print(f"   🚨 Found {len(escalation_emails)} escalation emails in queue")
        
        if escalation_emails:
            for email in escalation_emails:
                print(f"      📧 {email.subject} - Status: {email.status}")
                if email.error:
                    print(f"         ❌ Error: {email.error}")
    except Exception as e:
        print(f"   ❌ Error checking email queue: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("📋 DIAGNOSIS SUMMARY")
    print("="*80)
    
    if not issues_found:
        print("🎉 NO ISSUES FOUND - System should be working!")
        print("\nTo test escalation:")
        print("1. Create a new HD Ticket")
        print("2. Wait 16+ minutes")
        print("3. Check Email Queue for escalation emails")
    else:
        print(f"❌ FOUND {len(issues_found)} ISSUE(S):")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 FIXES NEEDED:")
        for i, fix in enumerate(fixes_needed, 1):
            print(f"   {i}. {fix}")
    
    # Quick fix code
    if issues_found:
        print(f"\n💡 QUICK FIX CODE:")
        print("Copy and run this code to fix common issues:")
        print("""
# Fix notification settings
if not frappe.db.exists("Customer Support Notification Settings", "Customer Support Notification Settings"):
    settings = frappe.new_doc("Customer Support Notification Settings")
    settings.enable_notifications = 1
    settings.company = frappe.defaults.get_user_default("Company") or "Your Company"
    settings.default_from_email = "support@yourcompany.com"  # CHANGE THIS
    
    # Add escalation rule
    settings.append("notification_rules", {
        "enabled": 1,
        "notification_type": "Escalation", 
        "trigger_event": "Scheduler",
        "delay_minutes": 15,
        "email_template": "HD Ticket - Escalation",
        "send_to_assigned_agent": 1,
        "cc_support_team": 1
    })
    
    settings.insert(ignore_permissions=True)
    print("✅ Created notification settings")

# Enable notifications if disabled
settings = frappe.get_single("Customer Support Notification Settings")
if not settings.enable_notifications:
    settings.enable_notifications = 1
    settings.save(ignore_permissions=True)
    print("✅ Enabled notifications")
""")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    diagnose_escalation_system()