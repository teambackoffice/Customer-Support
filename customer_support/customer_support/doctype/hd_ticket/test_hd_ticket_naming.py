"""
Test script for HD Ticket custom naming series

This script can be run in Frappe console to test the naming logic.

To run in bench console:
    bench --site [your-site] console
    >>> from customer_support.customer_support.doctype.hd_ticket.test_hd_ticket_naming import test_naming_series
    >>> test_naming_series()
"""

import frappe
from frappe.utils import now_datetime


def test_naming_series():
	"""
	Test the HD Ticket naming series implementation
	"""
	print("\n" + "=" * 80)
	print("HD TICKET NAMING SERIES TEST")
	print("=" * 80 + "\n")

	# Test 1: Check if custom field exists
	print("Test 1: Checking if custom_naming_series field exists...")
	try:
		meta = frappe.get_meta("HD Ticket")
		custom_field = meta.get_field("custom_naming_series")
		if custom_field:
			print("✓ custom_naming_series field exists")
			print(f"  Field Type: {custom_field.fieldtype}")
			print(f"  Label: {custom_field.label}")
		else:
			print("✗ custom_naming_series field NOT found")
			print("  Run: bench --site [your-site] migrate")
			return
	except Exception as e:
		print(f"✗ Error checking field: {str(e)}")
		return

	# Test 2: Check if User has custom_company field
	print("\nTest 2: Checking if User has custom_company field...")
	try:
		user_meta = frappe.get_meta("User")
		company_field = user_meta.get_field("custom_company")
		if company_field:
			print("✓ custom_company field exists in User DocType")
		else:
			print("✗ custom_company field NOT found in User DocType")
			print("  Please create this field manually or via custom field")
			return
	except Exception as e:
		print(f"✗ Error checking User field: {str(e)}")

	# Test 3: Check current user's company
	print("\nTest 3: Checking current user's company assignment...")
	try:
		user = frappe.session.user
		user_doc = frappe.get_doc("User", user)
		if hasattr(user_doc, "custom_company") and user_doc.custom_company:
			print(f"✓ User {user} has company: {user_doc.custom_company}")
			company = frappe.get_doc("Company", user_doc.custom_company)
			print(f"  Company Abbreviation: {company.abbr}")
		else:
			print(f"✗ User {user} does NOT have company assigned")
			print("  Please set custom_company field in User record")
			return
	except Exception as e:
		print(f"✗ Error checking user company: {str(e)}")
		return

	# Test 4: Check existing HD Tickets
	print("\nTest 4: Checking existing HD Tickets...")
	try:
		tickets = frappe.get_all(
			"HD Ticket",
			fields=["name", "custom_naming_series", "creation"],
			order_by="creation desc",
			limit=5,
		)
		if tickets:
			print(f"✓ Found {len(tickets)} recent tickets:")
			for ticket in tickets:
				print(f"  - {ticket.name} | {ticket.custom_naming_series} | {ticket.creation}")
		else:
			print("  No existing tickets found (this is OK for first time)")
	except Exception as e:
		print(f"✗ Error checking tickets: {str(e)}")

	# Test 5: Simulate naming generation
	print("\nTest 5: Simulating naming series generation...")
	try:
		user = frappe.session.user
		user_doc = frappe.get_doc("User", user)
		company = frappe.get_doc("Company", user_doc.custom_company)
		company_abbr = company.abbr
		date_portion = now_datetime().strftime("%d%m%y")

		# Get next sequence
		existing_tickets = frappe.get_all(
			"HD Ticket",
			filters={"custom_naming_series": ["like", f"{company_abbr}%"]},
			fields=["custom_naming_series"],
			order_by="creation desc",
			limit=1,
		)

		if existing_tickets:
			last_naming_series = existing_tickets[0].custom_naming_series
			last_sequence = int(last_naming_series[-2:])
			next_sequence = last_sequence + 1
			print(f"  Last ticket: {last_naming_series}")
			print(f"  Last sequence: {last_sequence}")
		else:
			next_sequence = 1
			print("  No previous tickets for this company")

		simulated_name = f"{company_abbr}{date_portion}{next_sequence:02d}"
		print(f"\n✓ Simulated next ticket name: {simulated_name}")
		print(f"  Company Abbr: {company_abbr}")
		print(f"  Date (DDMMYY): {date_portion}")
		print(f"  Sequence: {next_sequence:02d}")

	except Exception as e:
		print(f"✗ Error simulating naming: {str(e)}")

	# Test 6: Check if hook is registered
	print("\nTest 6: Checking if naming hook is registered...")
	try:
		from customer_support import hooks

		if hasattr(hooks, "doc_events"):
			events = hooks.doc_events
			if "HD Ticket" in events and "autoname" in events["HD Ticket"]:
				print(f"✓ HD Ticket autoname hook registered: {events['HD Ticket']['autoname']}")
			else:
				print("✗ HD Ticket autoname hook NOT found in doc_events")
		else:
			print("✗ doc_events not found in hooks")
	except Exception as e:
		print(f"✗ Error checking hook: {str(e)}")

	print("\n" + "=" * 80)
	print("TEST COMPLETE")
	print("=" * 80 + "\n")

	print("Summary:")
	print("- If all tests passed (✓), you can create HD Tickets")
	print("- If any test failed (✗), follow the instructions shown")
	print("- To create a test ticket, use the HD Ticket form in Desk")
	print("\n")


def get_naming_preview(company_abbr=None):
	"""
	Get a preview of what the next ticket name would be

	Args:
	    company_abbr: Company abbreviation (optional, uses current user's company if not provided)

	Example:
	    >>> from customer_support.customer_support.doctype.hd_ticket.test_hd_ticket_naming import get_naming_preview
	    >>> get_naming_preview()
	    >>> get_naming_preview("HYD")
	"""
	try:
		if not company_abbr:
			user = frappe.session.user
			user_doc = frappe.get_doc("User", user)
			if not hasattr(user_doc, "custom_company") or not user_doc.custom_company:
				print(f"Error: User {user} does not have a company assigned")
				return None
			company = frappe.get_doc("Company", user_doc.custom_company)
			company_abbr = company.abbr

		date_portion = now_datetime().strftime("%d%m%y")

		existing_tickets = frappe.get_all(
			"HD Ticket",
			filters={"custom_naming_series": ["like", f"{company_abbr}%"]},
			fields=["custom_naming_series"],
			order_by="creation desc",
			limit=1,
		)

		if existing_tickets:
			last_naming_series = existing_tickets[0].custom_naming_series
			last_sequence = int(last_naming_series[-2:])
			next_sequence = last_sequence + 1
		else:
			next_sequence = 1

		next_name = f"{company_abbr}{date_portion}{next_sequence:02d}"

		print(f"\nNext HD Ticket name will be: {next_name}")
		print(f"  Company: {company_abbr}")
		print(f"  Date: {date_portion}")
		print(f"  Sequence: {next_sequence:02d}\n")

		return next_name

	except Exception as e:
		print(f"Error generating preview: {str(e)}")
		return None


if __name__ == "__main__":
	# This allows running the test directly
	test_naming_series()
