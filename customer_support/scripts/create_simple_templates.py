import frappe

def execute():
    """Create simple email templates that won't cause Jinja errors"""
    print("📧 Creating Simple Email Templates...")
    
    try:
        # Create simple New Ticket template
        print("\n📧 Creating Simple HD Ticket - New Ticket Template...")
        
        if frappe.db.exists("Email Template", "HD Ticket - New Ticket"):
            template = frappe.get_doc("Email Template", "HD Ticket - New Ticket")
        else:
            template = frappe.new_doc("Email Template")
            template.name = "HD Ticket - New Ticket"
        
        template.subject = "Support Ticket Created: {{ doc.name }}"
        template.response = """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
<h2 style="color: #2c5282;">Support Ticket Created Successfully</h2>
<p>Hello,</p>
<p>Thank you for contacting our support team.</p>
<p>Your support ticket has been successfully created and is now being reviewed.</p>
<div style="background: #f7fafc; padding: 15px; border-left: 4px solid #4299e1; margin: 20px 0;">
<strong>Ticket Details:</strong><br>
<strong>Ticket Number:</strong> {{ doc.name }}<br>
<strong>Subject:</strong> {{ doc.subject }}<br>
<strong>Status:</strong> {{ doc.status }}<br>
<strong>Created on:</strong> {{ doc.creation }}
</div>
<p>Our team will get back to you as soon as possible.</p>
<p>Thank you for your patience.</p>
<p><strong>Kind regards,</strong><br>Support Team</p>
</div>
"""
        template.use_html = 1
        template.doctype_name = "HD Ticket"
        
        if frappe.db.exists("Email Template", "HD Ticket - New Ticket"):
            template.save(ignore_permissions=True)
        else:
            template.insert(ignore_permissions=True)
        
        print("✅ Simple New Ticket template created")
        
        # Create simple Resolved template
        print("\n✅ Creating Simple HD Ticket - Resolved Template...")
        
        if frappe.db.exists("Email Template", "HD Ticket - Resolved"):
            template = frappe.get_doc("Email Template", "HD Ticket - Resolved")
        else:
            template = frappe.new_doc("Email Template")
            template.name = "HD Ticket - Resolved"
        
        template.subject = "Ticket Resolved: {{ doc.name }}"
        template.response = """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="background: #d1fae5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
<h2 style="color: #059669; margin: 0;">Issue Resolved</h2>
<p style="margin: 5px 0 0 0; color: #666;">Ticket {{ doc.name }}</p>
</div>
<div style="background: white; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
<p><strong>Hello,</strong></p>
<p>We're pleased to inform you that your support issue has been resolved.</p>
<div style="background: #f0fdf4; padding: 15px; border-radius: 8px; margin: 20px 0;">
<h3 style="color: #15803d; margin: 0 0 10px 0;">Resolution Summary</h3>
<p><strong>Ticket:</strong> {{ doc.name }}</p>
<p><strong>Subject:</strong> {{ doc.subject }}</p>
</div>
<p>Thank you for using our support services.</p>
<p><strong>Best regards,</strong><br>Support Team</p>
</div>
</div>
"""
        template.use_html = 1
        template.doctype_name = "HD Ticket"
        
        if frappe.db.exists("Email Template", "HD Ticket - Resolved"):
            template.save(ignore_permissions=True)
        else:
            template.insert(ignore_permissions=True)
        
        print("✅ Simple Resolved template created")
        
        # Create simple Escalation template
        print("\n⚠️ Creating Simple HD Ticket - Escalation Template...")
        
        if frappe.db.exists("Email Template", "HD Ticket - Escalation"):
            template = frappe.get_doc("Email Template", "HD Ticket - Escalation")
        else:
            template = frappe.new_doc("Email Template")
            template.name = "HD Ticket - Escalation"
        
        template.subject = "URGENT: Ticket Escalation {{ doc.name }}"
        template.response = """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="background: #fecaca; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
<h2 style="color: #dc2626; margin: 0;">Ticket Escalation</h2>
<p style="margin: 5px 0 0 0; color: #666;">Ticket {{ doc.name }} requires immediate attention</p>
</div>
<div style="background: white; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
<p><strong>Hello,</strong></p>
<p>This ticket has been escalated due to no response within the specified timeframe.</p>
<div style="background: #fef2f2; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ef4444;">
<h3 style="color: #dc2626; margin: 0 0 10px 0;">Escalation Details</h3>
<p><strong>Ticket:</strong> {{ doc.name }}</p>
<p><strong>Subject:</strong> {{ doc.subject }}</p>
<p><strong>Status:</strong> {{ doc.status }}</p>
<p><strong>Created:</strong> {{ doc.creation }}</p>
</div>
<p><strong>Urgent regards,</strong><br>Support Management System</p>
</div>
</div>
"""
        template.use_html = 1
        template.doctype_name = "HD Ticket"
        
        if frappe.db.exists("Email Template", "HD Ticket - Escalation"):
            template.save(ignore_permissions=True)
        else:
            template.insert(ignore_permissions=True)
        
        print("✅ Simple Escalation template created")
        
        frappe.db.commit()
        
        # Re-enable notifications with improved error handling
        print("\n🔄 Re-enabling notifications with improved error handling...")
        
        settings = frappe.get_single("Customer Support Notification Settings")
        settings.enable_notifications = 1
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("✅ Notifications re-enabled")
        
        print(f"\n🎯 Simple Email Templates Ready:")
        print(f"   📧 New Ticket: Basic template with ticket info")
        print(f"   ✅ Resolved: Green theme without complex Jinja") 
        print(f"   ⚠️  Escalation: Red theme with simple fields")
        print(f"   🛡️  Error handling: All errors logged, not shown to users")
        print(f"   📨 Background sending: Emails sent asynchronously")
        
        print(f"\n✅ Notification system should now work without errors!")
        
    except Exception as e:
        print(f"❌ Error creating templates: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()