import frappe

@frappe.whitelist()
def get_ticket_customizations():
    """
    Override for Helpdesk API to inject custom fields and actions into the Vue SPA.
    """
    # 1. Fetch custom fields dynamically from the DB to show in the portal
    fields_to_show = [
        "custom_module",
        "custom_screenshot_",
        "custom_assigned_to",
        "custom_estimation_hours",
        "custom_related_task",
        "custom_reference_document",
        "custom_reference_document_name",
        "custom_estimated_resolution_hour",
        "custom_customer"
    ]
    
    custom_fields = frappe.get_all(
        "Custom Field",
        filters={"dt": "HD Ticket", "fieldname": ["in", fields_to_show]},
        fields=["fieldname", "reqd as required", "placeholder"],
        order_by="idx"
    )
    
    # Helpdesk natively expects `url_method` on template fields.
    for cf in custom_fields:
        cf["url_method"] = None
        
    # 2. Get original form scripts (if any)
    try:
        from helpdesk.helpdesk.doctype.hd_ticket.api import get_form_script
        form_scripts = get_form_script("HD Ticket") or []
    except Exception:
        form_scripts = []
        
    if not isinstance(form_scripts, list):
        form_scripts = [form_scripts]
        
    # 3. Inject our Vue setupForm payload to add custom actions safely
    custom_script = """
function setupForm(ctx) {
    const doc = (ctx && ctx.doc) ? ctx.doc : {};
    // frappe-ui's call wrapper directly returns the promise resolving to the message object.
    const _call = ctx && ctx.call ? ctx.call : null;
    
    return {
        actions: [
            {
                label: "Create Follow-up Ticket",
                onClick: () => {
                    const currentDoc = (ctx && ctx.doc) ? ctx.doc : {};
                    if (currentDoc.status !== 'Not Completed') {
                        window.alert('Follow-up can only be created for Not Completed tickets.');
                        return;
                    }
                    const reason = window.prompt("Reason for Follow-up:");
                    if (reason && _call) {
                        _call('customer_support.customer_support.doctype.hd_ticket.hd_ticket.create_follow_up_ticket', {
                            parent_ticket_name: currentDoc.name,
                            reason: reason
                        }).then(r => {
                            if (r && r.success) {
                                window.location.href = '/helpdesk/tickets/' + r.follow_up_ticket;
                            }
                        }).catch(err => {
                            console.error(err);
                            window.alert('Failed to create follow-up ticket.');
                        });
                    }
                }
            },
            {
                label: "Send Resolution Estimate",
                onClick: () => {
                    const currentDoc = (ctx && ctx.doc) ? ctx.doc : {};
                    if (['Resolved', 'Closed'].includes(currentDoc.status)) {
                        window.alert('Cannot send estimate for resolved/closed tickets.');
                        return;
                    }
                    const defaultHours = currentDoc.custom_estimation_hours || '';
                    const hours = window.prompt("Estimated Resolution Time (in hours):", defaultHours);
                    if (hours !== null && hours !== '' && _call) {
                        _call('customer_support.customer_support.doctype.hd_ticket.hd_ticket.send_estimate_resolution_time', {
                            ticket_name: currentDoc.name,
                            estimation_hours: hours
                        }).then(r => {
                            if (r) {
                                if (r.status === 'success') {
                                    window.location.reload();
                                } else if (r.status === 'already_sent') {
                                    if (window.confirm('A resolution estimate has already been sent for this ticket. Do you want to send it again?')) {
                                        _call('customer_support.customer_support.doctype.hd_ticket.hd_ticket.send_estimate_resolution_time', {
                                            ticket_name: currentDoc.name,
                                            estimation_hours: hours,
                                            force_send: true
                                        }).then(res => {
                                            if (res && res.status === 'success') {
                                                window.location.reload();
                                            }
                                        });
                                    }
                                }
                            }
                        }).catch(err => {
                            console.error(err);
                        });
                    }
                }
            },
            {
                label: "Create Task",
                onClick: () => {
                    const currentDoc = (ctx && ctx.doc) ? ctx.doc : {};
                    if (!currentDoc.custom_assigned_to) {
                        window.alert('Please assign the ticket to someone first (using the custom Assigned To field) before creating a task.');
                        return;
                    }
                    if (currentDoc.custom_related_task) {
                        window.alert('A task has already been created for this ticket.');
                        return;
                    }
                    window.alert('A task is automatically created when a ticket is assigned and estimation hours are provided. If it failed, please check the Error Log.');
                }
            }
        ]
    };
}
"""
    
    form_scripts.append(custom_script)

    return {"custom_fields": custom_fields, "_form_script": form_scripts}
