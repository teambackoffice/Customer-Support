#!/usr/bin/env python3
"""
Test Customer Field Implementation
Validates that the custom_customer field is correctly populated for HD Tickets
"""

import frappe


def test_customer_field_implementation():
    """Test the customer field functionality"""
    print("🧪 Testing Customer Field Implementation...")
    
    try:
        # Test 1: Check if custom field exists
        print("\n1. 📋 Checking Custom Field...")
        
        field_exists = frappe.db.exists("Custom Field", {
            "dt": "HD Ticket",
            "fieldname": "custom_customer"
        })
        
        if field_exists:
            print("   ✓ custom_customer field exists in HD Ticket")
        else:
            print("   ✗ custom_customer field NOT found")
            return False
        
        # Test 2: Check current user's company setup
        print("\n2. 👤 Checking Current User Company Setup...")
        
        current_user = frappe.session.user
        print(f"   Current User: {current_user}")
        
        if current_user and current_user != "Guest":
            user_doc = frappe.get_doc("User", current_user)
            
            has_custom_company = hasattr(user_doc, "custom_company")
            print(f"   Has custom_company field: {has_custom_company}")
            
            if has_custom_company and user_doc.custom_company:
                company_name = frappe.db.get_value("Company", user_doc.custom_company, "company_name")
                print(f"   ✓ User Company: {user_doc.custom_company} ({company_name})")
            else:
                print("   ⚠ User has no company assigned")
                
                # Check default company
                default_company = frappe.db.get_single_value("Global Defaults", "default_company")
                if default_company:
                    default_name = frappe.db.get_value("Company", default_company, "company_name")
                    print(f"   ℹ️ Default Company: {default_company} ({default_name})")
                else:
                    print("   ⚠ No default company configured")
        
        # Test 3: Check existing tickets with customer field
        print("\n3. 📊 Checking Existing Tickets...")
        
        total_tickets = frappe.db.count("HD Ticket")
        tickets_with_customer = frappe.db.count("HD Ticket", {"custom_customer": ["!=", ""]})
        tickets_without_customer = total_tickets - tickets_with_customer
        
        print(f"   Total HD Tickets: {total_tickets}")
        print(f"   ✓ With Customer Field: {tickets_with_customer}")
        print(f"   ⚠ Without Customer Field: {tickets_without_customer}")
        
        if tickets_with_customer > 0:
            # Show some examples
            sample_tickets = frappe.get_all("HD Ticket",
                filters={"custom_customer": ["!=", ""]},
                fields=["name", "custom_customer", "owner"],
                limit=3
            )
            
            print("   Sample tickets with customer field:")
            for ticket in sample_tickets:
                print(f"     - {ticket.name}: '{ticket.custom_customer}' (Owner: {ticket.owner})")
        
        # Test 4: Test the helper functions
        print("\n4. 🔧 Testing Helper Functions...")
        
        try:
            from customer_support.customer_support.doctype.hd_ticket.hd_ticket import get_company_name_from_user
            
            if current_user and current_user != "Guest":
                company_from_function = get_company_name_from_user(current_user)
                print(f"   get_company_name_from_user result: {company_from_function}")
            
            print("   ✓ Helper functions accessible")
            
        except ImportError as e:
            print(f"   ✗ Helper function import error: {str(e)}")
        
        # Test 5: Simulate ticket creation logic
        print("\n5. 🎯 Testing Ticket Creation Logic...")
        
        try:
            # This simulates what happens when a ticket is created
            mock_doc = frappe._dict({
                "name": "TEST-TICKET",
                "owner": current_user,
                "custom_customer": None
            })
            
            # Import the function
            from customer_support.customer_support.doctype.hd_ticket.hd_ticket import set_customer_from_user_company
            
            # Test the function
            set_customer_from_user_company(mock_doc)
            
            if mock_doc.custom_customer:
                print(f"   ✓ Mock ticket customer set to: '{mock_doc.custom_customer}'")
            else:
                print("   ⚠ Mock ticket customer not set")
            
        except Exception as e:
            print(f"   ✗ Ticket creation simulation failed: {str(e)}")
        
        print("\n✅ Customer Field Test completed!")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if tickets_without_customer > 0:
            print("   - Run population script to update existing tickets")
        if current_user == "Guest" or not hasattr(user_doc, "custom_company") or not user_doc.custom_company:
            print("   - Set up user company assignments")
        print("   - Test by creating a new HD Ticket")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        frappe.log_error(f"Customer Field Test Error: {str(e)}")
        return False


def show_user_company_report():
    """Show a report of users and their company assignments"""
    print("\n📋 User Company Assignment Report:")
    
    try:
        users = frappe.get_all("User",
            filters={
                "enabled": 1,
                "user_type": "System User"
            },
            fields=["name", "full_name", "custom_company"]
        )
        
        users_with_company = 0
        users_without_company = 0
        
        for user in users[:10]:  # Show first 10 users
            if user.custom_company:
                company_name = frappe.db.get_value("Company", user.custom_company, "company_name")
                print(f"   ✓ {user.full_name} ({user.name}): {company_name}")
                users_with_company += 1
            else:
                print(f"   ⚠ {user.full_name} ({user.name}): No company assigned")
                users_without_company += 1
        
        if len(users) > 10:
            print(f"   ... and {len(users) - 10} more users")
        
        print(f"\n   Summary: {users_with_company} with company, {users_without_company} without")
        
    except Exception as e:
        print(f"   Error generating report: {str(e)}")


if __name__ == "__main__":
    test_customer_field_implementation()
    show_user_company_report()