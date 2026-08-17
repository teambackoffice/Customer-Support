import frappe

def execute():
    """Show example of how to configure recipients in the UI"""
    print("📋 How to Configure Recipients in Customer Support Notification Settings")
    print("=" * 70)
    
    print("\n1. **Click on the 'New Ticket' row** in Notification Rules table")
    print("2. **Scroll down** to find 'Recipients' section")
    print("3. **Click 'Add Row'** to add recipients")
    print("\n🎯 **Example Recipients Configuration:**")
    
    examples = [
        {
            "purpose": "Send to customer who created the ticket",
            "receiver_by": "Document Field",
            "receiver_type": "To",
            "field_name": "raised_by",
            "note": "Customer's email address"
        },
        {
            "purpose": "Copy the assigned agent",
            "receiver_by": "Document Field", 
            "receiver_type": "CC",
            "field_name": "custom_assigned_to",
            "note": "Agent who handles the ticket"
        },
        {
            "purpose": "Notify support team",
            "receiver_by": "Role",
            "receiver_type": "CC", 
            "role": "Support Team",
            "note": "All users with Support Team role"
        },
        {
            "purpose": "Copy management",
            "receiver_by": "Email",
            "receiver_type": "BCC",
            "email": "management@tboindia.com",
            "note": "Custom email address"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n   **Recipient {i}: {example['purpose']}**")
        print(f"   • Receiver By: {example['receiver_by']}")
        print(f"   • Receiver Type: {example['receiver_type']}")
        
        if 'field_name' in example:
            print(f"   • Field Name: {example['field_name']}")
        if 'role' in example:
            print(f"   • Role: {example['role']}")
        if 'email' in example:
            print(f"   • Email: {example['email']}")
            
        print(f"   • Note: {example['note']}")
    
    print(f"\n🔧 **Available Field Options:**")
    field_options = [
        ("raised_by", "Customer's email who created ticket"),
        ("custom_assigned_to", "Assigned agent/user"),
        ("owner", "Ticket owner/creator"),
        ("contact", "Linked contact email"),
        ("customer", "Linked customer email"),
        ("agent_group", "Team members")
    ]
    
    for field, desc in field_options:
        print(f"   • {field} - {desc}")
    
    print(f"\n📧 **Test the Configuration:**")
    print(f"   1. Save the notification settings")
    print(f"   2. Create a new HD Ticket")
    print(f"   3. Check if emails are sent to configured recipients")
    
    # Show current configuration
    try:
        settings = frappe.get_single("Customer Support Notification Settings")
        
        print(f"\n📋 **Current Configuration:**")
        if settings.notification_rules:
            for rule in settings.notification_rules:
                print(f"   Rule: {rule.notification_type}")
                if hasattr(rule, 'recipients') and rule.recipients:
                    print(f"   Recipients: {len(rule.recipients)} configured")
                    for recipient in rule.recipients:
                        print(f"      • {recipient.receiver_type}: {recipient.receiver_by} → {getattr(recipient, 'field_name', getattr(recipient, 'email_by_role', getattr(recipient, 'email_by_document_field', 'N/A')))}")
                else:
                    print(f"   ⚠️  No recipients configured yet - add them in the UI!")
        
    except Exception as e:
        print(f"   Error checking config: {e}")

if __name__ == "__main__":
    execute()