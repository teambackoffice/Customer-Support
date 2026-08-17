import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now

from customer_support.customer_support.doctype.hd_ticket.hd_ticket import send_estimate_resolution_time

class TestResolutionEstimate(FrappeTestCase):

    def setUp(self):
        """Set up the necessary documents for testing."""
        # Create a test user who will send the estimate
        self.agent_user = frappe.get_doc({
            "doctype": "User",
            "email": f"test_agent_{now()}@example.com",
            "first_name": "Test Agent",
            "roles": [{"role": "System Manager"}] # Role with permissions
        }).insert(ignore_permissions=True)

        # Create a test HD Ticket
        self.ticket = frappe.get_doc({
            "doctype": "HD Ticket",
            "subject": "Test Ticket for Timeline Comment",
            "raised_by": "customer@example.com",
            "status": "Open"
        }).insert(ignore_permissions=True)

        # Create a dummy Email Template
        if not frappe.db.exists("Email Template", "Test Estimate Template"):
            frappe.get_doc({
                "doctype": "Email Template",
                "name": "Test Estimate Template",
                "subject": "Test",
                "response": "Test"
            }).insert()

        # Create Notification Settings and a rule for "Resolution Estimate"
        self.settings = frappe.get_single("Customer Support Notification Settings")
        self.settings.enable_notifications = 1
        self.settings.append("notification_rules", {
            "enabled": 1,
            "notification_type": "Resolution Estimate",
            "trigger_event": "Manual Action",
            "email_template": "Test Estimate Template",
            "send_once": 0 # Disable send_once for simplicity in testing
        })
        self.settings.save(ignore_permissions=True)

        # Set the current user for the test
        frappe.set_user(self.agent_user.name)

    def tearDown(self):
        """Clean up test data."""
        frappe.set_user("Administrator")
        # Documents created will be rolled back by FrappeTestCase
        frappe.db.rollback()

    def test_timeline_comment_is_created(self):
        """
        Test that a comment is added to the HD Ticket's timeline after
        sending a resolution estimate.
        """
        estimation_hours = 5.5

        # Call the function to send the estimate
        send_estimate_resolution_time(
            ticket_name=self.ticket.name,
            estimation_hours=estimation_hours
        )

        # Verify that a comment was created
        comment = frappe.get_all(
            "Comment",
            filters={
                "reference_doctype": "HD Ticket",
                "reference_name": self.ticket.name,
                "comment_type": "Info"
            },
            fields=["content", "comment_by"]
        )

        self.assertEqual(len(comment), 1, "A timeline comment should have been created.")
        self.assertIn(str(estimation_hours), comment[0].content, "Comment content should include the estimation hours.")
        self.assertEqual(comment[0].comment_by, self.agent_user.name, "Comment should be created by the user who sent the estimate.")