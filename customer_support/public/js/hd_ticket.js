frappe.ui.form.on('HD Ticket', {
    refresh: function(frm) {
        // This function runs every time the form is loaded or refreshed.
        // We will add all our custom buttons and logic here.

        // 1. "Create Follow-up Ticket" button
        //    - Appears only when the ticket status is 'Not Completed'.
        if (frm.doc.status === 'Not Completed' && !frm.is_new()) {
            frm.add_custom_button(__('Create Follow-up Ticket'), function() {
                // Show a dialog to get the reason for the follow-up.
                frappe.prompt({
                    fieldname: 'reason',
                    label: 'Reason for Follow-up',
                    fieldtype: 'Data',
                    reqd: 1
                }, (values) => {
                    // Call the backend Python method to create the follow-up ticket.
                    frappe.call({
                        method: 'customer_support.customer_support.doctype.hd_ticket.hd_ticket.create_follow_up_ticket',
                        args: {
                            parent_ticket_name: frm.doc.name,
                            reason: values.reason
                        },
                        callback: function(r) {
                            if (r.message && r.message.success) {
                                // If successful, navigate to the new follow-up ticket.
                                frappe.set_route('Form', 'HD Ticket', r.message.follow_up_ticket);
                            }
                        }
                    });
                }, __('Create Follow-up'), __('Create'));
            }, __('Actions'));
        }

        // 2. "Send Resolution Estimate" button
        //    - Appears if the ticket is open and not resolved/closed.
        if (!frm.is_new() && !['Resolved', 'Closed'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Send Resolution Estimate'), function() {
                // Open a dialog to ask for the estimation in hours.
                frappe.prompt([
                    {
                        fieldname: 'estimation_hours',
                        label: __('Estimated Resolution Time (in hours)'),
                        fieldtype: 'Float',
                        reqd: 1,
                        default: frm.doc.custom_estimated_resolution_hour || ''
                    }
                ], function(values) {
                    // Call the backend Python method.
                    frappe.call({
                        method: 'customer_support.customer_support.doctype.hd_ticket.hd_ticket.send_estimate_resolution_time',
                        args: {
                            ticket_name: frm.doc.name,
                            estimation_hours: values.estimation_hours
                        },
                        callback: function(r) {
                            if (r.message) {
                                if (r.message.status === 'success') {
                                    frm.reload_doc(); // Reload to show the new comment and updated hours.
                                } else if (r.message.status === 'already_sent') {
                                    // If estimate was already sent, ask the user if they want to send it again.
                                    frappe.confirm(
                                        __('A resolution estimate has already been sent for this ticket. Do you want to send it again?'),
                                        function() {
                                            // Call the backend method again with force_send=True
                                            frappe.call({
                                                method: 'customer_support.customer_support.doctype.hd_ticket.hd_ticket.send_estimate_resolution_time',
                                                args: {
                                                    ticket_name: frm.doc.name,
                                                    estimation_hours: values.estimation_hours,
                                                    force_send: true
                                                },
                                                callback: function(r) {
                                                    if (r.message && r.message.status === 'success') {
                                                        frm.reload_doc();
                                                    }
                                                }
                                            });
                                        }
                                    );
                                }
                            }
                        }
                    });
                }, __('Send Estimate'), __('Send'));
            }, __('Actions'));
        }

        // 3. "Create Task" button
        //    - Appears if the ticket is assigned but no task has been created yet.
        //    - Note: The system now auto-creates tasks, so this button is a manual fallback.
        if (frm.doc.custom_assigned_to && !frm.doc.custom_related_task && !frm.is_new()) {
            frm.add_custom_button(__('Create Task'), function() {
                // This would call a whitelisted method to manually create a task.
                // Since auto-creation is implemented, we can just notify the user.
                // If you need a manual creation method, it can be added.
                frappe.show_alert({
                    message: __('A task is automatically created when a ticket is assigned. If it failed, please check the Error Log.'),
                    indicator: 'info'
                });
            }, __('Actions'));
        }

        // 4. Display Ticket Relationships (Parent/Follow-ups)
        //    - Adds a custom HTML section to the form to show related tickets.
        if (!frm.is_new()) {
            frappe.call({
                method: "customer_support.customer_support.doctype.hd_ticket.hd_ticket.get_ticket_relationships",
                args: { ticket_name: frm.doc.name },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        let html = '';
                        // Display parent ticket if this is a follow-up
                        if (r.message.parent_ticket) {
                            html += `
                                <div class="frappe-control">
                                    <div class="form-group">
                                        <div class="clearfix">
                                            <label class="control-label" style="padding-right: 0px;">Parent Ticket</label>
                                        </div>
                                        <div class="control-input-wrapper">
                                            <a href="/app/hd-ticket/${r.message.parent_ticket.name}">${r.message.parent_ticket.name}</a>: ${r.message.parent_ticket.subject}
                                        </div>
                                    </div>
                                </div>`;
                        }

                        // Display follow-up tickets
                        if (r.message.follow_up_tickets && r.message.follow_up_tickets.length > 0) {
                            html += `
                                <div class="frappe-control">
                                    <div class="form-group">
                                        <div class="clearfix">
                                            <label class="control-label" style="padding-right: 0px;">Follow-up Tickets</label>
                                        </div>
                                        <div class="control-input-wrapper">
                                            <ul>`;
                            r.message.follow_up_tickets.forEach(ticket => {
                                html += `<li><a href="/app/hd-ticket/${ticket.name}">${ticket.name}</a>: ${ticket.subject} (${ticket.status})</li>`;
                            });
                            html += `       </ul>
                                        </div>
                                    </div>
                                </div>`;
                        }

                        if (html) {
                            frm.fields_dict.ticket_relationships_html.html(html);
                        }
                    }
                }
            });
        }
    },

    // Client-side validation to complement the backend validation.
    custom_estimated_resolution_hour: function(frm) {
        if (frm.doc.custom_estimated_resolution_hour && !frm.doc.custom_assigned_to) {
            frappe.show_alert({
                message: __('Please assign this ticket to a user before adding an estimation.'),
                indicator: 'orange'
            });
            frm.set_value('custom_estimated_resolution_hour', ''); // Clear the value
        }
    }
});