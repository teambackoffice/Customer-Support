import frappe
import re


def run():
	frappe.flags.in_test = False

	tickets = frappe.get_all(
		"HD Ticket",
		filters=[["custom_naming_series", "like", "TBO%"]],
		fields=["name", "custom_naming_series", "custom_parent_ticket", "creation"],
		order_by="creation asc",
		limit_page_length=500,
	)

	corrupted = []
	followups = []
	for t in tickets:
		if re.search(r"-R\d*$", t.name):
			followups.append(t)
			continue
		m = re.match(r"^TBO(\d{6})(\d+)$", t.name)
		if m and len(m.group(2)) != 2:
			corrupted.append(t)

	corrupted.sort(key=lambda t: t.creation)

	next_seq = 34
	rename_map = {}
	for t in corrupted:
		date6 = re.match(r"^TBO(\d{6})\d+$", t.name).group(1)
		new_name = f"TBO{date6}{next_seq:02d}"
		rename_map[t.name] = new_name
		next_seq += 1

	print(f"Renaming {len(rename_map)} corrupted tickets (34..{next_seq - 1:02d})")

	for old, new in rename_map.items():
		if frappe.db.exists("HD Ticket", new):
			frappe.throw(f"Target name already exists: {new} (from {old})")
		frappe.rename_doc("HD Ticket", old, new, force=True, show_alert=False)
		frappe.db.set_value("HD Ticket", new, "custom_naming_series", new)
		print(f"  {old} -> {new}")

	fu_renamed = 0
	for t in followups:
		parent_new = rename_map.get(t.custom_parent_ticket)
		if not parent_new:
			continue
		m = re.match(r"^(.*)-R(\d+)$", t.name)
		seq = m.group(2) if m else "1"
		new_fu = f"{parent_new}-R{seq}"
		if frappe.db.exists("HD Ticket", new_fu):
			frappe.throw(f"Follow-up target already exists: {new_fu} (from {t.name})")
		frappe.rename_doc("HD Ticket", t.name, new_fu, force=True, show_alert=False)
		frappe.db.set_value("HD Ticket", new_fu, "custom_naming_series", new_fu)
		print(f"  {t.name} -> {new_fu} (parent {t.custom_parent_ticket} -> {parent_new})")
		fu_renamed += 1

	print(f"Done. {len(rename_map)} regular + {fu_renamed} follow-ups renamed.")
