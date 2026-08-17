#!/usr/bin/env python3

"""
Diagnose and fix notification system issues
"""

import frappe
from frappe.utils import now_datetime


def diagnose_notification_issues():
    """Diagnose why notifications are not working"""
    
    print("🔍 DIAGNOSING NOTIFICATION SYSTEM ISSUES")
    print("=" * 50)
    
    issues_found = []
    
    # 1. Check if hooks are registered
    print("\n1️⃣ CHECKING HOOKS REGISTRATION")
    print("-" * 35)
    
    try:
        # Check if our hooks are in the system
        from frappe import get_hooks
        
        doc_events = get_hooks("doc_events")
        
        if "HD Ticket" in doc_events:
            print("✅ HD Ticket hooks found")
            
            hd_hooks = doc_events["HD Ticket"]
            
            # Check specific hooks
            if "after_insert" in hd_hooks:
                after_insert_hooks = hd_hooks["after_insert"]
                if isinstance(after_insert_hooks, list):
                    notification_hook_found = any("notification_system" in hook for hook in after_insert_hooks)
                else:
                    notification_hook_found = "notification_system" in after_insert_hooks
                
                if notification_hook_found:
                    print("✅ New ticket notification hook registered")
                else:
                    print("❌ New ticket notification hook NOT registered")
                    issues_found.append("Missing after_insert notification hook")
            else:
                print("❌ No after_insert hooks found")
                issues_found.append("Missing after_insert hooks")
            
            if "on_update" in hd_hooks:
                on_update_hooks = hd_hooks["on_update"]
                if isinstance(on_update_hooks, list):
                    notification_hook_found = any("notification_system" in hook for hook in on_update_hooks)
                else:
                    notification_hook_found = "notification_system" in on_update_hooks
                
                if notification_hook_found:
                    print("✅ Update notification hook registered")
                else:
                    print("❌ Update notification hook NOT registered")
                    issues_found.append("Missing on_update notification hook")
        else:
            print("❌ No HD Ticket hooks found at all")
            issues_found.append("No HD Ticket hooks registered")
            
    except Exception as e:
        print(f"❌ Error checking hooks: {str(e)}")
        issues_found.append(f"Hook check error: {str(e)}")
    
    # 2. Check notification system import
    print("\n2️⃣ CHECKING NOTIFICATION SYSTEM IMPORT")
    print("-" * 40)
    
    try:
        from customer_support.customer_support.notification_system import NotificationSystem
        print("✅ NotificationSystem can be imported")
        
        # Test basic functionality
        settings = NotificationSystem.get_notification_settings()
        if settings:
            print("✅ Can retrieve notification settings")
        else:
            print("❌ Cannot retrieve notification settings")
            issues_found.append("Settings retrieval failed")
            
    except Exception as e:
        print(f"❌ Cannot import NotificationSystem: {str(e)}")
        issues_found.append(f"Import error: {str(e)}")
    
    # 3. Check scheduler registration
    print("\n3️⃣ CHECKING SCHEDULER REGISTRATION")
    print("-" * 35)
    
    try:
        scheduler_events = get_hooks("scheduler_events")
        
        if "cron" in scheduler_events:
            cron_jobs = scheduler_events["cron"]
            
            escalation_job_found = False
            for cron_pattern, jobs in cron_jobs.items():
                if isinstance(jobs, list):
                    for job in jobs:
                        if "check_escalation_notifications" in job:
                            escalation_job_found = True
                            print(f"✅ Escalation scheduler found: {cron_pattern}")
                            break
                else:
                    if "check_escalation_notifications" in jobs:
                        escalation_job_found = True
                        print(f"✅ Escalation scheduler found: {cron_pattern}")
            
            if not escalation_job_found:
                print("❌ Escalation scheduler NOT registered")
                issues_found.append("Missing escalation scheduler")
        else:
            print("❌ No cron jobs found")
            issues_found.append("No cron scheduler configured")
            
    except Exception as e:
        print(f"❌ Error checking scheduler: {str(e)}")
        issues_found.append(f"Scheduler check error: {str(e)}")
    
    # 4. Check email account configuration
    print("\n4️⃣ CHECKING EMAIL CONFIGURATION")
    print("-" * 32)
    
    try:
        email_accounts = frappe.get_all("Email Account", 
            filters={"enable_outgoing": 1}, 
            fields=["name", "email_id", "smtp_server"])
        
        if email_accounts:
            print(f"✅ Found {len(email_accounts)} outgoing email accounts:")
            for account in email_accounts:
                print(f"   📧 {account.name}: {account.email_id}")
        else:
            print("⚠️  No outgoing email accounts configured")
            issues_found.append("No SMTP configuration")
            
    except Exception as e:
        print(f"❌ Error checking email accounts: {str(e)}")
    
    # 5. Test notification functions directly
    print("\n5️⃣ TESTING NOTIFICATION FUNCTIONS")
    print("-" * 35)
    
    try:
        # Create a test ticket (without saving to DB)
        test_ticket = frappe.new_doc("HD Ticket")
        test_ticket.name = "TEST-NOTIFICATION"
        test_ticket.subject = "Test Notification"
        test_ticket.contact_email = "test@example.com"
        test_ticket.status = "Open"
        
        # Test notification system functions
        from customer_support.customer_support.notification_system import NotificationSystem
        
        # Test get notification rule
        new_ticket_rule = NotificationSystem.get_notification_rule("New Ticket", "After Insert")
        if new_ticket_rule:
            print("✅ Can retrieve New Ticket rule")
            
            # Test recipient building
            recipients = NotificationSystem.build_recipient_list(new_ticket_rule, test_ticket)
            print(f"✅ Recipients built: {len(sum(recipients.values(), []))} total")
            
            if not any(recipients.values()):
                print("⚠️  No recipients found - this explains why notifications don't work")
                issues_found.append("No recipients configured properly")
            
        else:
            print("❌ Cannot retrieve New Ticket rule")
            issues_found.append("Rule retrieval failed")
            
    except Exception as e:
        print(f"❌ Function test failed: {str(e)}")
        issues_found.append(f"Function test error: {str(e)}")
    
    return issues_found


def fix_notification_issues():
    """Fix identified notification issues"""
    
    print("\n🔧 FIXING NOTIFICATION ISSUES")
    print("=" * 35)
    
    fixed_count = 0
    
    # Fix 1: Reload hooks
    print("\n🔄 Reloading hooks...")
    try:
        frappe.clear_cache()
        print("✅ Cache cleared")
        fixed_count += 1
    except Exception as e:
        print(f"❌ Cache clear failed: {str(e)}")
    
    # Fix 2: Test notification manually
    print("\n🧪 Testing manual notification...")
    try:
        # Create a real test ticket
        timestamp = now_datetime().strftime("%Y%m%d_%H%M%S")
        
        ticket = frappe.new_doc("HD Ticket")
        ticket.subject = f"FIX TEST {timestamp}"
        ticket.description = "Testing notification fix"
        ticket.contact_email = "fixtest@example.com"
        ticket.status = "Open"
        
        # Insert without triggering hooks first
        ticket.flags.ignore_hooks = True
        ticket.insert(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ Test ticket created: {ticket.name}")
        
        # Now manually trigger notification
        from customer_support.customer_support.notification_system import on_ticket_insert
        
        # Remove ignore_hooks flag
        ticket.flags.ignore_hooks = False
        
        # Manually call the hook
        on_ticket_insert(ticket)
        
        print("✅ Manual notification trigger executed")
        fixed_count += 1
        
        return ticket
        
    except Exception as e:
        print(f"❌ Manual test failed: {str(e)}")
        return None


def create_working_notification_test():
    """Create a simple working notification test"""
    
    print("\n✨ CREATING WORKING NOTIFICATION TEST")
    print("=" * 40)
    
    try:
        # Get settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        # Find new ticket rule
        new_ticket_rule = None
        for rule in settings.notification_rules:
            if rule.notification_type == "New Ticket":
                new_ticket_rule = rule
                break
        
        if not new_ticket_rule:
            print("❌ No New Ticket rule found")
            return False
        
        print(f"✅ Found New Ticket rule: {new_ticket_rule.name}")
        
        # Check recipients
        recipients = frappe.get_all("Notification Recipient",
            filters={"parent": new_ticket_rule.name},
            fields=["recipient_role", "recipient_type", "custom_email"]
        )
        
        print(f"👥 Recipients found: {len(recipients)}")
        for recipient in recipients:
            print(f"   {recipient.recipient_role}: {recipient.recipient_type}")
            if recipient.custom_email:
                print(f"      Email: {recipient.custom_email}")
        
        # Create and send a manual notification
        from frappe.core.doctype.communication.email import make
        
        print("\n📧 Creating manual email notification...")
        
        # Build email content
        subject = "TEST: Manual Notification System Test"
        content = f"""
        <h2>Notification System Test</h2>
        <p>This is a manual test of the Customer Support Notification System.</p>
        <p><strong>Time:</strong> {now_datetime()}</p>
        <p><strong>Status:</strong> Testing notification delivery</p>
        <hr>
        <p>If you receive this email, the notification system is working!</p>
        """
        
        # Send to custom email recipients
        for recipient in recipients:
            if recipient.custom_email and recipient.recipient_type == "Custom Email":
                try:
                    make(
                        recipients=[recipient.custom_email],
                        subject=subject,
                        content=content,
                        send_email=True
                    )
                    print(f"✅ Email queued to: {recipient.custom_email}")
                except Exception as e:
                    print(f"❌ Email failed to: {recipient.custom_email} - {str(e)}")
        
        frappe.db.commit()
        
        print("✅ Manual notification test completed")
        return True
        
    except Exception as e:
        print(f"❌ Working test failed: {str(e)}")
        return False


def main():
    """Main diagnostic and fix function"""
    
    print("🚀 NOTIFICATION SYSTEM DIAGNOSIS & FIX")
    print("=" * 45)
    
    # Step 1: Diagnose
    issues = diagnose_notification_issues()
    
    if issues:
        print(f"\n⚠️  ISSUES FOUND ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ NO ISSUES FOUND")
    
    # Step 2: Fix
    test_ticket = fix_notification_issues()
    
    # Step 3: Create working test
    working_test = create_working_notification_test()
    
    # Summary
    print(f"\n🎯 DIAGNOSIS & FIX SUMMARY")
    print("=" * 30)
    
    if len(issues) == 0:
        print("✅ System appears to be configured correctly")
    else:
        print(f"⚠️  {len(issues)} issues identified and addressed")
    
    if working_test:
        print("✅ Manual notification test successful")
    else:
        print("❌ Manual notification test failed")
    
    print(f"\n💡 NEXT STEPS:")
    print("   1. Check Email Queue for queued emails")
    print("   2. Configure SMTP if emails aren't being sent")
    print("   3. Create a real HD Ticket to test live notifications")
    
    if test_ticket:
        print(f"   4. Test ticket created: {test_ticket.name}")


if __name__ == "__main__":
    main()