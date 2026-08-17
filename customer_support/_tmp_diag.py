import frappe
from customer_support.customer_support.doctype.hd_ticket.hd_ticket import get_next_sequence

def run():
    print("next sequence (fixed code):", get_next_sequence("TBO"))
    bad = frappe.get_all(
        "HD Ticket",
        filters={
            "custom_naming_series": ["like", "TBO%"],
            "custom_is_follow_up": ["!=", 1],
        },
        fields=["name", "custom_naming_series"],
        order_by="creation asc",
        limit_page_length=500,
    )
    corrupted = []
    for t in bad:
        base = t.custom_naming_series
        # expected format TBO + DDMMYY + seq
        seq = base[3+6:]
        if len(seq) != 2:
            corrupted.append((t.creation, t.name, seq))
    print("non-follow-up tickets:", len(bad), "corrupted(seq!=2 digits):", len(corrupted))
    for c in corrupted[:5]:
        print("  ", c)
    print("  ...")
    for c in corrupted[-3:]:
        print("  ", c)
