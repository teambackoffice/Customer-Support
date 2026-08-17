#!/usr/bin/env python3
"""
Fix script to make default_from_email_address field work
"""

import frappe

def execute():
    """Fix the email configuration to use default_from_email_address"""
    print("🔧 Fixing email configuration to use default_from_email_address...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"\n📋 Current Settings:")
        print(f"   Default From Email (Link): '{settings.default_from_email}'")
        print(f"   Email (Direct): '{settings.default_from_email_address}'")
        
        # Clear the default_from_email field so default_from_email_address can work
        if settings.default_from_email_address:
            print(f"\n✅ You have a direct email address set: {settings.default_from_email_address}")
            print(f"🔧 Clearing the 'Default From Email' field so the direct email works...")
            
            settings.default_from_email = ""  # Clear the Email Account link
            settings.save(ignore_permissions=True)
            frappe.db.commit()
            
            print(f"\n✅ Fixed! Email configuration updated:")
            print(f"   Default From Email (Link): '{settings.default_from_email}' (cleared)")
            print(f"   Email (Direct): '{settings.default_from_email_address}' (will be used)")
            
        else:
            print(f"\n⚠️  No email address found in 'Email' field.")
            print(f"   Please add your email address to the 'Email' field first.")
        
        print(f"\n🎯 How it works now:")
        print(f"   1. The system will skip the empty 'Default From Email' field")
        print(f"   2. It will use the 'Email' field as fallback")
        print(f"   3. Your notifications should work with the direct email address")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    execute()