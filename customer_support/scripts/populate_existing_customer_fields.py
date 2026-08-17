#!/usr/bin/env python3
"""
Populate Customer Field for Existing HD Tickets
Sets the custom_customer field for existing HD Tickets based on user company information
"""

import frappe


def populate_existing_customer_fields():
    """Populate customer field for existing HD Tickets"""
    print("🔄 Populating customer fields for existing HD Tickets...")
    
    try:
        # Get all HD Tickets without customer field set or with empty customer field
        tickets = frappe.get_all("HD Ticket", 
            filters=[
                ["custom_customer", "in", [None, ""]]
            ],
            fields=["name", "owner", "creation", "custom_customer"]
        )
        
        if not tickets:
            print("   ℹ️  No tickets found that need customer field population")
            return
        
        print(f"   📋 Found {len(tickets)} tickets to update")
        
        updated_count = 0
        skipped_count = 0
        
        for ticket in tickets:
            try:
                company_name = None
                
                # Try to get company from ticket owner
                if ticket.owner:
                    company_name = get_company_name_from_user_safe(ticket.owner)
                
                # If no company from owner, try default company
                if not company_name:
                    default_company = frappe.db.get_single_value("Global Defaults", "default_company")
                    if default_company:
                        company_name = frappe.db.get_value("Company", default_company, "company_name")
                
                if company_name:
                    # Update the ticket
                    frappe.db.set_value("HD Ticket", ticket.name, "custom_customer", company_name, update_modified=False)
                    updated_count += 1
                    print(f"   ✓ Updated {ticket.name}: '{company_name}' (Owner: {ticket.owner})")
                else:
                    skipped_count += 1
                    print(f"   ⚠ Skipped {ticket.name}: No company found (Owner: {ticket.owner})")
                    
            except Exception as e:
                skipped_count += 1
                print(f"   ✗ Error updating {ticket.name}: {str(e)}")
        
        # Commit the changes
        frappe.db.commit()
        
        print(f"\n✅ Customer field population completed!")
        print(f"   📊 Updated: {updated_count} tickets")
        print(f"   ⚠️  Skipped: {skipped_count} tickets")
        
        if skipped_count > 0:
            print(f"\n💡 Troubleshooting skipped tickets:")
            print(f"   1. Check if users have 'custom_company' field set")
            print(f"   2. Verify default company is configured in Global Defaults")
            print(f"   3. Check User records for missing company assignments")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Population failed: {str(e)}")
        frappe.log_error(f"Customer Field Population Error: {str(e)}")
        return False


def get_company_name_from_user_safe(user_email):
    """
    Safely get company name from user (for population script)
    
    Args:
        user_email: User email/ID
        
    Returns:
        str: Company name or None if not found
    """
    try:
        if not user_email or user_email == "Guest":
            return None
            
        # Check if user exists
        if not frappe.db.exists("User", user_email):
            return None
            
        # Get user's custom_company
        custom_company = frappe.db.get_value("User", user_email, "custom_company")
        
        if custom_company:
            # Get company name
            company_name = frappe.db.get_value("Company", custom_company, "company_name")
            return company_name
            
        return None
        
    except Exception as e:
        print(f"   Warning: Error getting company for user {user_email}: {str(e)}")
        return None


if __name__ == "__main__":
    populate_existing_customer_fields()