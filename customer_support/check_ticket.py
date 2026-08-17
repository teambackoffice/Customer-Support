import frappe

def check():
    ticket_name = "TBO080826155"
    
    if not frappe.db.exists("HD Ticket", ticket_name):
        print(f"Ticket {ticket_name} not found.")
        return
        
    ticket = frappe.get_doc("HD Ticket", ticket_name)
    print("--- Ticket Details ---")
    print(f"Status: {ticket.status}")
    print(f"Escalation Sent: {ticket.escalation_sent}")
    print(f"Created On: {ticket.creation}")
    print(f"Raised By: {ticket.raised_by}")
    print(f"Assigned To: {ticket.custom_assigned_to if hasattr(ticket, 'custom_assigned_to') else None}")
    
    settings = frappe.get_single("Customer Support Notification Settings")
    print("\n--- Notification Settings ---")
    print(f"Global Enabled: {settings.enable_notifications}")
    
    rule = None
    for r in settings.notification_rules:
        if r.notification_type == "Escalation" and r.trigger_event == "Scheduler" and r.enabled:
            rule = r
            break
            
    if not rule:
        print("No enabled escalation rule found for Scheduler.")
        return
        
    print("\n--- Escalation Rule Details ---")
    escalation_condition = rule.get_escalation_condition() if hasattr(rule, 'get_escalation_condition') else None
    delay_minutes = escalation_condition.get('minutes_threshold', 15) if escalation_condition else (rule.delay_minutes or 15)
    print(f"Delay Minutes: {delay_minutes}")
    
    excluded_statuses = {"Replied", "Resolved", "Closed", "Not Completed", "Completed"}
    print(f"Excluded Statuses: {excluded_statuses}")
    
    print("\n--- Checking Eligibility ---")
    if ticket.status in excluded_statuses:
        print(f"REASON: Status '{ticket.status}' is in the excluded statuses list.")
    elif ticket.escalation_sent:
        print("REASON: Escalation was already sent (escalation_sent = 1).")
    else:
        from frappe.utils import now_datetime, add_to_date
        cutoff_time = add_to_date(now_datetime(), minutes=-delay_minutes)
        if ticket.creation > cutoff_time:
            print(f"REASON: Ticket is not old enough. Created: {ticket.creation}, Cutoff Time: {cutoff_time}")
        else:
            print("Ticket IS eligible based on standard checks.")
            
    print("\n--- Checking Error Logs ---")
    logs = frappe.get_all("Error Log", filters={"creation": [">", ticket.creation], "method": ["like", "%Escalation%"]}, fields=["name", "error", "method"], order_by="creation desc", limit=5)
    for log in logs:
        print(f"Error Log {log.name} ({log.method}):\n{log.error[:200]}...")

    try:
        from customer_support.customer_support.notification_system import NotificationSystem
        recipients = NotificationSystem.build_recipient_list(rule, ticket)
        print(f"\n--- Recipient List ---")
        print(recipients)
        
        all_emails = recipients.get("to", []) + recipients.get("cc", []) + recipients.get("bcc", [])
        if not all_emails:
            print("REASON: No recipients could be found to send the email to.")
    except Exception as e:
        print(f"Error checking recipients: {e}")
