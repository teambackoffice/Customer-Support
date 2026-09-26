#!/usr/bin/env python3
"""
Configure Ticket Sync Source
Run with: bench --site tboindia execute customer_support.configure_ticket_sync.configure

Update the values below before running!
"""

import frappe

def configure():
    """Configure the Medservice ticket sync source with correct credentials"""
    
    # ============================================
    # UPDATE THESE VALUES WITH YOUR ACTUAL DATA
    # ============================================
    
    SITE_NAME = "Medservice"  # Friendly name for the source
    SITE_URL = "http://127.0.0.1:8001"  # CHANGE THIS to actual source site URL
    API_KEY = "YOUR_API_KEY_HERE"  # From source site
    API_SECRET = "YOUR_API_SECRET_HERE"  # From source site
    ENABLED = 1  # 1 = enabled, 0 = disabled
    
    # ============================================
    
    try:
        if not frappe.db.exists("Ticket Sync Source", "Medservice"):
            print("✗ 'Medservice' Ticket Sync Source not found")
            print("  Create it first via the UI")
            return
        
        # Validate that values were changed
        if API_KEY == "YOUR_API_KEY_HERE" or API_SECRET == "YOUR_API_SECRET_HERE":
            print("✗ ERROR: Please update the API credentials in the script first!")
            print("  Edit: customer_support/configure_ticket_sync.py")
            print("  Update: API_KEY and API_SECRET variables")
            return
        
        if SITE_URL == "http://127.0.0.1:8001":
            print("⚠ WARNING: Using default URL. Is this correct?")
            print(f"  Site URL: {SITE_URL}")
            response = input("  Continue? (yes/no): ")
            if response.lower() != "yes":
                print("  Aborted.")
                return
        
        # Update the document
        doc = frappe.get_doc("Ticket Sync Source", "Medservice")
        doc.site_name = SITE_NAME
        doc.site_url = SITE_URL
        doc.api_key = API_KEY
        doc.set_value("api_secret", API_SECRET)  # Use set_value for password fields
        doc.enabled = ENABLED
        doc.save()
        
        frappe.db.commit()
        
        print("✓ Successfully configured 'Medservice' Ticket Sync Source")
        print(f"  Site Name: {SITE_NAME}")
        print(f"  Site URL: {SITE_URL}")
        print(f"  API Key: {API_KEY[:10]}...")
        print(f"  Enabled: {'Yes' if ENABLED else 'No'}")
        print("\nYou can now test the sync manually from the UI")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        frappe.log_error(frappe.get_traceback(), "Configure Ticket Sync Failed")

if __name__ == "__main__":
    frappe.init(site="tboindia")
    frappe.connect()
    configure()
    frappe.destroy()
