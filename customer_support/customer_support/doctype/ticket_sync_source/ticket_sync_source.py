# Copyright (c) 2024, nehala and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TicketSyncSource(Document):
	def validate(self):
		if not self.site_url:
			return
		self.site_url = self.site_url.strip().rstrip("/")
		if not self.site_url.startswith(("http://", "https://")):
			frappe.throw("Site URL must start with http:// or https://")
