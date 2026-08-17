import frappe

def execute():
    """Check available email templates"""
    print("📧 Checking available Email Templates...")
    
    try:
        templates = frappe.get_all("Email Template", fields=["name", "subject"])
        
        print(f"Found {len(templates)} email templates:")
        for template in templates:
            print(f"   - {template.name}: {template.subject}")
        
        # Check specifically for HD Ticket related templates
        hd_templates = [t for t in templates if "hd" in t.name.lower() or "ticket" in t.name.lower()]
        
        if hd_templates:
            print(f"\nHD Ticket related templates:")
            for template in hd_templates:
                print(f"   - {template.name}")
        else:
            print("\n⚠️  No HD Ticket templates found. Need to create them first.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()