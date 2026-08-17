import frappe

def execute():
    """Fix the custom_module field options in HD Ticket"""
    print("🔧 Fixing Module Field Validation...")
    
    try:
        # Check current custom fields for HD Ticket
        print("📋 Checking HD Ticket custom fields...")
        
        custom_fields = frappe.get_all("Custom Field", 
                                     filters={"dt": "HD Ticket", "fieldname": "custom_module"},
                                     fields=["name", "fieldname", "options", "reqd"])
        
        if custom_fields:
            for field in custom_fields:
                print(f"   Found custom_module field: {field.name}")
                print(f"   Current options: {field.options}")
                print(f"   Required: {field.reqd}")
                
                # Update the custom field options
                custom_field_doc = frappe.get_doc("Custom Field", field.name)
                
                # Set the correct module options
                custom_field_doc.options = "\nHR\nAccounts\nSales\nPurchase\nPayroll\nCRM\nProjects"
                custom_field_doc.reqd = 0  # Make it not required
                
                custom_field_doc.save(ignore_permissions=True)
                print(f"   ✅ Updated custom_module field options")
                
        else:
            print("   No custom_module field found")
        
        # Also check Property Setter for any module validation
        print("\n🔍 Checking Property Setters for module field...")
        
        property_setters = frappe.get_all("Property Setter",
                                        filters={
                                            "doc_type": "HD Ticket",
                                            "field_name": "custom_module"
                                        },
                                        fields=["name", "property", "value"])
        
        if property_setters:
            for ps in property_setters:
                print(f"   Found Property Setter: {ps.name}")
                print(f"   Property: {ps.property} = {ps.value}")
                
                if ps.property == "options":
                    ps_doc = frappe.get_doc("Property Setter", ps.name)
                    ps_doc.value = "\nHR\nAccounts\nSales\nPurchase\nPayroll\nCRM\nProjects"
                    ps_doc.save(ignore_permissions=True)
                    print(f"   ✅ Updated Property Setter options")
        else:
            print("   No Property Setters found for custom_module")
        
        # Check if there are any existing tickets with "Projects" module
        print("\n📊 Checking existing tickets with Projects module...")
        
        projects_tickets = frappe.get_all("HD Ticket",
                                        filters={"custom_module": "Projects"},
                                        fields=["name", "custom_module"])
        
        if projects_tickets:
            print(f"   Found {len(projects_tickets)} tickets with 'Projects' module")
            
            # Update them to be valid
            for ticket in projects_tickets:
                frappe.db.set_value("HD Ticket", ticket.name, "custom_module", "CRM")
                print(f"   Updated ticket {ticket.name} module to 'CRM'")
        else:
            print("   No tickets found with 'Projects' module")
        
        # Clear the DocType cache to reload field definitions
        frappe.clear_cache(doctype="HD Ticket")
        
        frappe.db.commit()
        
        print(f"\n✅ Module Field Fixed:")
        print(f"   📝 Available options: HR, Accounts, Sales, Purchase, Payroll, CRM, Projects")
        print(f"   🔓 Field is now optional (not required)")
        print(f"   🔄 Existing 'Projects' tickets updated to 'CRM'")
        
        print(f"\n🎯 You can now:")
        print(f"   1. Create HD Tickets with any of the valid modules")
        print(f"   2. Leave module field empty if desired")
        print(f"   3. Use 'Projects' as a valid module option")
        
        print(f"\n✅ Module validation error should be resolved!")
        
    except Exception as e:
        print(f"❌ Error fixing module field: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()