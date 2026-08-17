import frappe

def execute():
    """Fix email settings and create proper email account"""
    print("📧 Fixing Email Settings...")
    
    try:
        # Check current notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"📋 Current Email Settings:")
        print(f"   Default From Email: {settings.default_from_email}")
        print(f"   Reply To: {settings.reply_to}")
        
        # Check what email accounts are available
        email_accounts = frappe.get_all("Email Account", fields=["name", "email_id", "default_outgoing"])
        
        print(f"\n📬 Available Email Accounts:")
        for account in email_accounts:
            print(f"   - {account.name}: {account.email_id} (Default: {account.default_outgoing})")
        
        # Look for a valid email account to use
        valid_email_account = None
        
        # Try to find tboindia domain email
        for account in email_accounts:
            if "tboindia.com" in account.email_id or account.default_outgoing:
                valid_email_account = account.name
                break
        
        # If no tboindia email found, use any valid email account
        if not valid_email_account and email_accounts:
            valid_email_account = email_accounts[0].name
        
        if valid_email_account:
            print(f"\n✅ Using email account: {valid_email_account}")
            
            # Update notification settings with valid email
            settings.default_from_email = valid_email_account
            
            # Set a valid reply-to email
            email_account_doc = frappe.get_doc("Email Account", valid_email_account)
            settings.reply_to = email_account_doc.email_id
            
            settings.save(ignore_permissions=True)
            frappe.db.commit()
            
            print(f"✅ Updated notification settings:")
            print(f"   Default From Email: {settings.default_from_email}")
            print(f"   Reply To: {settings.reply_to}")
        
        else:
            print(f"\n⚠️  No email accounts found. Creating a default one...")
            
            # Create a default email account for notifications
            try:
                email_account = frappe.new_doc("Email Account")
                email_account.email_id = "noreply@tboindia.com"
                email_account.account_name = "TBO Support Notifications"
                email_account.default_outgoing = 0
                email_account.enable_outgoing = 1
                email_account.smtp_server = "smtp.gmail.com"  # Default SMTP
                email_account.smtp_port = 587
                email_account.use_tls = 1
                email_account.insert(ignore_permissions=True)
                
                # Update notification settings
                settings.default_from_email = email_account.name
                settings.reply_to = email_account.email_id
                settings.save(ignore_permissions=True)
                frappe.db.commit()
                
                print(f"✅ Created email account: {email_account.email_id}")
                print(f"✅ Updated notification settings")
                
            except Exception as e:
                print(f"❌ Could not create email account: {str(e)}")
                
                # Set reply_to to a valid format at least
                settings.reply_to = "noreply@tboindia.com"
                settings.default_from_email = ""  # Clear invalid value
                settings.save(ignore_permissions=True)
                frappe.db.commit()
                
                print(f"✅ Cleared invalid email settings")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Go to Setup > Email > Email Account")
        print(f"   2. Configure your actual SMTP settings")
        print(f"   3. Set proper from email in notification settings")
        print(f"   4. Test notifications by creating a ticket")
        
        # Test a simple notification
        print(f"\n🧪 Testing notification system...")
        
        # Get a sample ticket for testing
        tickets = frappe.get_all("HD Ticket", limit=1)
        if tickets:
            ticket = frappe.get_doc("HD Ticket", tickets[0].name)
            
            # Test the new simple recipient system
            from customer_support.customer_support.notification_system import NotificationSystem
            
            rule = settings.notification_rules[0] if settings.notification_rules else None
            if rule:
                recipients = NotificationSystem.build_recipient_list(rule, ticket)
                
                print(f"📬 Test Recipients for '{rule.notification_type}':")
                print(f"   To: {recipients['to']}")
                print(f"   CC: {recipients['cc']}")
                print(f"   BCC: {recipients['bcc']}")
                print(f"   Total: {len(recipients['to']) + len(recipients['cc']) + len(recipients['bcc'])}")
        
        print(f"\n✅ Email settings fixed! Try saving the notification settings now.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()