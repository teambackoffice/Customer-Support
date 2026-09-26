#!/usr/bin/env python3
"""
Check current Ticket Sync configuration
Run: bench --site tboindia execute customer_support.check_sync_config.check
"""

import frappe

def check():
    """Check current sync configuration"""
    
    print("=" * 80)
    print("TICKET SYNC CONFIGURATION CHECK")
    print("=" * 80)
    print()
    
    # Find all sync sources
    sources = frappe.get_all("Ticket Sync Source", fields=["name"])
    
    if not sources:
        print("✗ No Ticket Sync Sources found")
        print("\nCreate one:")
        print("  1. Go to: Ticket Sync Source → New")
        print("  2. Set the configuration")
        return
    
    print(f"Found {len(sources)} Ticket Sync Source(s):\n")
    
    for src in sources:
        doc = frappe.get_doc("Ticket Sync Source", src.name)
        
        print(f"Name: {doc.name}")
        print(f"  Site Name: {doc.site_name}")
        print(f"  Site URL: {doc.site_url}")
        print(f"  API Key: {doc.api_key[:10] if doc.api_key else 'NOT SET'}...")
        print(f"  API Secret: {'SET (' + str(len(doc.get_password('api_secret'))) + ' chars)' if doc.get_password('api_secret') else 'NOT SET'}")
        print(f"  Enabled: {'✓ Yes' if doc.enabled else '✗ No'}")
        print(f"  Last Sync: {doc.last_sync_on or 'Never'}")
        print(f"  Last Message: {(doc.last_sync_message or 'None')[:100]}")
        print()
        
        # Warnings
        if doc.site_url == "http://127.0.0.1:8000" or doc.site_url == "http://127.0.0.1:8000/app":
            print("  ⚠ WARNING: Site URL points to port 8000 (same as tboindia)")
            print("    This will sync from itself, which doesn't make sense.")
            print("    Change to the actual source site URL (e.g., http://127.0.0.1:8001)")
            print()
        
        if not doc.api_key or not doc.get_password('api_secret'):
            print("  ⚠ WARNING: API credentials not set")
            print("    Generate them on the source site and update here")
            print()
        
        print("-" * 80)
        print()

if __name__ == "__main__":
    frappe.init(site="tboindia")
    frappe.connect()
    check()
    frappe.destroy()
