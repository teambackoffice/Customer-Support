import frappe

def execute():
    """Update the New Ticket email template with the provided HTML"""
    print("📧 Updating HD Ticket - New Ticket Email Template...")
    
    try:
        # Check if the email template exists
        template_name = "HD Ticket - New Ticket"
        
        if frappe.db.exists("Email Template", template_name):
            template = frappe.get_doc("Email Template", template_name)
            print(f"✅ Found existing template: {template_name}")
        else:
            print(f"⚠️  Template not found, creating new one...")
            template = frappe.new_doc("Email Template")
            template.name = template_name
        
        # Update template content
        template.subject = "Support Ticket Created - {{ doc.name }}"
        
        # Set the new HTML template content
        template.response = """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
<h2 style="color: #2c5282;">Support Ticket Created Successfully</h2>
<p>Hello,</p>
<p>Thank you for contacting our support team.</p>
<p>Your support ticket has been successfully created and is now being reviewed.</p>
<div style="background: #f7fafc; padding: 15px; border-left: 4px solid #4299e1; margin: 20px 0;">
<strong>Ticket Details:</strong><br>
<strong>Ticket Number:</strong> {{ doc.name }}<br>
<strong>Subject:</strong> {{ doc.subject }}<br>
<strong>Status:</strong> {{ doc.status }}<br>
{% if doc.custom_module %}<strong>Module:</strong> {{ doc.custom_module }}<br>{% endif %}
<strong>Created on:</strong> {{ doc.creation.strftime('%B %d, %Y at %I:%M %p') }}
</div>
<p>Our team will get back to you as soon as possible.</p>
<p>Thank you for your patience.</p>
<p><strong>Kind regards,</strong><br>Support Team</p>
</div>"""
        
        # Set other template properties
        template.use_html = 1
        template.doctype_name = "HD Ticket"
        
        # Save the template
        if frappe.db.exists("Email Template", template_name):
            template.save(ignore_permissions=True)
            print(f"✅ Updated existing email template")
        else:
            template.insert(ignore_permissions=True)
            print(f"✅ Created new email template")
        
        frappe.db.commit()
        
        print(f"\n📋 Template Details:")
        print(f"   Name: {template.name}")
        print(f"   Subject: {template.subject}")
        print(f"   HTML Format: {template.use_html}")
        print(f"   DocType: {template.doctype_name}")
        
        print(f"\n📝 Template Content Preview:")
        print(f"   - Professional HTML design with blue header")
        print(f"   - Ticket details box with light blue background") 
        print(f"   - Dynamic fields: ticket number, subject, status, module, creation date")
        print(f"   - Conditional module display")
        print(f"   - Professional closing signature")
        
        # Test the template with sample data
        print(f"\n🧪 Testing template rendering...")
        
        # Get a sample ticket to test
        sample_tickets = frappe.get_all("HD Ticket", limit=1)
        if sample_tickets:
            ticket = frappe.get_doc("HD Ticket", sample_tickets[0].name)
            
            try:
                rendered = frappe.render_template(template.response, {"doc": ticket})
                print(f"✅ Template renders successfully")
                print(f"   Sample ticket: {ticket.name}")
                print(f"   Sample subject: {ticket.subject}")
            except Exception as e:
                print(f"⚠️  Template rendering test failed: {str(e)}")
        else:
            print(f"   No sample tickets available for testing")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. The new template is ready for use")
        print(f"   2. Create a new HD Ticket to test the email")
        print(f"   3. Check if notifications are sent with the new design")
        print(f"   4. The template includes professional styling and all ticket details")
        
        print(f"\n✅ New Ticket email template updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating template: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()