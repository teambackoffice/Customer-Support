import frappe

def execute():
    """Update Resolved and Escalation email templates with professional HTML"""
    print("📧 Updating Resolved and Escalation Email Templates...")
    
    try:
        # Update Resolved Template
        print("\n🟢 Updating HD Ticket - Resolved Template...")
        
        resolved_template_name = "HD Ticket - Resolved"
        
        if frappe.db.exists("Email Template", resolved_template_name):
            resolved_template = frappe.get_doc("Email Template", resolved_template_name)
            print(f"✅ Found existing resolved template")
        else:
            print(f"⚠️  Resolved template not found, creating new one...")
            resolved_template = frappe.new_doc("Email Template")
            resolved_template.name = resolved_template_name
        
        # Set resolved template content
        resolved_template.subject = "✅ Ticket Resolved - {{ doc.name }}"
        resolved_template.response = """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="background: #d1fae5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
<h2 style="color: #059669; margin: 0;">🎉 Issue Resolved</h2>
<p style="margin: 5px 0 0 0; color: #666;">Ticket #{{ doc.name }}</p>
</div>
<div style="background: white; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
<p><strong>Hello,</strong></p>
<p>We're pleased to inform you that your support issue has been resolved.</p>
<div style="background: #f0fdf4; padding: 15px; border-radius: 8px; margin: 20px 0;">
<h3 style="color: #15803d; margin: 0 0 10px 0;">✅ Resolution Summary</h3>
<p><strong>Ticket:</strong> {{ doc.name }}</p>
<p><strong>Subject:</strong> {{ doc.subject }}</p>
</div>
<p>Thank you for using our support services.</p>
<p><strong>Best regards,</strong><br>Support Team</p>
</div>
</div>"""
        
        resolved_template.use_html = 1
        resolved_template.doctype_name = "HD Ticket"
        
        # Save resolved template
        if frappe.db.exists("Email Template", resolved_template_name):
            resolved_template.save(ignore_permissions=True)
        else:
            resolved_template.insert(ignore_permissions=True)
        
        print(f"✅ Resolved template updated successfully")
        
        # Update Escalation Template
        print("\n🔴 Updating HD Ticket - Escalation Template...")
        
        escalation_template_name = "HD Ticket - Escalation"
        
        if frappe.db.exists("Email Template", escalation_template_name):
            escalation_template = frappe.get_doc("Email Template", escalation_template_name)
            print(f"✅ Found existing escalation template")
        else:
            print(f"⚠️  Escalation template not found, creating new one...")
            escalation_template = frappe.new_doc("Email Template")
            escalation_template.name = escalation_template_name
        
        # Set escalation template content (matching style with red/orange theme)
        escalation_template.subject = "⚠️ URGENT: Ticket Escalation - {{ doc.name }}"
        escalation_template.response = """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="background: #fecaca; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
<h2 style="color: #dc2626; margin: 0;">⚠️ Ticket Escalation</h2>
<p style="margin: 5px 0 0 0; color: #666;">Ticket #{{ doc.name }} requires immediate attention</p>
</div>
<div style="background: white; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
<p><strong>Hello,</strong></p>
<p>This ticket has been escalated due to no response within the specified timeframe.</p>
<div style="background: #fef2f2; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ef4444;">
<h3 style="color: #dc2626; margin: 0 0 10px 0;">🚨 Escalation Details</h3>
<p><strong>Ticket:</strong> {{ doc.name }}</p>
<p><strong>Subject:</strong> {{ doc.subject }}</p>
<p><strong>Status:</strong> {{ doc.status }}</p>
<p><strong>Created:</strong> {{ doc.creation.strftime('%B %d, %Y at %I:%M %p') }}</p>
<p><strong>Time Elapsed:</strong> More than 15 minutes without response</p>
{% if doc.custom_assigned_to %}
<p><strong>Assigned To:</strong> {{ doc.custom_assigned_to }}</p>
{% endif %}
</div>
<div style="background: #fff7ed; padding: 15px; border-radius: 8px; margin: 20px 0;">
<h4 style="color: #ea580c; margin: 0 0 10px 0;">📋 Required Action</h4>
<p>This ticket requires immediate attention from the support team.</p>
<p>Please review and respond to the customer as soon as possible.</p>
</div>
<p><strong>Urgent regards,</strong><br>Support Management System</p>
</div>
</div>"""
        
        escalation_template.use_html = 1
        escalation_template.doctype_name = "HD Ticket"
        
        # Save escalation template
        if frappe.db.exists("Email Template", escalation_template_name):
            escalation_template.save(ignore_permissions=True)
        else:
            escalation_template.insert(ignore_permissions=True)
        
        print(f"✅ Escalation template updated successfully")
        
        frappe.db.commit()
        
        # Summary
        print(f"\n📋 Templates Summary:")
        print(f"   ✅ Resolved Template:")
        print(f"      - Green success theme with celebration emoji")
        print(f"      - Professional resolution summary box")
        print(f"      - Clean white content area with borders")
        
        print(f"   ✅ Escalation Template:")
        print(f"      - Red/orange urgent theme with warning emoji")
        print(f"      - Escalation details with time elapsed")
        print(f"      - Required action box for support team")
        print(f"      - Professional urgent styling")
        
        # Test both templates
        print(f"\n🧪 Testing template rendering...")
        
        sample_tickets = frappe.get_all("HD Ticket", limit=1)
        if sample_tickets:
            ticket = frappe.get_doc("HD Ticket", sample_tickets[0].name)
            
            try:
                # Test resolved template
                resolved_render = frappe.render_template(resolved_template.response, {"doc": ticket})
                print(f"✅ Resolved template renders successfully")
                
                # Test escalation template  
                escalation_render = frappe.render_template(escalation_template.response, {"doc": ticket})
                print(f"✅ Escalation template renders successfully")
                
            except Exception as e:
                print(f"⚠️  Template rendering test failed: {str(e)}")
        
        print(f"\n🎯 Email Templates Ready:")
        print(f"   📧 New Ticket: Professional blue theme (already updated)")
        print(f"   ✅ Resolved: Green success theme with celebration")
        print(f"   ⚠️  Escalation: Red urgent theme with warning")
        
        print(f"\n✅ All email templates updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating templates: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()