import frappe
from frappe.model.document import Document


class Project(Document):
	def before_save(self):
		if not self.custom_abbr and self.project_name:
			self.custom_abbr = "".join(
				word[0].upper() for word in self.project_name.split() if word
			)
