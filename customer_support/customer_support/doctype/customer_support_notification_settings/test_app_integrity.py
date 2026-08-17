import frappe
from frappe.tests.utils import FrappeTestCase

# Import the hooks from your app directly to inspect them
import customer_support.hooks as app_hooks

class TestAppIntegrity(FrappeTestCase):
    def test_all_doc_event_hooks_are_valid(self):
        """
        Iterates through all doc_events in hooks.py and verifies that the
        function paths are valid and the functions exist. This prevents
        AttributeError exceptions from outdated hook references.
        """
        if not hasattr(app_hooks, 'doc_events'):
            self.assertTrue(True, "No doc_events found in hooks.py to test.")
            return

        doc_events = app_hooks.doc_events

        for doctype, events in doc_events.items():
            for event, handlers in events.items():
                # Ensure handlers are in a list format
                if isinstance(handlers, str):
                    handlers = [handlers]

                for handler_path in handlers:
                    try:
                        # frappe.get_attr is the same utility Frappe uses to resolve
                        # the hook path to a function object. If it fails, the hook is broken.
                        frappe.get_attr(handler_path)
                        # If successful, the test passes for this hook.
                        self.assertTrue(True, f"Hook is valid: {handler_path}")
                    except (ImportError, AttributeError) as e:
                        # If get_attr fails, we fail the test with a descriptive message.
                        self.fail(
                            f"Invalid hook found in hooks.py!\n"
                            f"  - Doctype: {doctype}\n"
                            f"  - Event: {event}\n"
                            f"  - Path: {handler_path}\n"
                            f"  - Error: {e}"
                        )