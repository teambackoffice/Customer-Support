/* eslint-disable no-undef */

frappe.tests.ui.ready(function() {
    QUnit.module('HD Ticket: Global Support Button');

    // A helper function to create test data for different DocTypes
    const get_test_data = (doctype) => {
        const now = frappe.datetime.now_datetime().replace(/ /g, "-").replace(/:/g, "-");
        switch (doctype) {
            case 'Customer':
                return { customer_name: `Test Customer ${now}`, customer_type: "Individual" };
            case 'Item':
                return { item_code: `Test Item ${now}`, item_group: "All Item Groups" };
            case 'Attendance':
                // This requires an employee to exist. We'll assume one does for the test.
                // If not, this part of the test may fail and require a test employee to be created.
                return { employee: frappe.boot.user.name, status: "Present", attendance_date: frappe.datetime.now_date() };
            default:
                return {};
        }
    };

    // A generic test runner for the support button on any given DocType
    const test_support_button_on_doctype = (doctype, expected_module) => {
        QUnit.test(`Test support button on ${doctype} form`, function(assert) {
            assert.expect(5);
            let done = assert.async();
            let doc_name = '';

            frappe.run_serially([
                // 1. Create a new document to test on
                () => frappe.tests.make(doctype, [get_test_data(doctype)]),

                // 2. Navigate to the new document's form
                () => {
                    doc_name = frappe.locals[doctype][0].name;
                    return frappe.set_route('Form', doctype, doc_name);
                },
                () => frappe.timeout(1), // Wait for the form to load completely

                // 3. Find the support button and click it
                () => {
                    const support_button = $('.global-support-button'); // Assuming this class is used
                    assert.ok(support_button.length > 0 && support_button.is(':visible'), `Support button should be visible on ${doctype} form.`);
                    support_button.click();
                },
                () => frappe.timeout(1), // Wait for the new HD Ticket form to open

                // 4. Verify that a new HD Ticket form is open
                () => {
                    assert.equal(cur_frm.doctype, 'HD Ticket', 'Should have navigated to a new HD Ticket form.');
                    assert.ok(cur_frm.is_new(), 'The HD Ticket form should be a new document.');
                },

                // 5. Verify that the context (module and reference) is correctly set
                () => {
                    assert.equal(cur_frm.doc.custom_module, expected_module, `Module should be pre-filled as '${expected_module}'.`);
                    assert.equal(cur_frm.doc.custom_reference_document_name, doc_name, `Reference document name should be '${doc_name}'.`);
                },

                () => done()
            ]);
        });
    };

    // --- Run the tests ---

    // Test on a DocType from the "Accounts" module
    test_support_button_on_doctype('Customer', 'Accounts');

    // Test on a DocType from the "Stock" module
    test_support_button_on_doctype('Item', 'Stock');

    // Test on a DocType from the "HR" module
    test_support_button_on_doctype('Attendance', 'HR');


    // --- Test the negative case ---

    QUnit.test("Test support button does NOT appear on HD Ticket form", function(assert) {
        assert.expect(1);
        let done = assert.async();

        frappe.run_serially([
            // 1. Create a standard HD Ticket
            () => frappe.tests.make('HD Ticket', [
                { subject: 'Test ticket to check for no support button' }
            ]),

            // 2. Navigate to its form
            () => frappe.set_route('Form', 'HD Ticket', frappe.locals['HD Ticket'][0].name),
            () => frappe.timeout(1),

            // 3. Assert that the support button is NOT visible
            () => {
                const support_button = $('.global-support-button');
                assert.not.ok(support_button.is(':visible'), 'The global support button should NOT be visible on the HD Ticket form itself.');
            },

            () => done()
        ]);
    });
});