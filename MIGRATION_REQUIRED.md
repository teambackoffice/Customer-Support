# Migration Required: Fix Missing Custom Fields

## Problem

The customer_support app has custom fields defined in code and patches, but they haven't been applied to the database yet. This causes errors when trying to create HD Tickets:

- `Unknown column 'custom_naming_series' in 'SELECT'`
- `Unknown column 'tabHD Ticket.custom_is_follow_up' in 'WHERE'`

## Root Cause

The patches in `customer_support/patches.txt` contain field definitions that need to be executed via migration:

1. `add_custom_naming_series_field` - Adds the custom naming series field
2. `add_hd_ticket_follow_up_fields` - Adds follow-up ticket fields
3. And several other patches that add custom fields

These patches have been registered but **not yet executed** on your database.

## Solution: Run Migration

### Option 1: Migrate Specific Site (Recommended)

```bash
# Your site name is: tboindia
bench --site tboindia migrate
```

### Option 2: Migrate All Sites

```bash
bench migrate
```

### Option 3: Manual Patch Execution (If migration fails)

If the full migration encounters issues, you can run specific patches:

```bash
bench --site tboindia console
```

Then in the Python console:

```python
# Run the naming series field patch
from customer_support.patches.v1_0.add_custom_naming_series_field import execute as add_naming
add_naming()

# Run the follow-up fields patch
from customer_support.patches.v1_0.add_hd_ticket_follow_up_fields import execute as add_followup
add_followup()

# Run other required patches
from customer_support.patches.v1_0.add_hd_ticket_reference_fields import execute as add_ref
add_ref()

# Commit the changes
frappe.db.commit()
```

## What the Migration Will Do

The migration will:

1. ✅ Create `custom_naming_series` field in HD Ticket
2. ✅ Create `custom_is_follow_up` field in HD Ticket
3. ✅ Create `custom_parent_ticket` field in HD Ticket
4. ✅ Create `custom_follow_up_sequence` field in HD Ticket
5. ✅ Create `custom_reference_document` and `custom_reference_document_name` fields
6. ✅ Create `custom_assigned_to`, `custom_estimation_hours` fields
7. ✅ Create `custom_module`, `custom_customer` fields
8. ✅ And all other custom fields defined in the patches

## After Migration

Once the migration completes successfully:

1. Reload your browser/clear cache
2. Try creating an HD Ticket again from the Lead form
3. The custom naming should work properly (e.g., TBO260918001)

## Verification

After migration, you can verify the fields exist:

```bash
bench --site tboindia console
```

```python
import frappe
meta = frappe.get_meta("HD Ticket")

# Check for key custom fields
fields_to_check = [
    "custom_naming_series",
    "custom_is_follow_up",
    "custom_parent_ticket",
    "custom_assigned_to",
    "custom_reference_document"
]

for field in fields_to_check:
    exists = meta.get_field(field)
    print(f"{field}: {'✓ EXISTS' if exists else '✗ MISSING'}")
```

## Next Steps

1. Run the migration command
2. Check the migration logs for any errors
3. If successful, test ticket creation
4. Delete this file once migration is complete

---

**Created:** 2026-09-26
**Status:** MIGRATION PENDING
