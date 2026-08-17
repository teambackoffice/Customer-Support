#!/usr/bin/env python3
"""
Test script for HD Ticket follow-up functionality

This script can be run in Frappe console to test the follow-up ticket creation.

To run in bench console:
    bench --site [your-site] console
    >>> exec(open('test_follow_up.py').read())
"""

import frappe
from frappe.utils import now_datetime


def test_follow_up_functionality():
    """Test the follow-up ticket creation functionality"""
    
    print("\n" + "=" * 80)
    print("HD TICKET FOLLOW-UP FUNCTIONALITY TEST")
    print("=" * 80 + "\n")
    
    # Test 1: Check if follow-up fields exist
    print("Test 1: Checking if follow-up custom fields exist...")
    try:
        meta = frappe.get_meta("HD Ticket")
        
        fields_to_check = [
            "custom_parent_ticket",
            "custom_follow_up_sequence", 
            "custom_is_follow_up"
        ]
        
        all_fields_exist = True
        for field_name in fields_to_check:
            field = meta.get_field(field_name)
            if field:
                print(f"  ✓ {field_name} exists (Type: {field.fieldtype})")
            else:
                print(f"  ✗ {field_name} NOT found")
                all_fields_exist = False
                
        if not all_fields_exist:
            print("\nRUN: bench --site [your-site] migrate")
            return False
            
    except Exception as e:
        print(f"✗ Error checking fields: {str(e)}")
        return False
    
    # Test 2: Check customer field functionality
    print("\nTest 2: Checking customer field...")
    try:
        customer_field = meta.get_field("custom_customer")
        if customer_field:
            print("  ✓ custom_customer field exists")
        else:
            print("  ✗ custom_customer field NOT found")
            
    except Exception as e:
        print(f"  ✗ Error checking customer field: {str(e)}")
    
    # Test 3: Test follow-up naming logic
    print("\nTest 3: Testing follow-up naming logic...")
    try:
        parent_ticket = "TBO05082649"  # Example ticket ID
        
        # Test the follow-up naming function
        from customer_support.customer_support.doctype.hd_ticket.hd_ticket import get_next_follow_up_sequence
        
        sequence = get_next_follow_up_sequence(parent_ticket)
        expected_name = f"{parent_ticket}-R{sequence}"
        
        print(f"  ✓ Next follow-up for {parent_ticket} would be: {expected_name}")
        
    except Exception as e:
        print(f"  ✗ Error testing naming logic: {str(e)}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_follow_up_functionality()