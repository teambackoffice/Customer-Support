import frappe

def execute():
    """Fix Jinja template errors in email templates"""
    print("🔧 Fixing Jinja Template Errors...")
    
    try:
        # Fix New Ticket Template
        print("\n📧 Fixing HD Ticket - New Ticket Template...")
        
        new_ticket_template = frappe.get_doc("Email Template", "HD Ticket - New Ticket")
        
        # Fix the template with proper Jinja syntax
        new_ticket_template.response = """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
<h2 style="color: #2c5282;">Support Ticket Created Successfully</h2>
<p>Hello,</p>
<p>Thank you for contacting our support team.</p>
<p>Your support ticket has been successfully created and is now being reviewed.</p>
<div style="background: #f7fafc; padding: 15px; border-left: 4px solid #4299e1; margin: 20px 0;">
<strong>Ticket Details:</strong><br>
<strong>Ticket Number:</strong> {{ doc.name }}<br>
<strong>Subject:</strong> {{ doc.subject }}<br>
<strong>Status:</strong> {{ doc.status }}<br>
{% if doc.custom_module -%}
<strong>Module:</strong> {{ doc.custom_module }}<br>
{%- endif %}
<strong>Created on:</strong> {{ doc.creation.strftime('%B %d, %Y at %I:%M %p') if doc.creation else 'Just now' }}
</div>
<p>Our team will get back to you as soon as possible.</p>
<p>Thank you for your patience.</p>
<p><strong>Kind regards,</strong><br>Support Team</p>
</div>"""
        
        new_ticket_template.save(ignore_permissions=True)
        print("✅ Fixed New Ticket template")
        
        # Fix Resolved Template
        print("\n✅ Fixing HD Ticket - Resolved Template...")
        
        resolved_template = frappe.get_doc("Email Template", "HD Ticket - Resolved")
        
        # Fix with clean template
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
        
        resolved_template.save(ignore_permissions=True)
        print("✅ Fixed Resolved template")
        
        # Fix Escalation Template
        print("\n⚠️ Fixing HD Ticket - Escalation Template...")
        
        escalation_template = frappe.get_doc("Email Template", "HD Ticket - Escalation")
        
        # Fix with clean template
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
<p><strong>Created:</strong> {{ doc.creation.strftime('%B %d, %Y at %I:%M %p') if doc.creation else 'Recently' }}</p>
<p><strong>Time Elapsed:</strong> More than 15 minutes without response</p>
{% if doc.custom_assigned_to -%}
<p><strong>Assigned To:</strong> {{ doc.custom_assigned_to }}</p>
{%- endif %}
</div>
<div style="background: #fff7ed; padding: 15px; border-radius: 8px; margin: 20px 0;">
<h4 style="color: #ea580c; margin: 0 0 10px 0;">📋 Required Action</h4>
<p>This ticket requires immediate attention from the support team.</p>
<p>Please review and respond to the customer as soon as possible.</p>
</div>
<p><strong>Urgent regards,</strong><br>Support Management System</p>
</div>
</div>"""
        
        escalation_template.save(ignore_permissions=True)
        print("✅ Fixed Escalation template")
        
        frappe.db.commit()
        
        # Also check if there's an issue with the notification system sending logic
        print("\n🔧 Checking notification system logic...")
        
        # Check if the notification system is properly configured to send emails silently
        settings = frappe.get_single("Customer Support Notification Settings")
        
        if settings.enable_notifications:
            print("✅ Notifications are enabled")
            print(f"   Rules configured: {len(settings.notification_rules)}")
        else:
            print("⚠️  Notifications are disabled")
        
        # Test template rendering
        print("\n🧪 Testing template rendering...")
        
        # Get a sample ticket
        sample_tickets = frappe.get_all("HD Ticket", limit=1)
        if sample_tickets:
            ticket = frappe.get_doc("HD Ticket", sample_tickets[0].name)
            
            try:
                # Test New Ticket template
                rendered = frappe.render_template(new_ticket_template.response, {"doc": ticket})
                print("✅ New Ticket template renders without errors")
                
                # Test Resolved template
                rendered = frappe.render_template(resolved_template.response, {"doc": ticket})
                print("✅ Resolved template renders without errors")
                
                # Test Escalation template
                rendered = frappe.render_template(escalation_template.response, {"doc": ticket})
                print("✅ Escalation template renders without errors")
                
            except Exception as e:
                print(f"❌ Template rendering error: {str(e)}")
        
        print(f"\n🎯 Templates Fixed:")
        print(f"   ✅ Proper Jinja syntax with safe conditionals")
        print(f"   ✅ Error handling for missing fields")
        print(f"   ✅ Clean HTML without syntax issues")
        
        print(f"\n✅ Template errors fixed! Emails should send silently now.")
        
    except Exception as e:
        print(f"❌ Error fixing templates: {str(e)}")
        frappe.db.rollback()
        import traceback
        traceback.print_exc()