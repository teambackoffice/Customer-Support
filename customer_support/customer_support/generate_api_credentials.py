#!/usr/bin/env python3
"""
Generate API credentials for Ticket Sync
Run this on the SOURCE site (the one you want to sync FROM)

For medservice site:
  bench --site medservice execute customer_support.generate_api_credentials.generate

This will generate fresh API Key + Secret for the Administrator user
"""

import frappe

def generate(user="Administrator"):
    """Generate API credentials for a user"""
    
    try:
        # Check if user exists
        if not frappe.db.exists("User", user):
            print(f"✗ User '{user}' not found")
            return
        
        # Get user document
        user_doc = frappe.get_doc("User", user)
        
        # Generate API keys
        api_key = frappe.generate_hash(length=15)
        api_secret = frappe.generate_hash(length=15)
        
        # Set the keys
        user_doc.api_key = api_key
        user_doc.api_secret = api_secret
        user_doc.save(ignore_permissions=True)
        
        frappe.db.commit()
        
        print("=" * 80)
        print("API CREDENTIALS GENERATED SUCCESSFULLY")
        print("=" * 80)
        print()
        print(f"User: {user}")
        print(f"API Key: {api_key}")
        print(f"API Secret: {api_secret}")
        print()
        print("IMPORTANT: Copy these credentials NOW!")
        print("The API Secret cannot be retrieved again after this.")
        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print()
        print("1. Copy the API Key and API Secret above")
        print()
        print("2. On tboindia site, update the Ticket Sync Source:")
        print("   - Go to: Ticket Sync Source → Medservice")
        print("   - Paste the API Key")
        print("   - Paste the API Secret")
        print("   - Save")
        print()
        print("3. Test the sync:")
        print("   bench --site tboindia execute customer_support.diagnose_sync.diagnose")
        print()
        
    except Exception as e:
        print(f"✗ Error generating credentials: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    # Detect which site we're on
    import sys
    if len(sys.argv) > 1:
        site = sys.argv[1]
    else:
        site = "medservice"  # default
    
    frappe.init(site=site)
    frappe.connect()
    generate()
    frappe.destroy()
