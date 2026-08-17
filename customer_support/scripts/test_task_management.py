#!/usr/bin/env python3
"""
Test Task Management System
Validates the Task creation and Extra Hour Request system
"""

import frappe


def test_task_management():
    """Test the complete task management workflow"""
    print("🧪 Testing Task Management System...")
    
    # Test 1: Check if DocTypes exist
    print("\n1. 📋 Checking DocTypes...")
    doctypes_to_check = ["HD Ticket", "Task", "Extra Hour Request"]
    
    for doctype in doctypes_to_check:
        if frappe.db.exists("DocType", doctype):
            print(f"   ✓ {doctype} exists")
        else:
            print(f"   ✗ {doctype} missing")
            return False
    
    # Test 2: Check custom fields
    print("\n2. 🔧 Checking Custom Fields...")
    
    # HD Ticket fields
    hd_ticket_fields = ["custom_related_task"]
    for field in hd_ticket_fields:
        if frappe.db.exists("Custom Field", {"dt": "HD Ticket", "fieldname": field}):
            print(f"   ✓ HD Ticket.{field}")
        else:
            print(f"   ✗ HD Ticket.{field} missing")
    
    # Task fields  
    task_fields = ["custom_hd_ticket", "custom_allocated_hours", "custom_extra_approved_hours", "custom_total_hours"]
    for field in task_fields:
        if frappe.db.exists("Custom Field", {"dt": "Task", "fieldname": field}):
            print(f"   ✓ Task.{field}")
        else:
            print(f"   ✗ Task.{field} missing")
    
    # Test 3: Check roles
    print("\n3. 👥 Checking Roles...")
    roles_to_check = ["Support Employee", "Support Manager"]
    
    for role in roles_to_check:
        if frappe.db.exists("Role", role):
            print(f"   ✓ {role} role exists")
        else:
            print(f"   ⚠ {role} role missing - will be created automatically")
    
    # Test 4: Check JavaScript files
    print("\n4. 📄 Checking JavaScript Files...")
    js_files = [
        "customer_support/public/js/hd_ticket.js",
        "customer_support/public/js/task_extra_hours.js"
    ]
    
    import os
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"   ✓ {js_file}")
        else:
            print(f"   ✗ {js_file} missing")
    
    # Test 5: Check whitelisted methods
    print("\n5. 🔗 Checking API Methods...")
    methods_to_check = [
        "customer_support.customer_support.doctype.task.task.create_task_from_hd_ticket",
        "customer_support.customer_support.doctype.extra_hour_request.extra_hour_request.create_extra_hour_request"
    ]
    
    for method in methods_to_check:
        # Check if method exists in the module
        try:
            module_path, function_name = method.rsplit(".", 1)
            module = frappe.get_module(module_path)
            if hasattr(module, function_name):
                print(f"   ✓ {method}")
            else:
                print(f"   ✗ {method} not found")
        except Exception as e:
            print(f"   ✗ {method} - Error: {str(e)}")
    
    print("\n✅ Task Management System validation completed!")
    print("\n📋 Next Steps:")
    print("1. Run: bench migrate")  
    print("2. Execute: customer_support/scripts/setup_task_management.py")
    print("3. Assign Support Employee and Support Manager roles to users")
    print("4. Test by creating an HD Ticket and following the workflow")
    
    return True


if __name__ == "__main__":
    test_task_management()