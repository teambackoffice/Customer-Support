"""
Quick Setup Script: Set Company for All Users

This is a simplified script to quickly set up the company field for all users.

Usage:
    bench --site [your-site] console
    
    # Then run:
    >>> from customer_support.scripts.quick_setup_users import quick_setup
    >>> quick_setup()
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def quick_setup():
	"""
	Quick setup to:
	1. Create custom_company field in User DocType
	2. Set the first available company to all users
	"""
	print("\n" + "🚀 " + "=" * 76)
	print("QUICK SETUP: Setting Company for All Users")
	print("=" * 78 + "\n")

	try:
		# Step 1: Create custom field
		print("Step 1: Creating custom_company field...")
		user_meta = frappe.get_meta("User")
		existing_field = user_meta.get_field("custom_company")

		if not existing_field:
			custom_fields = {
				"User": [
					{
						"fieldname": "custom_company",
						"fieldtype": "Link",
						"options": "Company",
						"label": "Company",
						"insert_after": "username",
						"description": "Default company for this user",
						"in_standard_filter": 1,
					}
				]
			}
			create_custom_fields(custom_fields, update=True)
			frappe.db.commit()
			print("✓ Field created\n")
		else:
			print("✓ Field already exists\n")

		# Step 2: Get first company
		print("Step 2: Getting companies...")
		companies = frappe.get_all("Company", fields=["name", "abbr"], limit=1)

		if not companies:
			print("❌ No companies found!")
			print("Please create a company first: Setup > Company")
			return False

		company_name = companies[0].name
		company_abbr = companies[0].abbr
		print(f"✓ Using company: {company_name} ({company_abbr})\n")

		# Step 3: Get all active users
		print("Step 3: Getting users...")
		all_users = frappe.get_all("User", fields=["name", "full_name"], filters={"enabled": 1})

		print(f"✓ Found {len(all_users)} active users\n")

		# Step 4: Update users
		print("Step 4: Updating users...")
		updated = 0
		skipped = 0

		for user in all_users:
			user_doc = frappe.get_doc("User", user.name)

			# Skip if already has company
			if user_doc.get("custom_company"):
				skipped += 1
				continue

			# Set company
			user_doc.custom_company = company_name
			user_doc.save(ignore_permissions=True)
			updated += 1
			print(f"  ✓ {user.full_name or user.name}")

		frappe.db.commit()

		# Summary
		print("\n" + "=" * 78)
		print("✅ SETUP COMPLETE!")
		print("=" * 78)
		print(f"Company set: {company_name} ({company_abbr})")
		print(f"Users updated: {updated}")
		print(f"Users skipped (already had company): {skipped}")
		print(f"Total users: {len(all_users)}")
		print("=" * 78 + "\n")

		print("✓ You can now create HD Tickets!")
		print("✓ Each ticket will be named: <CompanyAbbr><DDMMYY><Sequence>")
		print(f"✓ Example: {company_abbr}26062601\n")

		return True

	except Exception as e:
		print(f"\n❌ Error: {str(e)}")
		import traceback

		traceback.print_exc()
		return False


def set_company_to_all(company_name):
	"""
	Set a specific company to all users

	Args:
	    company_name: Name of the company to set

	Usage:
	    >>> set_company_to_all("Hyderabad Office")
	"""
	print(f"\n🚀 Setting company '{company_name}' to all users...\n")

	try:
		# Verify company exists
		if not frappe.db.exists("Company", company_name):
			print(f"❌ Company '{company_name}' not found!")
			print("\nAvailable companies:")
			companies = frappe.get_all("Company", fields=["name", "abbr"])
			for comp in companies:
				print(f"  - {comp.name} ({comp.abbr})")
			return False

		# Get company details
		company = frappe.get_doc("Company", company_name)
		print(f"✓ Company found: {company.name} (Abbreviation: {company.abbr})\n")

		# Get all users
		all_users = frappe.get_all("User", fields=["name", "full_name"], filters={"enabled": 1})

		print(f"Updating {len(all_users)} users...\n")

		updated = 0
		for user in all_users:
			user_doc = frappe.get_doc("User", user.name)
			user_doc.custom_company = company_name
			user_doc.save(ignore_permissions=True)
			updated += 1
			print(f"  ✓ {user.full_name or user.name}")

		frappe.db.commit()

		print(f"\n✅ Successfully updated {updated} users!")
		print(f"All users now assigned to: {company_name} ({company.abbr})\n")

		return True

	except Exception as e:
		print(f"\n❌ Error: {str(e)}")
		import traceback

		traceback.print_exc()
		return False


def list_companies():
	"""List all available companies"""
	print("\n📋 Available Companies:\n")

	companies = frappe.get_all("Company", fields=["name", "abbr", "country"], order_by="name")

	if not companies:
		print("No companies found")
		return

	for idx, comp in enumerate(companies, 1):
		print(f"{idx}. {comp.name}")
		print(f"   Abbreviation: {comp.abbr}")
		print(f"   Country: {comp.country}")
		print()


def show_user_status():
	"""Show which users have company assigned"""
	print("\n📊 User Company Status:\n")

	users = frappe.get_all("User", fields=["name", "full_name"], filters={"enabled": 1}, order_by="name")

	has_company = 0
	no_company = 0

	print(f"{'User':<40} {'Company':<30}")
	print("-" * 70)

	for user in users:
		user_doc = frappe.get_doc("User", user.name)
		company = user_doc.get("custom_company")

		user_display = user.full_name or user.name

		if company:
			print(f"✓ {user_display:<38} {company:<30}")
			has_company += 1
		else:
			print(f"❌ {user_display:<38} {'Not Set':<30}")
			no_company += 1

	print("-" * 70)
	print(f"Total: {len(users)} | With Company: {has_company} | Without Company: {no_company}\n")


if __name__ == "__main__":
	print(__doc__)
	print("\n📚 Available Functions:\n")
	print("1. quick_setup()              - Automatic setup (uses first company)")
	print("2. set_company_to_all('name') - Set specific company to all users")
	print("3. list_companies()           - Show all available companies")
	print("4. show_user_status()         - Show current user assignments")
	print()
