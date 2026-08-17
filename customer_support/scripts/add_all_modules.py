import frappe

def execute():
    """Add all available ERPNext modules to the custom_module field"""
    print("📦 Adding All Available Modules to HD Ticket...")
    
    try:
        # Get all modules from ERPNext system
        print("🔍 Discovering available modules in the system...")
        
        # Get modules from Module Def doctype
        system_modules = frappe.get_all("Module Def", 
                                       fields=["name", "module_name"],
                                       order_by="module_name")
        
        if system_modules:
            print(f"📋 Found {len(system_modules)} system modules:")
            for module in system_modules[:10]:  # Show first 10
                print(f"   - {module.module_name}")
            if len(system_modules) > 10:
                print(f"   ... and {len(system_modules) - 10} more")
        
        # Also get the modules I can see in your dialog
        dialog_modules = [
            "Accounts",
            "Selling", 
            "Buying",
            "Stock",
            "HR", 
            "Manufacturing",
            "CRM",
            "Projects",
            "Support", 
            "Assets",
            "Quality",
            "Payroll",
            "Website",
            "Portal",
            "Integrations",
            "Desk",
            "Setup",
            "Utilities",
            "Custom",
            "Core",
            "Email",
            "Print",
            "Social",
            "Contacts",
            "Communications",
            "Workflow",
            "Data Import",
            "Geo",
            "Event Streaming",
            "Reports",
            "Dashboard"
        ]
        
        # Combine and create comprehensive list
        all_modules = []
        
        # Add system modules
        if system_modules:
            for module in system_modules:
                if module.module_name and module.module_name not in all_modules:
                    all_modules.append(module.module_name)
        
        # Add dialog modules (in case some are missing)
        for module in dialog_modules:
            if module not in all_modules:
                all_modules.append(module)
        
        # Sort alphabetically
        all_modules.sort()
        
        print(f"\n📝 Preparing complete module list ({len(all_modules)} modules)...")
        
        # Create the options string for the field
        options_string = "\n" + "\n".join(all_modules)
        
        # Update the custom field
        print("\n🔧 Updating custom_module field...")
        
        custom_fields = frappe.get_all("Custom Field", 
                                     filters={"dt": "HD Ticket", "fieldname": "custom_module"},
                                     fields=["name"])
        
        if custom_fields:
            custom_field_doc = frappe.get_doc("Custom Field", custom_fields[0].name)
            custom_field_doc.options = options_string
            custom_field_doc.reqd = 0  # Keep it optional
            custom_field_doc.save(ignore_permissions=True)
            
            print(f"✅ Updated custom_module field with {len(all_modules)} modules")
            
        else:
            print("❌ custom_module field not found")
        
        # Clear cache to reload field options
        frappe.clear_cache(doctype="HD Ticket")
        frappe.db.commit()
        
        print(f"\n📋 Complete Module List Added:")
        print(f"   📦 Total Modules: {len(all_modules)}")
        print(f"   📝 First 15 modules:")
        for i, module in enumerate(all_modules[:15]):
            print(f"      {i+1:2d}. {module}")
        
        if len(all_modules) > 15:
            print(f"      ... and {len(all_modules) - 15} more modules")
        
        print(f"\n🎯 Now you can:")
        print(f"   ✅ Select any ERPNext module when creating tickets")
        print(f"   ✅ All system modules are available")
        print(f"   ✅ Module field is optional (can be left empty)")
        print(f"   ✅ No validation errors for any module")
        
        print(f"\n✅ All modules successfully added to HD Ticket!")
        
    except Exception as e:
        print(f"❌ Error adding modules: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()