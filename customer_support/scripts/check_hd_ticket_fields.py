import frappe

def execute():
    """Check HD Ticket fields to see what's available for notifications"""
    print("🔍 Checking HD Ticket DocType fields...")
    
    try:
        # Get HD Ticket DocType
        doctype_meta = frappe.get_meta("HD Ticket")
        
        print(f"📋 HD Ticket fields:")
        for field in doctype_meta.fields:
            if field.fieldtype in ["Link", "Data", "Small Text"]:
                print(f"   - {field.fieldname}: {field.label} ({field.fieldtype})")
        
        # Get a sample ticket to see actual field values
        tickets = frappe.get_all("HD Ticket", limit=1)
        if tickets:
            ticket = frappe.get_doc("HD Ticket", tickets[0].name)
            print(f"\n📄 Sample ticket {ticket.name} fields:")
            
            important_fields = [
                'name', 'subject', 'owner', 'contact', 'contact_email', 
                'customer', 'custom_assigned_to', 'status', 'raised_by'
            ]
            
            for field in important_fields:
                value = getattr(ticket, field, 'Not Found')
                print(f"   {field}: {value}")
                
        print(f"\n📊 All ticket attributes:")
        if tickets:
            for attr in sorted(dir(ticket)):
                if not attr.startswith('_') and not callable(getattr(ticket, attr)):
                    try:
                        value = getattr(ticket, attr)
                        if value and str(value).strip():
                            print(f"   {attr}: {value}")
                    except:
                        pass
                        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()