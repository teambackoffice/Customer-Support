"""
Script to add custom fields to HD Ticket DocType

Fields to add:
1. custom_assigned_to - Link to User
2. custom_estimation_hours - Float field for estimated hours

Usage:
    bench --site [your-site] console
    >>> from customer_support.scripts.add_hd_ticket_fields import add_hd_ticket_fields
    >>> add_hd_ticket_fields()
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def add_hd_ticket_fields():
	"""Add custom fields to HD Ticket DocType"""
	print("\n" + "=" * 80)
	print("Adding Custom Fields to HD Ticket")
	print("=" * 80 + "\n")

	try:
		# Check if fields already exist
		hd_ticket_meta = frappe.get_meta("HD Ticket")
		
		assigned_to_exists = hd_ticket_meta.get_field("custom_assigned_to")
		estimation_hours_exists = hd_ticket_meta.get_field("custom_estimation_hours")

		if assigned_to_exists and estimation_hours_exists:
			print("✓ Both fields already exist")
			print(f"  - custom_assigned_to: {assigned_to_exists.fieldtype}")
			print(f"  - custom_estimation_hours: {estimation_hours_exists.fieldtype}")
			return True

		# Create the custom fields
		custom_fields = {
			"HD Ticket": [
				{
					"fieldname": "custom_assigned_to",
					"fieldtype": "Link",
					"options": "User",
					"label": "Assigned To",
					"insert_after": "custom_module",  # Insert after module field
					"description": "User assigned to handle this ticket",
					"in_list_view": 1,
					"in_standard_filter": 1,
					"bold": 0,
					"allow_on_submit": 0,
					"translatable": 0,
				},
				{
					"fieldname": "custom_estimation_hours",
					"fieldtype": "Float",
					"label": "Estimation Hours",
					"insert_after": "custom_assigned_to",
					"description": "Estimated hours to resolve this ticket",
					"in_list_view": 1,
					"in_standard_filter": 0,
					"bold": 0,
					"allow_on_submit": 0,
					"precision": "2",  # 2 decimal places (e.g., 2.50 hours)
					"translatable": 0,
				},
			]
		}

		create_custom_fields(custom_fields, update=True)
		frappe.db.commit()

		print("✓ Custom fields created successfully")
		print("\nFields added:")
		print("  1. custom_assigned_to (Link to User)")
		print("     - Visible in list view")
		print("     - Available in filters")
		print("     - Manual assignment only (no auto-assignment)")
		print()
		print("  2. custom_estimation_hours (Float)")
		print("     - Visible in list view")
		print("     - Precision: 2 decimal places")
		print("     - Examples: 1.50, 2.25, 8.00 hours")
		print()

		print("=" * 80)
		print("NEXT STEPS")
		print("=" * 80)
		print("1. Clear cache: bench --site [site] clear-cache")
		print("2. Restart: bench restart")
		print("3. Test: Create/Edit HD Ticket and verify fields appear")
		print("=" * 80 + "\n")

		return True

	except Exception as e:
		print(f"✗ Error creating fields: {str(e)}")
		import traceback
		traceback.print_exc()
		return False


def remove_hd_ticket_fields():
	"""Remove custom fields from HD Ticket DocType (if needed)"""
	print("\n" + "=" * 80)
	print("Removing Custom Fields from HD Ticket")
	print("=" * 80 + "\n")

	try:
		fields_to_remove = ["custom_assigned_to", "custom_estimation_hours"]
		removed_count = 0

		for fieldname in fields_to_remove:
			# Check if custom field exists
			if frappe.db.exists("Custom Field", {"dt": "HD Ticket", "fieldname": fieldname}):
				custom_field = frappe.get_doc(
					"Custom Field", {"dt": "HD Ticket", "fieldname": fieldname}
				)
				custom_field.delete()
				print(f"✓ Removed: {fieldname}")
				removed_count += 1
			else:
				print(f"  {fieldname} - Not found (already removed or doesn't exist)")

		frappe.db.commit()

		print(f"\n✓ Removed {removed_count} field(s)")
		print("\nRun: bench clear-cache && bench restart")
		print("=" * 80 + "\n")

		return True

	except Exception as e:
		print(f"✗ Error removing fields: {str(e)}")
		import traceback
		traceback.print_exc()
		return False


def show_hd_ticket_fields():
	"""Display current custom fields in HD Ticket"""
	print("\n" + "=" * 80)
	print("HD TICKET CUSTOM FIELDS")
	print("=" * 80 + "\n")

	try:
		custom_fields = frappe.get_all(
			"Custom Field",
			filters={"dt": "HD Ticket"},
			fields=["fieldname", "fieldtype", "label", "options"],
			order_by="idx",
		)

		if not custom_fields:
			print("No custom fields found in HD Ticket")
			return

		print(f"Found {len(custom_fields)} custom field(s):\n")
		print(f"{'Field Name':<35} {'Type':<15} {'Label':<25} {'Options':<20}")
		print("-" * 95)

		for field in custom_fields:
			fieldname = field.fieldname or ""
			fieldtype = field.fieldtype or ""
			label = field.label or ""
			options = field.options or ""

			print(f"{fieldname:<35} {fieldtype:<15} {label:<25} {options:<20}")

		print("\n" + "=" * 80 + "\n")

	except Exception as e:
		print(f"Error: {str(e)}")


if __name__ == "__main__":
	print(__doc__)
	print("\n📚 Available Functions:\n")
	print("1. add_hd_ticket_fields()      - Add custom fields")
	print("2. remove_hd_ticket_fields()   - Remove custom fields")
	print("3. show_hd_ticket_fields()     - Show all custom fields")
	print()
