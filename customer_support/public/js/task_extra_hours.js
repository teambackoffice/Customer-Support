/**
 * Task Extra Hours Client Script
 * Handles extra hour requests from tasks linked to HD Tickets
 */

frappe.ui.form.on("Task", {
	refresh: function (frm) {
		// Calculate and display total hours
		calculate_and_display_total_hours(frm);

		// Add Request Extra Hours button if task is linked to HD Ticket and has assignment
		if (!frm.is_new() && frm.doc.custom_hd_ticket) {
			// Check if task is assigned via ToDo
			check_task_assignment(frm, function(is_assigned) {
				if (is_assigned) {
					frm.add_custom_button(__("Request Extra Hours"), function() {
						request_extra_hours_dialog(frm);
					}, __("Actions"));
				}
			});
		}

		// Show extra hour requests for this task
		if (!frm.is_new() && frm.doc.custom_hd_ticket) {
			show_extra_hour_requests(frm);
		}
	},

	// Recalculate when hours change
	custom_allocated_hours: function (frm) {
		calculate_and_display_total_hours(frm);
	},

	custom_extra_approved_hours: function (frm) {
		calculate_and_display_total_hours(frm);
	}
});

/**
 * Check if task is assigned to current user
 */
function check_task_assignment(frm, callback) {
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "ToDo",
			filters: {
				reference_type: "Task",
				reference_name: frm.doc.name,
				status: "Open"
			},
			fields: ["allocated_to"]
		},
		callback: function(r) {
			const is_assigned = r.message && r.message.length > 0;
			callback(is_assigned);
		}
	});
}

/**
 * Calculate and display total hours
 */
function calculate_and_display_total_hours(frm) {
	if (frm.fields_dict.custom_total_hours) {
		const allocated = parseFloat(frm.doc.custom_allocated_hours || 0);
		const extra = parseFloat(frm.doc.custom_extra_approved_hours || 0);
		const total = allocated + extra;
		
		frm.set_value("custom_total_hours", total);
		
		// Add visual indicator for hours
		if (extra > 0) {
			frm.dashboard.add_indicator(__("Extra Hours Approved: {0}", [extra]), "green");
		}
	}
}

/**
 * Request extra hours dialog
 */
function request_extra_hours_dialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __("Request Extra Hours"),
		fields: [
			{
				fieldtype: "Float",
				fieldname: "requested_hours",
				label: __("Requested Hours"),
				reqd: 1,
				precision: 2
			},
			{
				fieldtype: "Small Text",
				fieldname: "reason",
				label: __("Reason"),
				reqd: 1,
				description: __("Explain why additional hours are needed")
			}
		],
		primary_action_label: __("Submit Request"),
		primary_action: function(values) {
			frappe.call({
				method: "customer_support.customer_support.doctype.extra_hour_request.extra_hour_request.create_extra_hour_request",
				args: {
					task: frm.doc.name,
					requested_hours: values.requested_hours,
					reason: values.reason
				},
				callback: function(r) {
					if (r.message) {
						dialog.hide();
						frappe.show_alert({
							message: __("Extra hour request submitted successfully"),
							indicator: "green"
						});
						frm.reload_doc();
						frappe.set_route("Form", "Extra Hour Request", r.message);
					}
				}
			});
		}
	});
	dialog.show();
}

/**
 * Show extra hour requests for this task
 */
function show_extra_hour_requests(frm) {
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Extra Hour Request",
			filters: {
				task: frm.doc.name
			},
			fields: ["name", "requested_hours", "status", "reason", "creation", "approved_by"],
			order_by: "creation desc"
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				// Remove existing section if present
				frm.dashboard.remove_section("extra_hour_requests");
				
				// Create new section
				const section = frm.dashboard.add_section("extra_hour_requests", __("Extra Hour Requests"));
				
				r.message.forEach(function(request) {
					const status_color = get_status_color(request.status);
					const request_html = `
						<div class="row">
							<div class="col-sm-12">
								<a href="/app/extra-hour-request/${request.name}" target="_blank">
									<strong>${request.name}</strong>
								</a>
								<span class="indicator-pill ${status_color}" style="margin-left: 10px;">
									${request.status}
								</span>
								<br>
								<small>
									Hours: ${request.requested_hours} | 
									Date: ${frappe.datetime.str_to_user(request.creation)} |
									${request.approved_by ? `Approved by: ${request.approved_by}` : ''}
								</small>
								<br>
								<small><em>${request.reason}</em></small>
							</div>
						</div>
						<hr>
					`;
					$(section).append(request_html);
				});
			}
		}
	});
}

/**
 * Get status color for indicator
 */
function get_status_color(status) {
	switch(status) {
		case "Approved":
			return "green";
		case "Rejected": 
			return "red";
		case "Pending":
		default:
			return "orange";
	}
}