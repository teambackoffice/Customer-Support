import frappe
from datetime import datetime, timedelta
from frappe.utils import getdate


@frappe.whitelist()
def get_ticket_summary():
    statuses = ["Open", "Resolved", "Closed"]
    priorities = ["Urgent", "High", "Medium", "Low"]

    status_counts = {
        status: frappe.db.count("HD Ticket", {"status": status})
        for status in statuses
    }

    open_priority_counts = {
        priority: frappe.db.count("HD Ticket", {"status": "Open", "priority": priority})
        for priority in priorities
    }

    today = getdate()
    yesterday = today - timedelta(days=1)
    start_of_month = datetime(today.year, today.month, 1)

    open_delta = frappe.db.count(
        "HD Ticket",
        {
            "status": "Open",
            "creation": [">=", datetime.combine(yesterday, datetime.min.time())],
        },
    )

    resolved_delta = frappe.db.count(
        "HD Ticket",
        {
            "status": "Resolved",
            "creation": [">=", datetime.combine(yesterday, datetime.min.time())],
        },
    )

    closed_this_month = frappe.db.count(
        "HD Ticket",
        {
            "status": "Closed",
            "creation": [">=", start_of_month],
        },
    )

    total_closed = frappe.db.count("HD Ticket", {"status": "Closed"})
    queue_total = sum(open_priority_counts.values()) or status_counts.get("Open", 0)
    return {
        "status_counts": status_counts,
        "status_deltas": {
            "Open": open_delta,
            "Resolved": resolved_delta,
            "Closed": 0,
        },
        "closed_this_month": closed_this_month,
        "total_closed": total_closed,
        "priority_counts": open_priority_counts,
        "ticket_queue": queue_total,
    }
