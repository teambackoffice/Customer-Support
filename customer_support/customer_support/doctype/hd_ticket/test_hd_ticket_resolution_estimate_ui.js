/* eslint-disable no-undef */

frappe.tests.ui.ready(function() {
    // To run this test, you can use the command:
    // bench --site [your-site] run-ui-tests --app customer_support --doctype "HD Ticket"

    QUnit.module('HD Ticket: Resolution Estimate');

    QUnit.test("Test 'Send Estimate Resolution Time' dialog functionality", function(assert) {
        assert.expect(8);
        let done = assert.async();

        // Use frappe.run_serially to execute steps in order
        frappe.run_serially([
            // 1. Create a new HD Ticket to test with
            () => frappe.tests.make('HD Ticket', [
                { subject: 'UI Test for Resolution Estimate' },
                { raised_by: 'customer@example.com' },
                { status: 'Open' }
            ]),

            // 2. Go to the newly created ticket's form
            () => frappe.set_route('Form', 'HD Ticket', frappe.locals['HD Ticket'][0].name),
            () => frappe.timeout(1), // Wait for form to load

            // 3. Click the "Actions" button to open the menu
            () => {
                assert.ok(cur_frm.page.menu.find('[data-label="Actions"]').is(':visible'), 'Actions menu button is visible.');
                cur_frm.page.menu.find('[data-label="Actions"]').click();
            },
            () => frappe.timeout(0.5),

            // 4. Click the "Send Estimate Resolution Time" button
            () => {
                const send_button = cur_frm.page.menu.find('li:contains("Send Estimate Resolution Time")');
                assert.ok(send_button.is(':visible'), '"Send Estimate Resolution Time" button is visible in the Actions menu.');
                send_button.click();
            },
            () => frappe.timeout(0.5),

            // 5. Verify the dialog is open
            () => {
                assert.ok($('.modal-dialog .modal-title:contains("Send Estimate Resolution Time")').is(':visible'), 'Dialog is open with the correct title.');
            },

            // 6. Enter a value in the estimation hours field
            () => {
                const dialog = frappe.ui.get_open_dialog();
                assert.ok(dialog, 'Dialog object is accessible.');

                // Set a value and check it
                dialog.set_value('estimation_hours', 8.5);
                assert.equal(dialog.get_value('estimation_hours'), 8.5, 'Estimation hours set correctly in the dialog.');
            },

            // 7. Click the primary action ("Send") button
            () => {
                // Mock the server call to avoid actual email sending during tests
                frappe.tests.mock_server = true;
                frappe.call = (opts) => {
                    assert.equal(opts.method, 'customer_support.customer_support.doctype.hd_ticket.hd_ticket.send_estimate_resolution_time', 'Correct backend method is called.');
                    assert.deepEqual(opts.args, { ticket_name: cur_frm.doc.name, estimation_hours: 8.5, force_send: false }, 'Correct arguments are passed to the backend.');
                    // Simulate a successful response
                    if (opts.callback) {
                        opts.callback({ message: { status: 'success' } });
                    }
                };
                $('.modal-dialog .btn-primary:contains("Send")').click();
                frappe.tests.mock_server = false; // Unmock
            },
            () => frappe.timeout(1),

            // 8. Verify the success alert and that the dialog is closed
            () => {
                assert.ok($('.frappe-alert-for-async.alert-success').is(':visible'), 'Success alert is shown after sending.');
                done();
            }
        ]);
    });
});