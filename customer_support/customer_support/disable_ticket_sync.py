#!/usr/bin/env python3
"""
Disable the Medservice Ticket Sync Source to stop 401 errors
Run with: bench --site tboindia execute customer_support.disable_ticket_sync.disable_sync
"""

import frappe

def disable_sync():
    """Disable the Medservice ticket sync source"""
    try:
        # Check if the Ticket Sync Source exists
        if frappe.db.exists("Ticket Sync Source", "Medservice"):
            # Disable it
            frappe.db.set_value("Ticket Sync Source", "Medservice", "enabled", 0)
            frappe.db.commit()
            print("✓ Successfully disabled 'Medservice' Ticket Sync Source")
            print("  The 401 authentication errors should stop now.")
        else:
            print("⚠ 'Medservice' Ticket Sync Source not found")
            
        # List all ticket sync sources
        sources = frappe.get_all(
            "Ticket Sync Source",
            fields=["name", "site_name", "site_url", "enabled"],
            order_by="name"
        )
        
        if sources:
            print("\nAll Ticket Sync Sources:")
            print("-" * 80)
            for source in sources:
                status = "✓ ENABLED" if source.enabled else "✗ DISABLED"
                print(f"{status} | {source.name} | {source.site_url}")
        else:
            print("\nNo Ticket Sync Sources found")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        frappe.log_error(frappe.get_traceback(), "Disable Ticket Sync Failed")

if __name__ == "__main__":
    # For direct execution
    frappe.init(site="tboindia")
    frappe.connect()
    disable_sync()
    frappe.destroy()
