"""
Script to add custom_default_module field to User DocType

This field allows users to have a default module that will be automatically
populated when creating HD Tickets.

Usage:
    bench --site [your-site] console
    >>> from customer_support.scripts.add_user_default_module_field import add_default_module_field
    >>> add_default_module_field()
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def add_default_module_field():
	"""Add custom_default_module field to User DocType"""
	print("\n" + "=" * 80)
	print("Adding custom_default_module field to User DocType")
	print("=" * 80 + "\n")

	try:
		# Check if field already exists
		user_meta = frappe.get_meta("User")
		existing_field = user_meta.get_field("custom_default_module")

		if existing_field:
			print("✓ custom_default_module field already exists")
			return True

		# Create the custom field
		# Note: You need to replace "Module" with the actual field type/options
		# If you have specific module options, update the "options" field accordingly
		custom_fields = {
			"User": [
				{
					"fieldname": "custom_default_module",
					"fieldtype": "Data",  # Change to "Link" or "Select" if you have specific options
					"label": "Default Module",
					"insert_after": "custom_company",
					"description": "Default module for HD Tickets created by this user",
					"in_standard_filter": 0,
					"in_list_view": 0,
				}
			]
		}

		create_custom_fields(custom_fields, update=True)
		frappe.db.commit()

		print("✓ custom_default_module field created successfully")
		print("\nNote: This field is set to 'Data' type.")
		print("If you need specific module options, you can:")
		print("1. Go to User DocType → Customize Form")
		print("2. Find custom_default_module field")
		print("3. Change Field Type to 'Select' or 'Link'")
		print("4. Set appropriate Options")
		print()
		return True

	except Exception as e:
		print(f"✗ Error creating field: {str(e)}")
		return False


def set_default_module_for_users(module_mapping):
	"""
	Set default module for specific users

	Args:
	    module_mapping: Dict mapping user emails to module names
	                    Example: {
	                        "user1@example.com": "Accounts",
	                        "user2@example.com": "HR",
	                    }
	"""
	print("\n" + "=" * 80)
	print("Setting Default Module for Users")
	print("=" * 80 + "\n")

	# Ensure field exists
	if not add_default_module_field():
		print("Cannot proceed - field creation failed")
		return False

	success_count = 0
	failed_count = 0

	for user_email, module_name in module_mapping.items():
		try:
			if not frappe.db.exists("User", user_email):
				print(f"✗ {user_email} - User not found")
				failed_count += 1
				continue

			user_doc = frappe.get_doc("User", user_email)
			user_doc.custom_default_module = module_name
			user_doc.save(ignore_permissions=True)

			print(f"✓ {user_email} - Set default module: {module_name}")
			success_count += 1

		except Exception as e:
			print(f"✗ {user_email} - Error: {str(e)}")
			failed_count += 1

	frappe.db.commit()

	print("\n" + "=" * 80)
	print("SUMMARY")
	print("=" * 80)
	print(f"Successfully updated: {success_count}")
	print(f"Failed: {failed_count}")
	print("=" * 80 + "\n")

	return True


def set_same_module_for_all(module_name):
	"""
	Set the same default module for all active users

	Args:
	    module_name: Module name to set (e.g., "Accounts", "HR")
	"""
	print(f"\n" + "=" * 80)
	print(f"Setting default module '{module_name}' for all users")
	print("=" * 80 + "\n")

	# Ensure field exists
	if not add_default_module_field():
		print("Cannot proceed - field creation failed")
		return False

	users = frappe.get_all("User", fields=["name", "full_name"], filters={"enabled": 1})

	print(f"Updating {len(users)} users...\n")

	success_count = 0
	for user in users:
		try:
			user_doc = frappe.get_doc("User", user.name)
			user_doc.custom_default_module = module_name
			user_doc.save(ignore_permissions=True)

			print(f"✓ {user.full_name or user.name}")
			success_count += 1

		except Exception as e:
			print(f"✗ {user.full_name or user.name} - Error: {str(e)}")

	frappe.db.commit()

	print(f"\n✅ Successfully updated {success_count} users")
	print(f"Default module set to: {module_name}\n")

	return True


def show_user_modules():
	"""Display current module assignments for all users"""
	print("\n" + "=" * 80)
	print("CURRENT USER MODULE ASSIGNMENTS")
	print("=" * 80 + "\n")

	users = frappe.get_all("User", fields=["name", "full_name"], filters={"enabled": 1}, order_by="name")

	if not users:
		print("No users found")
		return

	print(f"{'User':<40} {'Default Module':<30}")
	print("-" * 70)

	for user in users:
		user_doc = frappe.get_doc("User", user.name)
		module = user_doc.get("custom_default_module") or "Not Set"
		user_display = user.full_name or user.name

		print(f"{user_display:<40} {module:<30}")

	print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
	print(__doc__)
	print("\n📚 Available Functions:\n")
	print("1. add_default_module_field()              - Create the custom field")
	print("2. set_same_module_for_all('Module Name')  - Set same module for all users")
	print("3. set_default_module_for_users(mapping)   - Set different modules per user")
	print("4. show_user_modules()                     - Show current assignments")
	print()
