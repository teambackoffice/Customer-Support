import frappe, re

def run():
    tickets = frappe.get_all(
        "HD Ticket",
        filters=[["custom_naming_series", "like", "TBO%"]],
        fields=["name", "custom_naming_series", "custom_parent_ticket", "custom_is_follow_up", "creation"],
        order_by="creation asc",
        limit_page_length=500,
    )
    corrupted = []
    followups = []
    for t in tickets:
        n = t.name
        if re.search(r"-R\d*$", n):
            followups.append(t)
        else:
            m = re.match(r"^TBO(\d{6})(\d+)$", n)
            if m and len(m.group(2)) != 2:
                corrupted.append(t)
    print("== CORRUPTED REGULAR (%d) ==" % len(corrupted))
    for i, t in enumerate(corrupted, 1):
        print(i, t.creation.strftime("%m-%d %H:%M"), t.name)
    print("== FOLLOW-UPS (%d) ==" % len(followups))
    for t in followups:
        print(t.creation.strftime("%m-%d %H:%M"), t.name, "parent=", t.custom_parent_ticket, "is_fu=", t.custom_is_follow_up)
