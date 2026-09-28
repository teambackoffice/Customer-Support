import frappe

# Extend the Project class that ERPNext / HRMS would otherwise use, so their
# methods (update_project, costing, gross margin, ...) keep working.
try:
	from hrms.overrides.employee_project import EmployeeProject as BaseProject
except ImportError:
	from erpnext.projects.doctype.project.project import Project as BaseProject


class Project(BaseProject):
	def before_save(self):
		if hasattr(super(), "before_save"):
			super().before_save()

		if not self.custom_abbr and self.project_name:
			self.custom_abbr = "".join(
				word[0].upper() for word in self.project_name.split() if word
			)
