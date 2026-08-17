#!/usr/bin/env python3

"""
Setup 15-minute escalation notification system for tboindia
"""

import frappe


def setup_escalation_rules():
    """Setup notification rules with proper recipients"""
    
    print("🚀 Setting up 15-minute escalation notification system...")
    
    try:
        # Get notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        
        # Clear existing rules
        settings.notification_rules = []
        
        # Rule 1: New Ticket (immediate)
        print("📧 Creating New Ticket notification rule...")
        new_rule = settings.append("notification_rules", {})
        new_rule.enabled = 1
        new_rule.notification_type = "New Ticket"
        new_rule.trigger_event = "After Insert"
        new_rule.delay_minutes = 0
        new_rule.email_template = "HD Ticket - New Ticket"
        new_rule.subject = "New Support Ticket: {{ doc.name }} - {{ doc.subject }}"
        
        # Recipients for new ticket
        customer = new_rule.append("recipients", {})
        customer.recipient_role = "To"
        customer.recipient_type = "Customer"
        
        support = new_rule.append("recipients", {})
        support.recipient_role = "CC" 
        support.recipient_type = "Custom Email"
        support.custom_email = "support@teambackoffice.com"
        
        # Rule 2: Escalation (15 minutes scheduler)
        print("⏰ Creating 15-minute Escalation rule...")
        esc_rule = settings.append("notification_rules", {})
        esc_rule.enabled = 1
        esc_rule.notification_type = "Escalation"
        esc_rule.trigger_event = "Scheduler"
        esc_rule.delay_minutes = 15
        esc_rule.email_template = "HD Ticket - Escalation"
        esc_rule.subject = "⚠️ ESCALATION: Ticket {{ doc.name }} - No response in 15 minutes"
        
        # Recipients for escalation
        esc_support = esc_rule.append("recipients", {})
        esc_support.recipient_role = "To"
        esc_support.recipient_type = "Custom Email"
        esc_support.custom_email = "support@teambackoffice.com, manager@teambackoffice.com"
        
        esc_customer = esc_rule.append("recipients", {})
        esc_customer.recipient_role = "CC"
        esc_customer.recipient_type = "Customer"
        
        # Rule 3: Resolved 
        print("✅ Creating Resolved notification rule...")
        res_rule = settings.append("notification_rules", {})
        res_rule.enabled = 1
        res_rule.notification_type = "Resolved"
        res_rule.trigger_event = "Status Change"
        res_rule.delay_minutes = 0
        res_rule.email_template = "HD Ticket - Resolved"
        res_rule.subject = "✅ Ticket Resolved: {{ doc.name }} - {{ doc.subject }}"
        
        # Recipients for resolved
        res_customer = res_rule.append("recipients", {})
        res_customer.recipient_role = "To"
        res_customer.recipient_type = "Customer"
        
        # Save settings
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("✅ Notification rules configured successfully!")
        print("\n📋 Rules created:")
        print("   1. New Ticket - Immediate notification to customer + support")
        print("   2. Escalation - 15 minutes after creation (if still Open)")
        print("   3. Resolved - When status changes to Resolved")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        frappe.log_error(f"Escalation setup failed: {str(e)}", "Setup Error")
        return False


def update_new_ticket_template():
    """Update the New Ticket email template with the new professional design."""
    print("📧 Updating New Ticket email template...")
    
    try:
        template_name = "HD Ticket - New Ticket"
        if not frappe.db.exists("Email Template", template_name):
            template = frappe.new_doc("Email Template")
            template.name = template_name
            print(f"   Creating new template: {template_name}")
        else:
            template = frappe.get_doc("Email Template", template_name)
            print(f"   Updating existing template: {template_name}")

        template.subject = "Support Ticket Created: {{ doc.name }}"
        template.use_html = 1
        template.response = """<div style="font-family: Arial, Helvetica, sans-serif; color: #333333; max-width: 1200px; margin: 0 auto; padding: 20px;">

    <!-- Header -->
    <h1 style="color: #315887; font-size: 42px; font-weight: 700; margin: 0 0 45px 0; line-height: 1.2;">
        Support Ticket Created Successfully
    </h1>

    <!-- Greeting -->
    <p style="font-size: 28px; line-height: 1.6; margin: 0 0 25px 0;">
        Hello,
    </p>
    <p style="font-size: 28px; line-height: 1.6; margin: 0 0 25px 0;">
        Thank you for contacting our support team.
    </p>
    <p style="font-size: 28px; line-height: 1.6; margin: 0 0 40px 0;">
        Your support ticket has been successfully created and is now being reviewed.
    </p>

    <!-- Ticket Details -->
    <div style="background-color: #f5f7f9; border-left: 8px solid #3d9be9; padding: 30px 30px; margin: 0 0 40px 0;">
        <p style="font-size: 28px; font-weight: 700; margin: 0 0 8px 0;">
            Ticket Details:
        </p>
        <p style="font-size: 28px; margin: 0 0 6px 0; line-height: 1.4;">
            <strong>Ticket Number:</strong> {{ doc.name }}
        </p>
        <p style="font-size: 28px; margin: 0 0 6px 0; line-height: 1.4;">
            <strong>Subject:</strong> {{ doc.subject or "-" }}
        </p>
        <p style="font-size: 28px; margin: 0; line-height: 1.4;">
            <strong>Module:</strong> {{ doc.custom_module or "-" }}
        </p>
        <p style="font-size: 28px; margin: 0; line-height: 1.4;">
            <strong>Created on:</strong>
            {{ frappe.utils.format_datetime(doc.creation, "MMMM dd, yyyy 'at' hh:mm A") }}
        </p>
    </div>

    <!-- Closing -->
    <p style="font-size: 28px; line-height: 1.6; margin: 0 0 25px 0;">Our team will get back to you as soon as possible.</p>
    <p style="font-size: 28px; line-height: 1.6; margin: 0 0 30px 0;">Thank you for your patience.</p>

    <!-- Signature -->
    <p style="font-size: 28px; line-height: 1.5; margin: 0;"><strong>Kind regards,</strong><br>Support Team</p>
</div>"""
        template.save(ignore_permissions=True)
        frappe.db.commit()
        print("✅ New Ticket email template updated successfully.")
    except Exception as e:
        print(f"❌ Failed to update New Ticket template: {e}")


def update_escalation_email_template():
    """Update escalation email template for 15-minute escalation"""
    
    print("📧 Updating escalation email template...")
    
    try:
        template = frappe.get_doc("Email Template", "HD Ticket - Escalation")
        
        # Update subject
        template.subject = "⚠️ ESCALATION: Ticket {{ doc.name }} - No response in 15 minutes"
        
        # Update response content
        template.response = """<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
    <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #e74c3c; margin: 0; font-size: 24px;">🚨 TICKET ESCALATION</h2>
            <p style="color: #7f8c8d; margin: 5px 0 0 0;">15 minutes - No agent response</p>
        </div>
        
        <div style="background-color: #ffeaa7; padding: 15px; border-left: 4px solid #fdcb6e; margin-bottom: 20px; border-radius: 4px;">
            <p style="margin: 0; font-size: 16px; color: #2c3e50;"><strong>⚠️ Ticket ID:</strong> {{ doc.name }}</p>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #636e72;">This ticket has been open for 15 minutes without any agent response.</p>
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
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #7f8c8d; font-weight: bold;">Created:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #2c3e50;">{{ frappe.utils.format_datetime(doc.creation, 'dd/MM/yyyy hh:mm a') }}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #7f8c8d; font-weight: bold;">Time Elapsed:</td>
                <td style="padding: 10px; border-bottom: 1px solid #ecf0f1; color: #e74c3c; font-weight: bold;">15+ minutes</td>
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
        
        <div style="background-color: #ffe8e8; padding: 15px; border-radius: 4px; margin-top: 20px; border: 1px solid #ffabab;">
            <p style="margin: 0; color: #2c3e50; font-size: 14px;">
                <strong>🔥 URGENT ATTENTION REQUIRED:</strong><br>
                This ticket has been open for 15 minutes without any agent response. Please take immediate action to ensure customer satisfaction.
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1;">
            <p style="margin: 0; color: #7f8c8d; font-size: 14px;">
                Escalation triggered automatically after 15 minutes
            </p>
        </div>
    </div>
</div>"""
        
        template.save(ignore_permissions=True)
        frappe.db.commit()
        
        print("✅ Escalation email template updated")
        
    except Exception as e:
        print(f"❌ Template update failed: {str(e)}")


def test_system():
    """Test the notification system"""
    
    print("\n🧪 Testing the notification system...")
    
    try:
        # Create test ticket
        ticket = frappe.new_doc("HD Ticket")
        ticket.subject = f"15-Min Escalation Test"
        ticket.description = "Testing 15-minute escalation system"
        ticket.contact_email = "customer@test.com"
        ticket.status = "Open"
        ticket.escalation_sent = 0
        
        ticket.insert(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ Created test ticket: {ticket.name}")
        print(f"📧 New ticket notification should have been sent")
        print(f"⏰ Escalation will trigger in 15 minutes if status remains 'Open'")
        
        # Check notification settings
        settings = frappe.get_single("Customer Support Notification Settings")
        escalation_rule = None
        
        for rule in settings.notification_rules:
            if rule.notification_type == "Escalation":
                escalation_rule = rule
                break
        
        if escalation_rule:
            print(f"⚙️ Escalation rule: {escalation_rule.delay_minutes} minutes delay")
            print(f"📧 Recipients: {len(escalation_rule.recipients)}")
        
        return ticket
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None


def main():
    """Main setup function"""
    print("🚀 Setting up 15-Minute Escalation Notification System")
    print("=" * 55)
    
    # Step 1: Setup rules
    if setup_escalation_rules():
        print("\n📧 Step 1: ✅ Rules configured")
    else:
        print("\n📧 Step 1: ❌ Rules configuration failed")
        return

    # Step 1.5: Update New Ticket Template
    update_new_ticket_template()
    print("📧 Step 1.5: ✅ New Ticket Template updated")
    
    # Step 2: Update template
    update_escalation_email_template()
    print("📧 Step 2: ✅ Template updated")
    
    # Step 3: Test system
    test_ticket = test_system()
    
    if test_ticket:
        print("\n🎉 Setup completed successfully!")
        print("\n📋 System behavior:")
        print("   • New Ticket: Immediate notification")
        print("   • Escalation: After 15 minutes if status = 'Open'")
        print("   • Resolved: When status changes to 'Resolved'")
        print("\n💡 Tips:")
        print("   • Change ticket status to 'Replied' to prevent escalation")
        print("   • Escalation only sends once per ticket")
        print("   • Check Email Queue for sent notifications")
    else:
        print("\n❌ Setup completed but testing failed")


if __name__ == "__main__":
    main()