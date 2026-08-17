frappe.ui.form.on('Customer Support Notification Settings', {
    refresh: function(frm) {
        // Add custom styling and help text
        frm.add_custom_button(__('Test Notifications'), function() {
            frappe.call({
                method: 'customer_support.customer_support.notification_system.test_notification_system',
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(__('Test notification sent successfully'));
                    }
                }
            });
        });
        
        // Add help text
        frm.set_intro(__('Configure email notifications for HD Tickets. Click on each notification rule below to add recipients.'), 'blue');
    }
});

frappe.ui.form.on('Support Notification Rule', {
    notification_rules_add: function(frm, cdt, cdn) {
        // Set default values for new notification rule
        var row = locals[cdt][cdn];
        row.enabled = 1;
        row.delay_minutes = 0;
        frm.refresh_field('notification_rules');
    },
    
    notification_type: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        
        // Set default email templates based on notification type
        if (row.notification_type === 'New Ticket') {
            row.email_template = 'HD Ticket - New Ticket';
            row.subject = 'New Support Ticket: {{ doc.name }} - {{ doc.subject }}';
            row.trigger_event = 'After Insert';
        } else if (row.notification_type === 'Escalation') {
            row.email_template = 'HD Ticket - Escalation';
            row.subject = '⚠️ ESCALATION: Ticket {{ doc.name }} - No response in 30 minutes';
            row.trigger_event = 'Scheduler';
            row.delay_minutes = 15;
        } else if (row.notification_type === 'Resolved') {
            row.email_template = 'HD Ticket - Resolved';
            row.subject = '✅ Ticket Resolved: {{ doc.name }} - {{ doc.subject }}';
            row.trigger_event = 'Status Change';
        }
        
        frm.refresh_field('notification_rules');
    },
    
    trigger_event: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        
        // Show delay field only for Scheduler events
        if (row.trigger_event === 'Scheduler') {
            frappe.meta.get_docfield('Support Notification Rule', 'delay_minutes', cdn).reqd = 1;
            if (!row.delay_minutes) {
                row.delay_minutes = 15; // Default to 15 for new scheduler rules
            }
        } else {
            frappe.meta.get_docfield('Support Notification Rule', 'delay_minutes', cdn).reqd = 0;
            row.delay_minutes = 0;
        }
        
        frm.refresh_field('notification_rules');
    }
});

frappe.ui.form.on('Notification Recipient', {
    recipient_type: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        
        // Show/hide custom email field based on recipient type
        if (row.recipient_type === 'Custom Email') {
            frappe.meta.get_docfield('Notification Recipient', 'custom_email', cdn).reqd = 1;
            frappe.meta.get_docfield('Notification Recipient', 'custom_email', cdn).hidden = 0;
        } else {
            frappe.meta.get_docfield('Notification Recipient', 'custom_email', cdn).reqd = 0;
            frappe.meta.get_docfield('Notification Recipient', 'custom_email', cdn).hidden = 1;
            row.custom_email = '';
        }
        
        frm.refresh_field('notification_rules');
    },
    
    recipients_add: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        
        // Set default recipient role
        if (!row.recipient_role) {
            row.recipient_role = 'To';
        }
        
        frm.refresh_field('notification_rules');
    }
});