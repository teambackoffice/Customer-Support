#!/usr/bin/env python3
"""
Setup Assignment and Estimation Email Notifications
Creates email template and notification for when tickets are assigned with estimation
"""

import frappe

def setup_assignment_notification():
    """Setup email template and notification for HD Ticket assignment with estimation"""
    
    try:
        print("🔄 Setting up HD Ticket assignment notifications...")
        
        # Create Email Template for Assignment
        create_assignment_email_template()
        
        # Create Notification for Assignment
        create_assignment_notification()
        
        frappe.db.commit()
        print("\n🎉 Successfully set up assignment notifications!")
        print("\nWhat was created:")
        print("- Email Template: HD Ticket Assignment Update")
        print("- Notification: HD Ticket Assigned - Client Update")
        print("\nClients will now receive emails when their tickets are assigned with estimated resolution time.")
        
    except Exception as e:
        print(f"❌ Error setting up assignment notifications: {str(e)}")
        frappe.db.rollback()
        raise

def create_assignment_email_template():
    """Create HD Ticket Assignment Update email template"""
    
    # Check if template already exists
    if frappe.db.exists("Email Template", "HD Ticket Assignment Update"):
        print("✅ Assignment email template already exists, updating...")
        template = frappe.get_doc("Email Template", "HD Ticket Assignment Update")
    else:
        print("🔄 Creating assignment email template...")
        template = frappe.new_doc("Email Template")
        template.name = "HD Ticket Assignment Update"
    
    template.subject = "Your Support Ticket Update - {{ doc.name }}"
    template.use_html = 1
    template.enabled = 1
    
    # HTML email content
    template.response_html = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="background: #e6f3ff; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid #0066cc;">
            <h2 style="color: #0066cc; margin: 0 0 10px 0;">Ticket Update - After Analysis</h2>
            <p style="margin: 0; color: #666; font-size: 14px;">Ticket #{{ doc.name }}</p>
        </div>
        
        <div style="background: white; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 20px;">
            <p><strong>Hello,</strong></p>
            
            <p>We have reviewed your support ticket and our team is now working on resolving your issue.</p>
            
            <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #bae6fd;">
                <h3 style="color: #0369a1; margin: 0 0 15px 0;">📋 Stage 2: After Analysis</h3>
                
                <div style="margin-bottom: 15px;">
                    <strong>Status:</strong> We reviewed your issue
                </div>
                
                {% if doc.custom_estimation_hours %}
                <div style="background: #fef3c7; padding: 15px; border-radius: 6px; border-left: 4px solid #f59e0b;">
                    <strong style="color: #92400e;">⏱️ Estimated Resolution Time:</strong><br>
                    <span style="font-size: 18px; font-weight: bold; color: #92400e;">{{ doc.custom_estimation_hours }} Hours</span>
                </div>
                {% endif %}
            </div>
            
            <div style="background: #f7fafc; padding: 15px; border-left: 4px solid #4299e1; margin: 20px 0;">
                <strong>Ticket Details:</strong><br>
                <strong>Ticket Number:</strong> {{ doc.name }}<br>
                <strong>Subject:</strong> {{ doc.subject }}<br>
                <strong>Current Status:</strong> {{ doc.status }}<br>
                {% if doc.custom_module %}<strong>Module:</strong> {{ doc.custom_module }}<br>{% endif %}
                {% if doc.custom_reference_document and doc.custom_reference_document_name %}
                <strong>Related to:</strong> {{ doc.custom_reference_document }} - {{ doc.custom_reference_document_name }}<br>
                {% endif %}
            </div>
            
            <p>Our support team is now working on your request and will provide updates as we progress toward resolution.</p>
            
            <p>If you have any additional information or questions, please reply to this email with your ticket number <strong>{{ doc.name }}</strong>.</p>
            
            <p>Thank you for your patience as we work to resolve your issue.</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; font-size: 12px; color: #666; text-align: center;">
            <p style="margin: 0;"><strong>Best regards,</strong><br>Support Team</p>
            <p style="margin: 10px 0 0 0;">You're receiving this update because you created support ticket {{ doc.name }}.</p>
        </div>
    </div>
    """
    
    # Plain text version
    template.response = """Hello,

We have reviewed your support ticket and our team is now working on resolving your issue.

STAGE 2: AFTER ANALYSIS

Status: We reviewed your issue
{% if doc.custom_estimation_hours %}
Estimated Resolution Time: {{ doc.custom_estimation_hours }} Hours
{% endif %}

Ticket Details:
- Ticket Number: {{ doc.name }}
- Subject: {{ doc.subject }}
- Current Status: {{ doc.status }}
{% if doc.custom_module %}- Module: {{ doc.custom_module }}{% endif %}
{% if doc.custom_reference_document and doc.custom_reference_document_name %}- Related to: {{ doc.custom_reference_document }} - {{ doc.custom_reference_document_name }}{% endif %}

Our support team is now working on your request and will provide updates as we progress toward resolution.

If you have any additional information or questions, please reply to this email with your ticket number {{ doc.name }}.

Thank you for your patience as we work to resolve your issue.

Best regards,
Support Team

---
You're receiving this update because you created support ticket {{ doc.name }}."""
    
    template.save()
    print("✅ Assignment email template created/updated")

def create_assignment_notification():
    """Create notification for HD Ticket assignment with estimation"""
    
    # Check if notification already exists
    if frappe.db.exists("Notification", "HD Ticket Assigned - Client Update"):
        print("✅ Assignment notification already exists, updating...")
        notification = frappe.get_doc("Notification", "HD Ticket Assigned - Client Update")
    else:
        print("🔄 Creating assignment notification...")
        notification = frappe.new_doc("Notification")
        notification.name = "HD Ticket Assigned - Client Update"
    
    notification.subject = "Your Support Ticket Update - {{ doc.name }}"
    notification.document_type = "HD Ticket"
    notification.event = "Value Change"  # Trigger on field changes
    notification.enabled = 1
    notification.send_to_all_assignees = 0
    notification.is_standard = 0  # Avoid module issues
    notification.channel = "Email"
    notification.email_template = "HD Ticket Assignment Update"
    
    # Condition: Send when estimation_hours is filled (we don't need assigned_to anymore)
    notification.condition = "doc.custom_estimation_hours"
    
    # Watch for changes in estimation hours field
    notification.property_value = "custom_estimation_hours"
    
    notification.message = "Your support ticket {{ doc.name }} has been assigned with estimated resolution time."
    notification.attach_print = 0
    notification.send_system_notification = 1
    
    # Clear existing recipients and add new one
    notification.recipients = []
    notification.append("recipients", {
        "receiver_by_document_field": "raised_by"
    })
    
    notification.save()
    print("✅ Assignment notification created/updated")

if __name__ == "__main__":
    setup_assignment_notification()