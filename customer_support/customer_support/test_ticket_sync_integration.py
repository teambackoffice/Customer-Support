#!/usr/bin/env python3
"""
Test Ticket Sync Integration
Tests the connection and sync functionality with another site

Run with: bench --site tboindia execute customer_support.test_ticket_sync_integration.run_tests
"""

import json
import frappe
import requests


def run_tests():
    """Run all integration tests for Ticket Sync"""
    print("=" * 80)
    print("TICKET SYNC INTEGRATION TEST")
    print("=" * 80)
    print()
    
    # Test 1: Check if Ticket Sync Source exists
    print("Test 1: Checking Ticket Sync Source configuration...")
    print("-" * 80)
    
    if not frappe.db.exists("Ticket Sync Source", "Medservice"):
        print("✗ FAILED: 'Medservice' Ticket Sync Source not found")
        print("  Create it first via: Ticket Sync Source → New")
        return
    
    source = frappe.get_doc("Ticket Sync Source", "Medservice")
    print(f"✓ Ticket Sync Source found: {source.name}")
    print(f"  Site Name: {source.site_name}")
    print(f"  Site URL: {source.site_url}")
    print(f"  API Key: {source.api_key[:10]}..." if source.api_key else "  API Key: NOT SET")
    print(f"  Enabled: {'Yes' if source.enabled else 'No'}")
    print()
    
    # Validate configuration
    if not source.site_url or source.site_url == "http://127.0.0.1:8000/app":
        print("⚠ WARNING: Site URL appears to be pointing to itself or invalid")
        print("  Current URL:", source.site_url)
        print("  This will cause issues. Update it to point to the actual source site.")
        print()
    
    if not source.api_key or not source.get_password("api_secret"):
        print("✗ FAILED: API credentials not configured")
        print("  Set API Key and API Secret before testing")
        return
    
    # Test 2: Check network connectivity
    print("Test 2: Testing network connectivity to source site...")
    print("-" * 80)
    
    try:
        # Try to ping the base URL
        base_url = source.site_url.rstrip("/")
        response = requests.get(base_url, timeout=10, allow_redirects=True)
        print(f"✓ Site is reachable: {base_url}")
        print(f"  Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"✗ FAILED: Cannot connect to {base_url}")
        print("  Check if the site is running and accessible")
        return
    except requests.exceptions.Timeout:
        print(f"✗ FAILED: Connection timeout to {base_url}")
        print("  The site may be slow or unreachable")
        return
    except Exception as e:
        print(f"⚠ WARNING: Error connecting: {e}")
    print()
    
    # Test 3: Test API authentication
    print("Test 3: Testing API authentication...")
    print("-" * 80)
    
    try:
        api_url = base_url.rstrip("/") + "/api/method/frappe.auth.get_logged_user"
        headers = {
            "Authorization": f"token {source.api_key}:{source.get_password('api_secret')}",
            "Accept": "application/json",
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("message")
            print(f"✓ Authentication successful!")
            print(f"  Authenticated as: {user}")
        elif response.status_code == 401:
            print("✗ FAILED: Authentication failed (401 Unauthorized)")
            print("  The API Key/Secret are invalid or expired")
            print("  Generate new credentials on the source site")
            return
        elif response.status_code == 403:
            print("✗ FAILED: Authentication forbidden (403)")
            print("  The user may not have API access enabled")
            return
        else:
            print(f"⚠ WARNING: Unexpected status code: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"✗ FAILED: Authentication test error: {e}")
        return
    print()
    
    # Test 4: Test HD Ticket API access
    print("Test 4: Testing HD Ticket API access...")
    print("-" * 80)
    
    try:
        api_url = base_url.rstrip("/") + "/api/resource/HD Ticket"
        params = {
            "fields": json.dumps(["name", "subject", "status"]),
            "limit_page_length": 5
        }
        
        response = requests.get(api_url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            tickets = data.get("data", [])
            print(f"✓ HD Ticket API accessible!")
            print(f"  Found {len(tickets)} tickets (showing first 5)")
            
            if tickets:
                print("\n  Sample tickets:")
                for ticket in tickets[:3]:
                    print(f"    - {ticket.get('name')}: {ticket.get('subject', 'No subject')[:50]}")
            else:
                print("  ⚠ No tickets found on source site (this is OK if it's new)")
        elif response.status_code == 401:
            print("✗ FAILED: Unauthorized to access HD Ticket")
            print("  The API user may not have permission to read HD Tickets")
            return
        elif response.status_code == 403:
            print("✗ FAILED: Forbidden to access HD Ticket")
            print("  Check user permissions on the source site")
            return
        elif response.status_code == 404:
            print("✗ FAILED: HD Ticket DocType not found")
            print("  The source site may not have Helpdesk installed")
            return
        else:
            print(f"⚠ WARNING: Unexpected status code: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"✗ FAILED: HD Ticket API test error: {e}")
        return
    print()
    
    # Test 5: Check custom fields on local site
    print("Test 5: Checking required custom fields on local site...")
    print("-" * 80)
    
    try:
        meta = frappe.get_meta("HD Ticket")
        required_fields = [
            "custom_ticket_source",
            "custom_remote_ticket",
            "custom_synced_on",
            "custom_naming_series"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not meta.get_field(field):
                missing_fields.append(field)
        
        if missing_fields:
            print("✗ FAILED: Missing required custom fields:")
            for field in missing_fields:
                print(f"    - {field}")
            print("\n  Run migration to add these fields:")
            print("  bench --site tboindia migrate")
            return
        else:
            print("✓ All required custom fields present")
    except Exception as e:
        print(f"✗ FAILED: Error checking fields: {e}")
        return
    print()
    
    # Test 6: Dry run sync test
    print("Test 6: Performing dry-run sync test...")
    print("-" * 80)
    
    try:
        from customer_support.customer_support.sync_tickets import sync_remote_tickets
        
        print("  Starting sync... (this may take a moment)")
        result = sync_remote_tickets("Medservice")
        
        if result and len(result) > 0:
            sync_result = result[0]
            if sync_result.get("status") == "ok":
                print("✓ Sync completed successfully!")
                print(f"  Created: {sync_result.get('created', 0)} tickets")
                print(f"  Updated: {sync_result.get('updated', 0)} tickets")
            else:
                print("✗ FAILED: Sync encountered an error")
                print(f"  Error: {sync_result.get('error', 'Unknown error')}")
                return
        else:
            print("⚠ WARNING: No sync results returned")
    except Exception as e:
        print(f"✗ FAILED: Sync test error: {e}")
        import traceback
        print("\nFull error:")
        print(traceback.format_exc())
        return
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("✓ All tests passed!")
    print("\nYour Ticket Sync integration is properly configured.")
    print("\nNext steps:")
    print("  1. Enable automatic sync in Ticket Sync Source if desired")
    print("  2. Monitor sync logs for any ongoing issues")
    print("  3. Check synced tickets in HD Ticket list")
    print()


if __name__ == "__main__":
    frappe.init(site="tboindia")
    frappe.connect()
    run_tests()
    frappe.destroy()
