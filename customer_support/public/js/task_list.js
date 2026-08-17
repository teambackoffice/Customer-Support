/**
 * Client script for Task List View
 * - Adds color indicators to the custom_workflow_status ("Workflow Status") field.
 */

frappe.listview_settings["Task"] = frappe.listview_settings["Task"] || {};
frappe.listview_settings["Task"].formatters = frappe.listview_settings["Task"].formatters || {};

frappe.listview_settings["Task"].formatters.custom_workflow_status = function (val) {
	if (!val) {
		return "";
	}
	const color_map = {
		"Extra Hour Requested": "orange",
		Approved: "green",
		Rejected: "red",
		Pending: "yellow",
	};
	const color = color_map[val] || "gray";
	return `<span class="indicator-pill ${color}">${val}</span>`;
};
