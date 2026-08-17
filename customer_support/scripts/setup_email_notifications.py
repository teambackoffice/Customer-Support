#!/usr/bin/env python3
"""
Setup Email Notifications for HD Tickets
Creates email template and notification for client acknowledgment
"""

import frappe
import json

def setup_email_notifications():
    """Setup email template and notification for HD Ticket creation"""
    
    try:
        print("🔄 Setting up HD Ticket email notifications...")
        
        # Create Email Template
        create_email_template()
        
        # Create Notification
        create_notification()
        
        frappe.db.commit()
        print("\n🎉 Successfully set up email notifications!")
        print("\nWhat was created:")
        print("- Email Template: HD Ticket Acknowledgment")
        print("- Notification: HD Ticket Created - Client Notification")
        print("\nClients will now receive automatic emails when they create support tickets.")
        
    except Exception as e:
        print(f"❌ Error setting up notifications: {str(e)}")
        frappe.db.rollback()
        raise

def create_email_template():
    """Create HD Ticket Acknowledgment email template"""
    
    # Check if template already exists
    if frappe.db.exists("Email Template", "HD Ticket Acknowledgment"):
        print("✅ Email template already exists, updating...")
        template = frappe.get_doc("Email Template", "HD Ticket Acknowledgment")
    else:
        print("🔄 Creating email template...")
        template = frappe.new_doc("Email Template")
        template.name = "HD Ticket Acknowledgment"
    
    template.subject = "Support Ticket Created - {{ doc.name }}"
    template.use_html = 1
    template.enabled = 1
    
    # HTML email content
    template.response_html = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="color: #2c5282; margin: 0 0 10px 0;">Support Ticket Created Successfully</h2>
            <p style="margin: 0; color: #666; font-size: 14px;">Ticket #{{ doc.name }}</p>
        </div>
        
        <div style="background: white; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 20px;">
            <p>Hello,</p>
            
            <p>Thank you for contacting our support team.</p>
            
            <p>Your support ticket has been successfully created and is now being reviewed.</p>
            
            <div style="background: #f7fafc; padding: 15px; border-left: 4px solid #4299e1; margin: 20px 0;">
                <strong>Ticket Details:</strong><br>
                <strong>Ticket Number:</strong> {{ doc.name }}<br>
                <strong>Subject:</strong> {{ doc.subject }}<br>
                <strong>Status:</strong> {{ doc.status }}<br>
                {% if doc.custom_module %}<strong>Module:</strong> {{ doc.custom_module }}<br>{% endif %}
                {% if doc.custom_reference_document and doc.custom_reference_document_name %}
                <strong>Related to:</strong> {{ doc.custom_reference_document }} - {{ doc.custom_reference_document_name }}<br>
                {% endif %}
                <strong>Created on:</strong> {{ doc.creation.strftime('%B %d, %Y at %I:%M %p') }}
            </div>
            
            <p>Our team will get back to you as soon as possible.</p>
            
            <p>You can track the status of your ticket by logging into your account or by referencing ticket number <strong>{{ doc.name }}</strong> in any future communications.</p>
            
            <p>Thank you for your patience.</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; font-size: 12px; color: #666; text-align: center;">
            <p style="margin: 0;"><strong>Kind regards,</strong><br>Support Team</p>
            <p style="margin: 10px 0 0 0;">This is an automated message. Please do not reply directly to this email.</p>
        </div>
    </div>
    """
    
    # Plain text version
    template.response = """Hello,

Thank you for contacting our support team.

Your support ticket has been successfully created and is now being reviewed.

Ticket Details:
- Ticket Number: {{ doc.name }}
- Subject: {{ doc.subject }}
- Status: {{ doc.status }}
{% if doc.custom_module %}- Module: {{ doc.custom_module }}{% endif %}
{% if doc.custom_reference_document and doc.custom_reference_document_name %}- Related to: {{ doc.custom_reference_document }} - {{ doc.custom_reference_document_name }}{% endif %}
- Created on: {{ doc.creation.strftime('%B %d, %Y at %I:%M %p') }}

Our team will get back to you as soon as possible.

You can track the status of your ticket by referencing ticket number {{ doc.name }} in any future communications.

Thank you for your patience.

Kind regards,
Support Team

---
This is an automated message. Please do not reply directly to this email."""
    
    template.save()
    print("✅ Email template created/updated")

def create_notification():
    """Create notification for HD Ticket creation"""
    
    # Check if notification already exists
    if frappe.db.exists("Notification", "HD Ticket Created - Client Notification"):
        print("✅ Notification already exists, updating...")
        notification = frappe.get_doc("Notification", "HD Ticket Created - Client Notification")
    else:
        print("🔄 Creating notification...")
        notification = frappe.new_doc("Notification")
        notification.name = "HD Ticket Created - Client Notification"
    
    notification.subject = "Support Ticket Created - {{ doc.name }}"
    notification.document_type = "HD Ticket"
    notification.event = "New"
    notification.enabled = 1
    notification.send_to_all_assignees = 0
    notification.is_standard = 0  # Non-standard notification avoids module/template loading
    notification.module = "Customer Support"
    notification.channel = "Email"
    notification.email_template = "HD Ticket Acknowledgment"
    notification.condition = "doc.raised_by"
    notification.message = "Your support ticket {{ doc.name }} has been created successfully."
    notification.attach_print = 0
    notification.send_system_notification = 1
    # Don't set module to avoid the error
    
    # Clear existing recipients and add new one
    notification.recipients = []
    notification.append("recipients", {
        "receiver_by_document_field": "raised_by"
    })
    
    notification.save()
    print("✅ Notification created/updated")

if __name__ == "__main__":
    setup_email_notifications()