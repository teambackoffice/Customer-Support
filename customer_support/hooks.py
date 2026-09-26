app_name = "customer_support"
app_title = "Customer Support"
app_publisher = "Team Backoffice"
app_description = "A web-based ticket management system for managing customer support requests."
app_email = "nahala@teambackoffice.com"
app_license = "mit"

# Apps
# ------------------

# Required apps - customer_support extends HD Ticket from helpdesk
required_apps = ["helpdesk"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "customer_support",
# 		"logo": "/assets/customer_support/logo.png",
# 		"title": "Customer Support",
# 		"route": "/customer_support",
# 		"has_permission": "customer_support.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/customer_support/css/customer_support.css"
app_include_js = "/assets/customer_support/js/global_support_button.js"

# include js, css files in header of web template
# web_include_css = "/assets/customer_support/css/customer_support.css"
# web_include_js = "/assets/customer_support/js/customer_support.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "customer_support/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Sales Invoice": "public/js/global_support_button.js",
	"HD Ticket": "public/js/hd_ticket.js",
	"Task": "public/js/task_extra_hours.js",
	# Add support button to common doctypes
	"Customer": "public/js/global_support_button.js",
	"Supplier": "public/js/global_support_button.js",
	"Item": "public/js/global_support_button.js",
	"Employee": "public/js/global_support_button.js",
	"Attendance": "public/js/global_support_button.js",
	"Leave Application": "public/js/global_support_button.js",
	"Sales Order": "public/js/global_support_button.js",
	"Purchase Order": "public/js/global_support_button.js",
	"Purchase Invoice": "public/js/global_support_button.js",
	"Payment Entry": "public/js/global_support_button.js",
	"Journal Entry": "public/js/global_support_button.js",
	"Stock Entry": "public/js/global_support_button.js",
	"Delivery Note": "public/js/global_support_button.js",
	"Purchase Receipt": "public/js/global_support_button.js",
	"Material Request": "public/js/global_support_button.js",
	"Lead": "public/js/global_support_button.js",
	"Opportunity": "public/js/global_support_button.js",
	"Project": "public/js/global_support_button.js",
	"Issue": "public/js/global_support_button.js",
	"Quotation": "public/js/global_support_button.js",
}
doctype_list_js = {
	"Task": "public/js/task_list.js",
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "customer_support/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "customer_support.utils.jinja_methods",
# 	"filters": "customer_support.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "customer_support.install.before_install"
# after_install = "customer_support.install.after_install"

# Fixtures
# --------

fixtures = [
	{
		"doctype": "Custom Field",
		"filters": {"dt": ["in", ["HD Ticket", "Task"]]}
	},
	{
		"doctype": "Property Setter",
		"filters": {"doc_type": ["in", ["HD Ticket", "Task"]]}
	}
]

# Uninstallation
# ------------

# before_uninstall = "customer_support.uninstall.before_uninstall"
# after_uninstall = "customer_support.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "customer_support.utils.before_app_install"
# after_app_install = "customer_support.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "customer_support.utils.before_app_uninstall"
# after_app_uninstall = "customer_support.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "customer_support.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Project": "customer_support.customer_support.doctype.project.project.Project",
	"Task": "customer_support.customer_support.doctype.task.task.Task",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"HD Ticket": {
		"autoname": "customer_support.customer_support.doctype.hd_ticket.hd_ticket.set_custom_naming_series",
		"before_insert": "customer_support.customer_support.doctype.hd_ticket.hd_ticket.set_default_values",
		"after_insert": [
			"customer_support.customer_support.doctype.hd_ticket.hd_ticket.prevent_auto_assignment",
			"customer_support.customer_support.notification_system.on_ticket_insert"
		],
		"on_update": [
			"customer_support.customer_support.doctype.hd_ticket.hd_ticket.auto_create_task_on_assignment",
			"customer_support.customer_support.notification_system.on_ticket_update",
			"customer_support.customer_support.scheduler.handle_status_reply_reset"
		],
	},
	"Extra Hour Request": {
		"after_insert": "customer_support.customer_support.doctype.extra_hour_request.extra_hour_request.send_manager_notification"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		"* * * * *": [  # Every minute
			"customer_support.customer_support.scheduler.check_escalation_notifications"
		],
		# Ticket sync - runs every 15 minutes
		# Change this cron expression to adjust sync frequency
		"*/15 * * * *": [  # Every 15 minutes
			"customer_support.customer_support.scheduler.sync_tickets_from_remote_sites"
		]
	}
}

# Testing
# -------

# before_tests = "customer_support.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "customer_support.event.get_events"
# }
override_whitelisted_methods = {
	"helpdesk.helpdesk.doctype.hd_ticket.api.get_ticket_customizations": "customer_support.customer_support.overrides.api.get_ticket_customizations"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "customer_support.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["customer_support.utils.before_request"]
# after_request = ["customer_support.utils.after_request"]
after_request = ["customer_support.customer_support.portal_overrides.inject_helpdesk_script"]

# Job Events
# ----------
# before_job = ["customer_support.utils.before_job"]
# after_job = ["customer_support.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"customer_support.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
