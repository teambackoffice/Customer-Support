#!/usr/bin/env python3

"""
Script to create email templates for the notification system
"""

import frappe
import json


def create_email_templates():
    """Create email templates manually"""
    
    templates = [
        {
            "name": "HD Ticket - New Ticket",
            "subject": "New Support Ticket: {{ doc.name }} - {{ doc.subject }}",
            "response": """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
    <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #2c3e50; margin: 0; font-size: 24px;">New Support Ticket Created</h2>
        </div>
        
        <div style="background-color: #e8f4fd; padding: 15px; border-left: 4px solid #3498db; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 16px; color: #2c3e50;"><strong>Ticket ID:</strong> {{ doc.name }}</p>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; width: 30%; color: #7f8c8d; font-weight: bold;">Subject:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #2c3e50;">{{ doc.subject }}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #7f8c8d; font-weight: bold;">Status:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #2c3e50;">{{ doc.status }}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #7f8c8d; font-weight: bold;">Priority:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #2c3e50;">{{ doc.priority or 'Medium' }}</td>
            </tr>
        </table>
        
        {% if doc.description %}
        <div style="margin-bottom: 20px;">
            <h4 style="color: #2c3e50; margin-bottom: 10px;">Description:</h4>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; border: 1px solid #e9ecef;">
                {{ doc.description | safe }}
            </div>
        </div>
        {% endif %}
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
            <p style="margin: 0; color: #7f8c8d; font-size: 14px;">
                Thank you for contacting our support team!
            </p>
        </div>
    </div>
</div>""",
            "use_html": 1
        },
        {
            "name": "HD Ticket - Escalation",
            "subject": "ESCALATION: Agent replied to ticket {{ doc.name }} - {{ doc.subject }}",
            "response": """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
    <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #e74c3c; margin: 0; font-size: 24px;">🚨 TICKET ESCALATION</h2>
            <p style="color: #7f8c8d; margin: 5px 0 0 0;">Agent has replied to this ticket</p>
        </div>
        
        <div style="background-color: #ffeaa7; padding: 15px; border-left: 4px solid #fdcb6e; margin-bottom: 20px; border-radius: 4px;">
            <p style="margin: 0; font-size: 16px; color: #2c3e50;"><strong>⚠️ Ticket ID:</strong> {{ doc.name }}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #636e72;">Status changed from Open to Replied - escalation notification triggered.</p>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background-color: #fab1a0;">
                <td style="padding: 12px; border-bottom: 1px solid #e17055; width: 30%; color: #2c3e50; font-weight: bold;">Subject:</td>
                <td style="padding: 12px; border-bottom: 1px solid #e17055; color: #2c3e50; font-weight: bold;">{{ doc.subject }}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #7f8c8d; font-weight: bold;">Status:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #e74c3c; font-weight: bold;">{{ doc.status }}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #7f8c8d; font-weight: bold;">Status Change:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #e74c3c; font-weight: bold;">Open → {{ doc.status }}</td>
            </tr>
        </table>
        
        <div style="background-color: #ffe8e8; padding: 15px; border-radius: 4px; margin-top: 20px; border: 1px solid #ffabab;">
            <p style="margin: 0; color: #2c3e50; font-size: 14px;">
                <strong>🔥 ESCALATION TRIGGERED:</strong><br>
                This ticket status has changed from Open to Replied. Please review the agent's response and take any necessary follow-up actions.
            </p>
        </div>
    </div>
</div>""",
            "use_html": 1
        },
        {
            "name": "HD Ticket - Resolved",
            "subject": "✅ Ticket Resolved: {{ doc.name }} - {{ doc.subject }}",
            "response": """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
    <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #27ae60; margin: 0; font-size: 24px;">✅ Ticket Resolved</h2>
            <p style="color: #7f8c8d; margin: 5px 0 0 0;">Your support request has been resolved</p>
        </div>
        
        <div style="background-color: #d5f4e6; padding: 15px; border-left: 4px solid #27ae60; margin-bottom: 20px; border-radius: 4px;">
            <p style="margin: 0; font-size: 16px; color: #2c3e50;"><strong>✓ Ticket ID:</strong> {{ doc.name }}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #636e72;">Status updated to: <strong style="color: #27ae60;">Resolved</strong></p>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; width: 30%; color: #7f8c8d; font-weight: bold;">Subject:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #2c3e50;">{{ doc.subject }}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #7f8c8d; font-weight: bold;">Status:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #27ae60; font-weight: bold;">{{ doc.status }}</td>
            </tr>
        </table>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
            <p style="margin: 0; color: #7f8c8d; font-size: 14px;">
                Thank you for using our support services!
            </p>
        </div>
    </div>
</div>""",
            "use_html": 1
        }
    ]
    
    created_count = 0
    
    for template_info in templates:
        template_name = template_info.get("name")
        
        if not frappe.db.exists("Email Template", template_name):
            try:
                # Create new email template
                template = frappe.new_doc("Email Template")
                
                # Set fields from template data
                template.name = template_info.get("name")
                template.subject = template_info.get("subject")
                template.response = template_info.get("response")
                template.use_html = template_info.get("use_html", 1)
                template.owner = "Administrator"
                
                # Insert the template
                template.insert(ignore_permissions=True)
                created_count += 1
                
                print(f"✅ Created email template: {template_name}")
                
            except Exception as e:
                print(f"❌ Error creating template '{template_name}': {str(e)}")
        else:
            print(f"✅ Email template already exists: {template_name}")
    
    if created_count > 0:
        frappe.db.commit()
        print(f"\n🎉 Successfully created {created_count} email templates!")
    else:
        print("\n✅ All email templates already exist")


def main():
    """Main function"""
    print("📧 Creating Email Templates for Notification System...")
    print("=" * 55)
    create_email_templates()


if __name__ == "__main__":
    main()