import frappe


def execute():
    """Fix HD Ticket notification module and standard settings."""
    notification_name = "HD Ticket Created - Client Notification"

    if frappe.db.exists("Notification", notification_name):
        notification = frappe.get_doc("Notification", notification_name)
        changed = False

        if notification.is_standard != 0:
            notification.is_standard = 0
            changed = True

        if not getattr(notification, "module", None):
            notification.module = "Customer Support"
            changed = True

        if changed:
            notification.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"✅ Updated Notification: {notification_name}")
        else:
            print(f"✅ Notification already correct: {notification_name}")
    else:
        print(f"⚠️ Notification not found: {notification_name}")
