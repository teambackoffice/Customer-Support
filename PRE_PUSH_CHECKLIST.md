# Pre-Push Checklist for Customer Support App

## ✅ Custom Fields Safety Check

Your custom fields for HD Ticket are **SAFE** because:

1. **Proper Prefix**: All custom fields use `custom_` prefix
   - `custom_naming_series`
   - `custom_is_follow_up`
   - `custom_ticket_source`
   - etc.

2. **Fixtures Configured**: `hooks.py` exports custom fields
   ```python
   fixtures = [
       {"doctype": "Custom Field", "filters": {"dt": ["in", ["HD Ticket", "Task"]]}}
   ]
   ```

3. **Patches Registered**: All patches in `patches.txt` will run on migration

4. **No HD Ticket DocType Override**: You're NOT modifying the HD Ticket DocType itself

## Before Git Push - Verify These

### 1. Export Latest Fixtures

Make sure fixtures are up to date:

```bash
cd /Users/nahala/frappe-bench
bench --site tboindia export-fixtures
```

This updates `fixtures/custom_field.json` with latest changes.

### 2. Check Git Status

```bash
cd apps/customer_support
git status
```

Should show:
- ✅ Modified: `customer_support/hooks.py`
- ✅ Modified: `customer_support/fixtures/custom_field.json`
- ✅ Modified: `customer_support/patches.txt`
- ✅ New: Patch files in `patches/v1_0/`
- ✅ New: Custom scripts (sync_tickets.py, etc.)

### 3. Stage Important Files

```bash
git add customer_support/hooks.py
git add customer_support/fixtures/
git add customer_support/patches.txt
git add customer_support/patches/v1_0/
git add customer_support/customer_support/sync_tickets.py
git add customer_support/customer_support/sync_tickets.py
```

### 4. Ignore Temporary Files

Make sure these are in `.gitignore`:
- `__pycache__/`
- `*.pyc`
- `_tmp_*.py` (your temporary diagnostic scripts)
- `*.log`

Check:
```bash
cat .gitignore
```

### 5. Commit with Clear Message

```bash
git commit -m "feat: Add custom fields and ticket sync for HD Ticket

- Add custom_naming_series for auto-naming (TBO260926001 format)
- Add ticket sync functionality to sync from remote sites
- Add custom fields for follow-up tickets, references, and assignments
- Add patches for field migration
- Update fixtures with HD Ticket custom fields"
```

### 6. Push to Remote

```bash
git push origin main  # or your branch name
```

## ⚠️ Important Notes

### Will This Cause Errors?

**NO** - Adding custom fields to HD Ticket from your app is:
- ✅ Standard Frappe pattern
- ✅ Used by many production apps
- ✅ Won't break HD Ticket functionality
- ✅ Can be uninstalled cleanly

### What Happens on Other Sites?

When someone installs your `customer_support` app:

1. **Migration runs** → Custom fields are created
2. **Fixtures imported** → Field definitions loaded
3. **HD Ticket extended** → Works with new fields
4. **No conflicts** → helpdesk app continues to work normally

### Dependencies

Your app requires:
- ✅ `frappe` (already required)
- ✅ `helpdesk` (for HD Ticket DocType)

Add this to `hooks.py`:

```python
required_apps = ["helpdesk"]
```

This ensures helpdesk is installed before customer_support.

## Post-Push - Testing on Fresh Site

To test your app works correctly after push:

```bash
# On a fresh site
bench new-site test-site
bench --site test-site install-app helpdesk
bench --site test-site install-app customer_support
bench --site test-site migrate

# Verify custom fields exist
bench --site test-site console
```

Then in console:
```python
import frappe
meta = frappe.get_meta("HD Ticket")
print("Custom fields:")
for field in meta.fields:
    if field.fieldname.startswith("custom_"):
        print(f"  - {field.fieldname}")
```

Should show all your custom fields!

## Files to Push

### Core Functionality
- ✅ `customer_support/hooks.py`
- ✅ `customer_support/fixtures/custom_field.json`
- ✅ `customer_support/fixtures/property_setter.json`
- ✅ `customer_support/patches.txt`
- ✅ `customer_support/patches/v1_0/*.py`
- ✅ `customer_support/customer_support/doctype/hd_ticket/hd_ticket.py`
- ✅ `customer_support/customer_support/sync_tickets.py`

### Documentation
- ✅ `README.md` (update with features)
- ✅ `MIGRATION_REQUIRED.md` (for users)
- ✅ `TICKET_SYNC_SETUP_GUIDE.md` (for users)

### Do NOT Push
- ❌ `_tmp_*.py` (temporary scripts)
- ❌ `*.pyc` (compiled python)
- ❌ `__pycache__/` (cache directories)
- ❌ `.DS_Store` (Mac files)
- ❌ Local test scripts unless documented

## Summary

✅ **Your setup is correct and safe!**
✅ **Custom fields won't cause errors**
✅ **Standard Frappe practice**
✅ **Ready to push to Git**

Just follow the steps above and you're good to go!
