import frappe

def run():
    tickets = frappe.get_all("HD Ticket", filters={"custom_naming_series": ["like", "TBO%"]}, fields=["name","creation"], order_by="creation asc", limit_page_length=500)
    for t in tickets:
        print(t.creation.strftime("%m-%d %H:%M:%S"), t.name)
