"""
Script to rearrange HD Ticket form layout
- Organize fields into logical sections
- Keep all fields visible
- Group related fields together

Usage:
    bench --site [your-site] console
    >>> from customer_support.scripts.customize_hd_ticket_form import rearrange_hd_ticket_fields
    >>> rearrange_hd_ticket_fields()
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def rearrange_hd_ticket_fields():
	"""Rearrange HD Ticket form fields for better organization"""
	print("\n" + "=" * 80)
	print("Rearranging HD Ticket Form Fields")
	print("=" * 80 + "\n")

	try:
		doctype = "HD Ticket"
		
		# Define field order with section breaks for logical grouping
		# This creates a clean, organized layout

		# Update custom field positions and add section breaks
		field_arrangements = [
			# Main section - Basic Info
			{
				"fieldname": "section_basic_info",
				"fieldtype": "Section Break",
				"label": "Basic Information",
				"insert_after": "naming_series",
				"collapsible": 0,
			},
			{
				"fieldname": "custom_naming_series",
				"insert_after": "section_basic_info",
				"bold": 1,
				"read_only": 1,
			},
			{
				"fieldname": "subject",
				"insert_after": "custom_naming_series",
			},
			{
				"fieldname": "column_break_basic",
				"fieldtype": "Column Break",
				"insert_after": "subject",
			},
			{
				"fieldname": "status",
				"insert_after": "column_break_basic",
				"bold": 1,
			},
			{
				"fieldname": "priority",
				"insert_after": "status",
			},
			# Assignment section
			{
				"fieldname": "section_assignment",
				"fieldtype": "Section Break",
				"label": "Assignment & Estimation",
				"insert_after": "priority",
				"collapsible": 0,
			},
			{
				"fieldname": "custom_module",
				"insert_after": "section_assignment",
				"bold": 1,
			},
			{
				"fieldname": "custom_assigned_to",
				"insert_after": "custom_module",
			},
			{
				"fieldname": "column_break_assignment",
				"fieldtype": "Column Break",
				"insert_after": "custom_assigned_to",
			},
			{
				"fieldname": "team",
				"insert_after": "column_break_assignment",
			},
			{
				"fieldname": "custom_estimation_hours",
				"insert_after": "team",
			},
			# Description section
			{
				"fieldname": "section_description",
				"fieldtype": "Section Break",
				"label": "Description",
				"insert_after": "custom_estimation_hours",
				"collapsible": 0,
			},
			{
				"fieldname": "description",
				"insert_after": "section_description",
			},
			# Additional Info section
			{
				"fieldname": "section_additional",
				"fieldtype": "Section Break",
				"label": "Additional Information",
				"insert_after": "description",
				"collapsible": 1,  # Collapsible to keep form clean
			},
			{
				"fieldname": "ticket_type",
				"insert_after": "section_additional",
			},
			{
				"fieldname": "raised_by",
				"insert_after": "ticket_type",
			},
			{
				"fieldname": "column_break_additional",
				"fieldtype": "Column Break",
				"insert_after": "raised_by",
			},
			{
				"fieldname": "via_customer_portal",
				"insert_after": "column_break_additional",
			},
			{
				"fieldname": "raised_outside_working_hours",
				"insert_after": "via_customer_portal",
			},
		]

		# Create section breaks and column breaks as custom fields
		section_fields = {
			"HD Ticket": []
		}

		for arrangement in field_arrangements:
			if arrangement.get("fieldtype") in ["Section Break", "Column Break"]:
				# Check if section/column break already exists
				exists = frappe.db.exists(
					"Custom Field",
					{"dt": doctype, "fieldname": arrangement["fieldname"]}
				)
				
				if not exists:
					section_fields["HD Ticket"].append({
						"fieldname": arrangement["fieldname"],
						"fieldtype": arrangement["fieldtype"],
						"label": arrangement.get("label", ""),
						"insert_after": arrangement["insert_after"],
						"collapsible": arrangement.get("collapsible", 0),
					})

		# Create section breaks
		if section_fields["HD Ticket"]:
			create_custom_fields(section_fields, update=True)
			print(f"  ✓ Created {len(section_fields['HD Ticket'])} section/column breaks")

		# Update existing fields position and properties
		updated_count = 0
		for arrangement in field_arrangements:
			if arrangement.get("fieldtype") not in ["Section Break", "Column Break"]:
				fieldname = arrangement["fieldname"]
				
				# Update custom field
				try:
					custom_field = frappe.db.exists(
						"Custom Field",
						{"dt": doctype, "fieldname": fieldname}
					)
					
					if custom_field:
						field_doc = frappe.get_doc("Custom Field", custom_field)
						if "insert_after" in arrangement:
							field_doc.insert_after = arrangement["insert_after"]
						if "bold" in arrangement:
							field_doc.bold = arrangement["bold"]
						if "read_only" in arrangement:
							field_doc.read_only = arrangement["read_only"]
						field_doc.save()
						updated_count += 1
						print(f"  ✓ Updated: {fieldname}")
				except Exception as e:
					pass  # Field might be standard field, not custom

		frappe.db.commit()

		print(f"\n  Total custom fields updated: {updated_count}")

		print("\n" + "=" * 80)
		print("REARRANGEMENT COMPLETE")
		print("=" * 80)
		print("\nForm sections created:")
		print("  1. Basic Information")
		print("     - Naming Series, Subject")
		print("     - Status, Priority")
		print()
		print("  2. Assignment & Estimation")
		print("     - Module, Assigned To")
		print("     - Team, Estimation Hours")
		print()
		print("  3. Description")
		print("     - Full ticket description")
		print()
		print("  4. Additional Information (Collapsible)")
		print("     - Ticket Type, Raised By")
		print("     - Portal status, Working hours")
		print()

		print("\n" + "=" * 80)
		print("NEXT STEPS")
		print("=" * 80)
		print("1. Clear cache: bench --site [site] clear-cache")
		print("2. Reload DocType: bench --site [site] reload-doctype 'HD Ticket'")
		print("3. Restart: bench restart")
		print("4. Open HD Ticket form to see new layout")
		print("=" * 80 + "\n")

		return True

	except Exception as e:
		print(f"\n✗ Error: {str(e)}")
		import traceback
		traceback.print_exc()
		return False


def customize_hd_ticket_form():
	"""Alias for backward compatibility"""
	return rearrange_hd_ticket_fields()


def reset_hd_ticket_form():
	"""Remove custom section breaks"""
	print("\n" + "=" * 80)
	print("Removing Custom Sections (Reset to Default Layout)")
	print("=" * 80 + "\n")

	try:
		doctype = "HD Ticket"

		# Remove custom section and column breaks we added
		custom_breaks = [
			"section_basic_info",
			"column_break_basic",
			"section_assignment",
			"column_break_assignment",
			"section_description",
			"section_additional",
			"column_break_additional",
		]

		removed_count = 0
		for fieldname in custom_breaks:
			if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": fieldname}):
				frappe.delete_doc("Custom Field", {"dt": doctype, "fieldname": fieldname})
				removed_count += 1
				print(f"  ✓ Removed: {fieldname}")

		frappe.db.commit()

		print(f"\n✓ Removed {removed_count} custom section/column breaks")
		print("\nRun: bench --site [site] reload-doctype 'HD Ticket'")
		print("Then: bench clear-cache && bench restart")
		print("=" * 80 + "\n")

		return True

	except Exception as e:
		print(f"✗ Error: {str(e)}")
		return False


def show_hd_ticket_fields_status():
	"""Show current field order in HD Ticket"""
	print("\n" + "=" * 80)
	print("HD TICKET FIELDS ORDER")
	print("=" * 80 + "\n")

	try:
		# Get all fields from DocType
		fields = frappe.get_all(
			"DocField",
			filters={"parent": "HD Ticket"},
			fields=["fieldname", "label", "fieldtype", "idx"],
			order_by="idx",
		)

		# Get custom fields
		custom_fields = frappe.get_all(
			"Custom Field",
			filters={"dt": "HD Ticket"},
			fields=["fieldname", "label", "fieldtype", "idx"],
			order_by="idx",
		)

		all_fields = sorted(fields + custom_fields, key=lambda x: x.idx)

		print(f"Total Fields: {len(all_fields)}\n")
		print(f"{'#':<4} {'Field Name':<35} {'Type':<20} {'Label':<30}")
		print("-" * 95)

		for idx, field in enumerate(all_fields[:30], 1):
			fieldname = field.fieldname or ""
			fieldtype = field.fieldtype or ""
			label = field.label or ""
			
			# Highlight section breaks
			if fieldtype in ["Section Break", "Column Break"]:
				print(f"{idx:<4} {fieldname:<35} {fieldtype:<20} {label:<30} ⭐")
			else:
				print(f"{idx:<4} {fieldname:<35} {fieldtype:<20} {label:<30}")

		if len(all_fields) > 30:
			print(f"\n... and {len(all_fields) - 30} more fields")

		print("\n" + "=" * 80 + "\n")

	except Exception as e:
		print(f"Error: {str(e)}")


if __name__ == "__main__":
	print(__doc__)
	print("\n📚 Available Functions:\n")
	print("1. rearrange_hd_ticket_fields()     - Organize fields into sections")
	print("2. reset_hd_ticket_form()           - Remove custom sections (reset)")
	print("3. show_hd_ticket_fields_status()   - Show current field order")
	print()
