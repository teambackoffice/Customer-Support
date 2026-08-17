import frappe

def run():
    templates = frappe.get_all('HD Ticket Template', fields=['name'])
    print("Templates:", templates)
    
    if templates:
        for t in templates:
            fields = frappe.get_all('HD Ticket Template Field', filters={'parent': t.name}, fields=['fieldname'])
            print(f"Fields in {t.name}:", [f.fieldname for f in fields])
            
    # Also let's print all custom fields on HD Ticket
    custom_fields = frappe.get_all('Custom Field', filters={'dt': 'HD Ticket'}, fields=['fieldname'])
    print("All Custom Fields on HD Ticket:", [f.fieldname for f in custom_fields])
