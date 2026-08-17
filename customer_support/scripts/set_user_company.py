"""
Script to set custom_company field for all users

This script will:
1. Create the custom_company field in User DocType (if not exists)
2. Get all companies from the system
3. Allow you to set a default company for all users
4. Optionally set specific companies for specific users

Usage:
    bench --site [your-site] console
    >>> from customer_support.scripts.set_user_company import set_company_for_all_users
    >>> set_company_for_all_users()
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_user_company_field():
	"""Create custom_company field in User DocType if it doesn't exist"""
	print("\n" + "=" * 80)
	print("STEP 1: Creating custom_company field in User DocType")
	print("=" * 80)

	try:
		# Check if field already exists
		user_meta = frappe.get_meta("User")
		existing_field = user_meta.get_field("custom_company")

		if existing_field:
			print("✓ custom_company field already exists")
			return True

		# Create the custom field
		custom_fields = {
			"User": [
				{
					"fieldname": "custom_company",
					"fieldtype": "Link",
					"options": "Company",
					"label": "Company",
					"insert_after": "username",
					"description": "Default company for this user (used for HD Ticket naming)",
					"in_standard_filter": 1,
					"in_list_view": 0,
				}
			]
		}

		create_custom_fields(custom_fields, update=True)
		frappe.db.commit()

		print("✓ custom_company field created successfully")
		return True

	except Exception as e:
		print(f"✗ Error creating field: {str(e)}")
		return False


def get_all_companies():
	"""Get list of all companies in the system"""
	try:
		companies = frappe.get_all("Company", fields=["name", "abbr"], order_by="name")
		return companies
	except Exception as e:
		print(f"Error fetching companies: {str(e)}")
		return []


def get_all_users():
	"""Get list of all users (excluding disabled and system users)"""
	try:
		users = frappe.get_all(
			"User",
			fields=["name", "full_name", "email", "enabled"],
			filters={"enabled": 1, "name": ["not in", ["Guest", "Administrator"]]},
			order_by="name",
		)

		# Include Administrator separately
		admin = frappe.get_all(
			"User",
			fields=["name", "full_name", "email", "enabled"],
			filters={"name": "Administrator"},
		)

		if admin:
			users = admin + users

		return users
	except Exception as e:
		print(f"Error fetching users: {str(e)}")
		return []


def set_company_for_user(user_email, company_name):
	"""Set company for a specific user"""
	try:
		user_doc = frappe.get_doc("User", user_email)
		user_doc.custom_company = company_name
		user_doc.save(ignore_permissions=True)
		frappe.db.commit()
		return True
	except Exception as e:
		print(f"Error setting company for {user_email}: {str(e)}")
		return False


def set_company_for_all_users(default_company=None, interactive=True):
	"""
	Set company for all users in the system

	Args:
	    default_company: Company name to set for all users (optional)
	    interactive: If True, prompt for user input; if False, use default_company

	Returns:
	    dict: Summary of operations
	"""
	print("\n" + "=" * 80)
	print("SET COMPANY FOR ALL USERS")
	print("=" * 80 + "\n")

	# Step 1: Create field
	if not create_user_company_field():
		return {"success": False, "message": "Failed to create custom_company field"}

	# Step 2: Get all companies
	print("\n" + "=" * 80)
	print("STEP 2: Fetching Companies")
	print("=" * 80)

	companies = get_all_companies()

	if not companies:
		print("✗ No companies found in the system")
		print("Please create a company first: Go to Setup > Company")
		return {"success": False, "message": "No companies found"}

	print(f"✓ Found {len(companies)} companies:\n")
	for idx, company in enumerate(companies, 1):
		print(f"  {idx}. {company.name} (Abbreviation: {company.abbr})")

	# Step 3: Get all users
	print("\n" + "=" * 80)
	print("STEP 3: Fetching Users")
	print("=" * 80)

	users = get_all_users()

	if not users:
		print("✗ No users found in the system")
		return {"success": False, "message": "No users found"}

	print(f"✓ Found {len(users)} users\n")

	# Step 4: Determine which company to use
	print("\n" + "=" * 80)
	print("STEP 4: Setting Company")
	print("=" * 80 + "\n")

	selected_company = default_company

	if interactive and not selected_company:
		if len(companies) == 1:
			selected_company = companies[0].name
			print(f"Using the only available company: {selected_company}")
		else:
			print("Please select a company to assign to all users:")
			for idx, company in enumerate(companies, 1):
				print(f"  {idx}. {company.name}")
			print("\nNote: You can modify this script to set different companies for different users")
			selected_company = companies[0].name
			print(f"\nUsing first company by default: {selected_company}")
	elif not selected_company:
		# Non-interactive mode without default company
		selected_company = companies[0].name
		print(f"Using first available company: {selected_company}")

	# Step 5: Update all users
	print(f"\nSetting company '{selected_company}' for all users...\n")

	success_count = 0
	failed_count = 0
	results = []

	for user in users:
		user_email = user.name
		user_name = user.full_name or user.email

		# Check if user already has a company
		user_doc = frappe.get_doc("User", user_email)
		current_company = user_doc.get("custom_company")

		if current_company:
			print(f"  ⊙ {user_name} ({user_email}) - Already has company: {current_company}")
			results.append(
				{
					"user": user_email,
					"status": "skipped",
					"company": current_company,
					"message": "Already has company",
				}
			)
			success_count += 1
			continue

		# Set the company
		if set_company_for_user(user_email, selected_company):
			print(f"  ✓ {user_name} ({user_email}) - Set to: {selected_company}")
			results.append(
				{
					"user": user_email,
					"status": "success",
					"company": selected_company,
					"message": "Company set successfully",
				}
			)
			success_count += 1
		else:
			print(f"  ✗ {user_name} ({user_email}) - Failed to set company")
			results.append(
				{"user": user_email, "status": "failed", "company": None, "message": "Failed to set company"}
			)
			failed_count += 1

	# Summary
	print("\n" + "=" * 80)
	print("SUMMARY")
	print("=" * 80)
	print(f"Total users processed: {len(users)}")
	print(f"Successfully updated: {success_count}")
	print(f"Failed: {failed_count}")
	print(f"Default company used: {selected_company}")
	print("=" * 80 + "\n")

	return {
		"success": True,
		"total_users": len(users),
		"success_count": success_count,
		"failed_count": failed_count,
		"company": selected_company,
		"results": results,
	}


def set_specific_companies(user_company_mapping):
	"""
	Set specific companies for specific users

	Args:
	    user_company_mapping: Dict mapping user emails to company names
	                          Example: {
	                              "user1@example.com": "Company A",
	                              "user2@example.com": "Company B",
	                          }

	Returns:
	    dict: Summary of operations
	"""
	print("\n" + "=" * 80)
	print("SET SPECIFIC COMPANIES FOR USERS")
	print("=" * 80 + "\n")

	# Create field first
	if not create_user_company_field():
		return {"success": False, "message": "Failed to create custom_company field"}

	success_count = 0
	failed_count = 0
	results = []

	for user_email, company_name in user_company_mapping.items():
		try:
			# Verify company exists
			if not frappe.db.exists("Company", company_name):
				print(f"  ✗ {user_email} - Company '{company_name}' not found")
				results.append(
					{
						"user": user_email,
						"status": "failed",
						"company": company_name,
						"message": "Company not found",
					}
				)
				failed_count += 1
				continue

			# Verify user exists
			if not frappe.db.exists("User", user_email):
				print(f"  ✗ {user_email} - User not found")
				results.append(
					{
						"user": user_email,
						"status": "failed",
						"company": company_name,
						"message": "User not found",
					}
				)
				failed_count += 1
				continue

			# Set the company
			if set_company_for_user(user_email, company_name):
				print(f"  ✓ {user_email} - Set to: {company_name}")
				results.append(
					{
						"user": user_email,
						"status": "success",
						"company": company_name,
						"message": "Company set successfully",
					}
				)
				success_count += 1
			else:
				results.append(
					{
						"user": user_email,
						"status": "failed",
						"company": company_name,
						"message": "Failed to set company",
					}
				)
				failed_count += 1

		except Exception as e:
			print(f"  ✗ {user_email} - Error: {str(e)}")
			results.append(
				{"user": user_email, "status": "failed", "company": company_name, "message": str(e)}
			)
			failed_count += 1

	# Summary
	print("\n" + "=" * 80)
	print("SUMMARY")
	print("=" * 80)
	print(f"Total mappings processed: {len(user_company_mapping)}")
	print(f"Successfully updated: {success_count}")
	print(f"Failed: {failed_count}")
	print("=" * 80 + "\n")

	return {
		"success": True,
		"total_mappings": len(user_company_mapping),
		"success_count": success_count,
		"failed_count": failed_count,
		"results": results,
	}


def show_user_companies():
	"""Display current company assignments for all users"""
	print("\n" + "=" * 80)
	print("CURRENT USER COMPANY ASSIGNMENTS")
	print("=" * 80 + "\n")

	users = frappe.get_all(
		"User",
		fields=["name", "full_name", "email", "enabled"],
		filters={"enabled": 1},
		order_by="name",
	)

	if not users:
		print("No users found")
		return

	print(f"{'User':<40} {'Company':<30} {'Status':<10}")
	print("-" * 80)

	for user in users:
		user_doc = frappe.get_doc("User", user.name)
		company = user_doc.get("custom_company") or "Not Set"
		user_display = f"{user.full_name or user.email} ({user.name})"

		if company == "Not Set":
			status = "❌"
		else:
			status = "✓"

		print(f"{user_display:<40} {company:<30} {status:<10}")

	print("\n" + "=" * 80 + "\n")


# Quick usage examples
if __name__ == "__main__":
	print(__doc__)
	print("\nQuick Usage Examples:")
	print("\n1. Set same company for all users:")
	print("   >>> set_company_for_all_users('Your Company Name')")
	print("\n2. Set specific companies for specific users:")
	print("   >>> mapping = {")
	print("   ...     'user1@example.com': 'Company A',")
	print("   ...     'user2@example.com': 'Company B',")
	print("   ... }")
	print("   >>> set_specific_companies(mapping)")
	print("\n3. View current assignments:")
	print("   >>> show_user_companies()")
