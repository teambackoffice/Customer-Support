#!/usr/bin/env python3
"""
Quick diagnostic for Ticket Sync issues
Run with: bench --site tboindia execute customer_support.diagnose_sync.diagnose
"""

import frappe
import requests

def diagnose():
    """Quick diagnostic check"""
    
    if not frappe.db.exists("Ticket Sync Source", "Medservice"):
        print("✗ Ticket Sync Source 'Medservice' not found")
        return
    
    source = frappe.get_doc("Ticket Sync Source", "Medservice")
    
    print("Configuration:")
    print(f"  URL: {source.site_url}")
    print(f"  API Key: {source.api_key[:10] if source.api_key else 'NOT SET'}...")
    print(f"  Enabled: {source.enabled}")
    print()
    
    # Quick connectivity test
    try:
        url = source.site_url.rstrip("/") + "/api/method/frappe.auth.get_logged_user"
        headers = {
            "Authorization": f"token {source.api_key}:{source.get_password('api_secret')}"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print("✓ Connection and authentication working!")
            user = response.json().get("message")
            print(f"  Authenticated as: {user}")
        elif response.status_code == 401:
            print("✗ Authentication FAILED (401)")
            print("  → Regenerate API Key/Secret on source site")
        else:
            print(f"⚠ Unexpected response: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to source site")
        print("  → Check if the site is running")
        print("  → Verify the URL is correct")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    frappe.init(site="tboindia")
    frappe.connect()
    diagnose()
    frappe.destroy()
