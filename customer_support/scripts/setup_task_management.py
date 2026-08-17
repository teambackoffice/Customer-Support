#!/usr/bin/env python3
"""
Setup Task Management System
Installs and configures the Task creation and Extra Hour Request system for HD Tickets
"""

import frappe


def setup_task_management():
    """Main setup function"""
    print("🚀 Setting up Task Management System for HD Tickets...")
    
    # Run migrations to create custom fields
    print("📋 Running migrations...")
    frappe.reload_doctype("HD Ticket")
    frappe.reload_doctype("Task") 
    frappe.reload_doctype("Extra Hour Request")
    
    # Create roles if they don't exist
    print("👥 Setting up roles...")
    create_roles()
    
    # Set up permissions
    print("🔒 Setting up permissions...")
    setup_permissions()
    
    print("✅ Task Management System setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Assign 'Support Employee' role to employees who will create tasks")
    print("2. Assign 'Support Manager' role to managers who will approve extra hours")
    print("3. Ensure employees have the 'custom_company' field set in their User records")
    print("4. Test the workflow by creating an HD Ticket and assigning it to an employee")


def create_roles():
    """Create Support Employee and Support Manager roles"""
    roles = [
        {
            "role_name": "Support Employee",
            "description": "Can create tasks from HD Tickets and request extra hours"
        },
        {
            "role_name": "Support Manager", 
            "description": "Can approve or reject extra hour requests"
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            role = frappe.new_doc("Role")
            role.role_name = role_data["role_name"]
            role.desk_access = 1
            role.is_custom = 1
            role.insert(ignore_permissions=True)
            print(f"   ✓ Created role: {role_data['role_name']}")
        else:
            print(f"   → Role already exists: {role_data['role_name']}")


def setup_permissions():
    """Set up DocType permissions for the new roles"""
    
    # HD Ticket permissions for Support Employee 
    add_permission("HD Ticket", "Support Employee", {
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 0,
        "cancel": 0,
        "amend": 0
    })
    
    # Task permissions for Support Employee
    add_permission("Task", "Support Employee", {
        "read": 1,
        "write": 1, 
        "create": 1,
        "submit": 0,
        "cancel": 0,
        "amend": 0
    })
    
    # Extra Hour Request permissions for Support Employee
    add_permission("Extra Hour Request", "Support Employee", {
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 0,
        "cancel": 0, 
        "amend": 0
    })
    
    # Extra Hour Request permissions for Support Manager (can approve/reject)
    add_permission("Extra Hour Request", "Support Manager", {
        "read": 1,
        "write": 1,
        "create": 1,
        "submit": 0,
        "cancel": 0,
        "amend": 0,
        "delete": 1
    })
    
    print("   ✓ Permissions configured")


def add_permission(doctype, role, permissions):
    """Add permission for a role to a doctype"""
    if not frappe.db.exists("DocPerm", {"parent": doctype, "role": role}):
        perm = frappe.new_doc("DocPerm")
        perm.parent = doctype
        perm.parenttype = "DocType"
        perm.parentfield = "permissions"
        perm.role = role
        
        for perm_name, value in permissions.items():
            setattr(perm, perm_name, value)
            
        perm.insert(ignore_permissions=True)


if __name__ == "__main__":
    setup_task_management()