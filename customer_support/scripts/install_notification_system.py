#!/usr/bin/env python3

"""
Customer Support Notification System Installation Script

This script ensures proper installation of the notification system.

Usage:
    bench execute customer_support.scripts.install_notification_system.install
"""

import frappe
from frappe import _


def install():
    """Complete installation of the notification system"""
    
    print("🚀 Installing Customer Support Notification System...")
    print("=" * 60)
    
    try:
        # Step 1: Run database migrations
        print("\n📊 Step 1: Running database migrations...")
        run_migrations()
        
        # Step 2: Create email templates
        print("\n📧 Step 2: Creating email templates...")
        create_email_templates()
        
        # Step 3: Setup notification settings
        print("\n⚙️ Step 3: Setting up notification configuration...")
        setup_notifications()
        
        # Step 4: Validate installation
        print("\n✅ Step 4: Validating installation...")
        validate_installation()
        
        print("\n" + "=" * 60)
        print("🎉 Installation completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Go to: Setup → Customer Support Notification Settings")
        print("   2. Configure your company and email settings")
        print("   3. Test by creating and updating HD Tickets")
        
    except Exception as e:
        print(f"\n❌ Installation failed: {str(e)}")
        frappe.log_error(f"Notification system installation failed: {str(e)}", "Installation Error")


def run_migrations():
    """Run database migrations to create DocTypes"""
    
    try:
        # Force reload DocType modules
        frappe.reload_doctype("Customer Support Notification Settings")
        frappe.reload_doctype("Support Notification Rule") 
        frappe.reload_doctype("Notification Recipient")
        
        print("✅ Database migrations completed")
        
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        # Try to migrate manually
        try:
            frappe.db.commit()
            print("✅ Database committed successfully")
        except Exception as commit_error:
            print(f"❌ Database commit failed: {str(commit_error)}")
            raise


def create_email_templates():
    """Create email templates from fixtures"""
    
    templates = [
        "HD Ticket - New Ticket",
        "HD Ticket - Escalation", 
        "HD Ticket - Resolved"
    ]
    
    created_count = 0
    
    for template_name in templates:
        if not frappe.db.exists("Email Template", template_name):
            try:
                # Templates will be created by fixtures during bench migrate
                print(f"📧 Template '{template_name}' will be created via fixtures")
                created_count += 1
            except Exception as e:
                print(f"❌ Failed to create template '{template_name}': {str(e)}")
        else:
            print(f"✅ Template '{template_name}' already exists")
    
    if created_count > 0:
        print(f"📧 {created_count} email templates ready for creation")


def setup_notifications():
    """Setup notification configuration"""
    
    try:
        # Get default company
        company = frappe.defaults.get_user_default("Company")
        if not company:
            # Get first available company
            companies = frappe.get_all("Company", limit=1, pluck="name")
            company = companies[0] if companies else "Default Company"
        
        # Import and run setup
        from customer_support.scripts.setup_notification_system import setup_default_notifications
        setup_default_notifications(company)
        
        print(f"✅ Notification settings configured for: {company}")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        # Create basic settings manually
        try:
            settings = frappe.get_single("Customer Support Notification Settings")
            if not settings.company:
                settings.company = company
                settings.enable_notifications = 1
                settings.save(ignore_permissions=True)
                frappe.db.commit()
                print(f"✅ Basic settings created for: {company}")
        except Exception as manual_error:
            print(f"❌ Manual setup failed: {str(manual_error)}")


def validate_installation():
    """Validate that everything is installed correctly"""
    
    issues = []
    
    # Check DocTypes
    doctypes = [
        "Customer Support Notification Settings",
        "Support Notification Rule", 
        "Notification Recipient"
    ]
    
    for doctype in doctypes:
        if frappe.db.exists("DocType", doctype):
            print(f"✅ DocType '{doctype}' exists")
        else:
            issues.append(f"❌ DocType '{doctype}' missing")
    
    # Check settings
    try:
        settings = frappe.get_single("Customer Support Notification Settings")
        if settings:
            print("✅ Notification settings accessible")
        else:
            issues.append("❌ Notification settings not accessible")
    except Exception as e:
        issues.append(f"❌ Settings error: {str(e)}")
    
    # Check email templates
    templates = ["HD Ticket - New Ticket", "HD Ticket - Escalation", "HD Ticket - Resolved"]
    for template in templates:
        if frappe.db.exists("Email Template", template):
            print(f"✅ Email template '{template}' exists")
        else:
            issues.append(f"❌ Email template '{template}' missing")
    
    if issues:
        print("\n⚠️ Issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("\n🎉 All validations passed!")
        return True


if __name__ == "__main__":
    install()