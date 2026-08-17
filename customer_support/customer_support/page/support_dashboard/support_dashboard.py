import frappe
from datetime import datetime, timedelta
from frappe.query_builder import DocType
from frappe.query_builder import functions as fn
from frappe.utils import getdate


STATUSES = [
    "Open",
    "Resolved",
    "Closed",
    "Replied",
    "Completed",
    "Out of Scope",
    "Not Completed",
]
PRIORITIES = ["Urgent", "High", "Medium", "Low"]


@frappe.whitelist()
def get_ticket_summary():
    """Return support ticket metrics drawn from the HD Ticket doctype.

    Returns:
        dict: status_counts, status_deltas, closed_this_month, total_closed,
            priority_counts (open tickets by priority) and ticket_queue.
    """
    today = getdate()
    yesterday = today - timedelta(days=1)
    yesterday_start = datetime.combine(yesterday, datetime.min.time())
    start_of_month = datetime(today.year, today.month, 1)

    status_counts = {status: 0 for status in STATUSES}
    for status, count in _count_grouped("HD Ticket", "status"):
        if status in status_counts:
            status_counts[status] = count

    open_priority_counts = {priority: 0 for priority in PRIORITIES}
    for priority, count in _count_grouped(
        "HD Ticket", "priority", {"status": "Open"}
    ):
        if priority in open_priority_counts:
            open_priority_counts[priority] = count

    # New tickets created since yesterday.
    open_delta = frappe.db.count(
        "HD Ticket",
        {"status": "Open", "creation": [">=", yesterday_start]},
    )

    # Tickets whose status changed (resolved/closed) since yesterday.
    resolved_delta = frappe.db.count(
        "HD Ticket",
        {"status": "Resolved", "modified": [">=", yesterday_start]},
    )

    closed_delta = frappe.db.count(
        "HD Ticket",
        {"status": "Closed", "modified": [">=", yesterday_start]},
    )

    closed_this_month = frappe.db.count(
        "HD Ticket",
        {"status": "Closed", "modified": [">=", start_of_month]},
    )

    total_closed = frappe.db.count("HD Ticket", {"status": "Closed"})
    queue_total = status_counts.get("Open", 0)

    return {
        "status_counts": status_counts,
        "status_deltas": {
            "Open": open_delta,
            "Resolved": resolved_delta,
            "Closed": closed_delta,
        },
        "closed_this_month": closed_this_month,
        "total_closed": total_closed,
        "priority_counts": open_priority_counts,
        "ticket_queue": queue_total,
        "top_customers": _top_customers_list(limit=10, days=90),
        "customers": _customer_overview(days=90, limit=20),
    }


def _top_customers_list(limit=10, days=90):
    """Return top customers with priority mix of their open tickets."""
    start = datetime.combine(
        getdate() - timedelta(days=days), datetime.min.time()
    )
    start_30 = datetime.combine(
        getdate() - timedelta(days=30), datetime.min.time()
    )
    rows = frappe.db.sql(
        """
        SELECT
            custom_customer,
            SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END) AS open_count,
            COUNT(*) AS total_count,
            SUM(CASE WHEN status='Open' AND priority='Urgent' THEN 1 ELSE 0 END) AS urgent_count,
            SUM(CASE WHEN status='Open' AND priority='High'   THEN 1 ELSE 0 END) AS high_count,
            SUM(CASE WHEN status='Open' AND priority='Medium' THEN 1 ELSE 0 END) AS medium_count,
            SUM(CASE WHEN status='Open' AND priority='Low'    THEN 1 ELSE 0 END) AS low_count,
            SUM(CASE WHEN status IN ('Resolved','Closed','Completed')
                          AND modified >= %(start_30)s THEN 1 ELSE 0 END) AS resolved_30d,
            AVG(CASE WHEN first_responded_on IS NOT NULL
                     THEN TIMESTAMPDIFF(SECOND, creation, first_responded_on)
                END) AS avg_response_seconds,
            MAX(creation) AS last_ticket
        FROM `tabHD Ticket`
        WHERE custom_customer IS NOT NULL
          AND custom_customer <> ''
          AND creation >= %(start)s
        GROUP BY custom_customer
        ORDER BY open_count DESC, total_count DESC
        LIMIT %(limit)s
        """,
        {"start": start, "start_30": start_30, "limit": int(limit)},
        as_dict=True,
    )

    results = []
    for r in rows:
        cust = r.custom_customer
        total_n = int(r.total_count or 0)
        if total_n >= 100:
            tier = "Enterprise"
        elif total_n >= 30:
            tier = "Growth"
        else:
            tier = "Starter"

        open_n = int(r.open_count or 0)
        urgent_n = int(r.urgent_count or 0)
        resolved_n = int(r.resolved_30d or 0)
        avg_sec = int(r.avg_response_seconds or 0)
        urgent_share = round((urgent_n / open_n) * 100) if open_n else 0

        results.append(
            {
                "customer": cust,
                "initials": _initials(cust),
                "tier": tier,
                "open": open_n,
                "urgent": urgent_n,
                "high": int(r.high_count or 0),
                "medium": int(r.medium_count or 0),
                "low": int(r.low_count or 0),
                "resolved_30d": resolved_n,
                "avg_response": _format_duration(avg_sec) if avg_sec else "—",
                "urgent_share": urgent_share,
                "last_ticket_dt": r.last_ticket.isoformat() if r.last_ticket else None,
            }
        )

    return results


def _customer_overview(days=90, limit=20):
    """Return customer-level ticket activity for the support dashboard table."""
    start_30 = datetime.combine(
        getdate() - timedelta(days=30), datetime.min.time()
    )

    rows = frappe.db.sql(
        """
        SELECT
            custom_customer,
            SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END) AS open_count,
            COUNT(*) AS total_count,
            SUM(CASE WHEN status IN ('Resolved','Closed')
                          AND modified >= %(start_30)s THEN 1 ELSE 0 END) AS resolved_30d,
            SUM(CASE WHEN creation >= %(start_30)s THEN 1 ELSE 0 END) AS total_30d,
            MAX(creation) AS last_ticket,
            AVG(CASE WHEN first_responded_on IS NOT NULL
                     THEN TIMESTAMPDIFF(SECOND, creation, first_responded_on)
                END) AS avg_response_seconds
        FROM `tabHD Ticket`
        WHERE custom_customer IS NOT NULL AND custom_customer <> ''
        GROUP BY custom_customer
        ORDER BY open_count DESC, total_count DESC
        LIMIT %(limit)s
        """,
        {"start_30": start_30, "limit": int(limit)},
        as_dict=True,
    )

    prio_rows = frappe.db.sql(
        """
        SELECT custom_customer, priority
        FROM `tabHD Ticket`
        WHERE status='Open' AND custom_customer IS NOT NULL
              AND custom_customer <> '' AND priority IS NOT NULL
        GROUP BY custom_customer, priority
        """,
        as_dict=True,
    )
    prio_order = {"Urgent": 4, "High": 3, "Medium": 2, "Low": 1}
    worst_weight = {}
    for r in prio_rows:
        w = prio_order.get(r.priority, 0)
        if w > worst_weight.get(r.custom_customer, 0):
            worst_weight[r.custom_customer] = w
    prio_label = {v: k for k, v in prio_order.items()}

    results = []
    for r in rows:
        cust = r.custom_customer
        open_n = int(r.open_count or 0)
        total_n = int(r.total_count or 0)
        resolved_n = int(r.resolved_30d or 0)
        total_30 = int(r.total_30d or 0)
        rate = round((resolved_n / total_30) * 100) if total_30 else 0
        avg_sec = int(r.avg_response_seconds or 0)
        avg_str = _format_duration(avg_sec) if avg_sec else "—"
        last = r.last_ticket

        if total_n >= 100:
            tier = "Enterprise"
        elif total_n >= 30:
            tier = "Growth"
        else:
            tier = "Starter"

        results.append(
            {
                "customer": cust,
                "initials": _initials(cust),
                "tier": tier,
                "priority": prio_label.get(worst_weight.get(cust, 0)),
                "open": open_n,
                "resolved_30d": resolved_n,
                "resolved_rate": rate,
                "avg_response": avg_str,
                "last_ticket_dt": last.isoformat() if last else None,
                "total": total_n,
            }
        )

    return results


def _initials(name):
    parts = (name or "").split()
    return "".join(p[0] for p in parts[:2])[:3] or "?"


def _format_duration(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h {m}m" if m else f"{h}h"
    d = seconds // 86400
    h = (seconds % 86400) // 3600
    return f"{d}d {h}h" if h else f"{d}d"


def _count_grouped(doctype, field, filters=None):
    """Yield (value, count) pairs grouped by `field` on `doctype`."""
    table = DocType(doctype)
    query = (
        frappe.qb.from_(table)
        .select(table[field], fn.Count(table[field]))
        .groupby(table[field])
    )
    if filters:
        for filter_field, filter_value in filters.items():
            query = query.where(table[filter_field] == filter_value)
    for row in query.run():
        if row[0] is not None:
            yield row[0], int(row[1])