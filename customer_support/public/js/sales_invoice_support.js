frappe.ui.form.on('Sales Invoice', {
  refresh: function (frm) {
    // This check ensures the global support button script handles this form.
    // The global_support_button.js script is designed to add the button to all
    // forms, so we don't need a separate implementation here.
    // We just need to make sure the global script is loaded for Sales Invoice.

    // By leaving this file empty, we ensure that the `global_support_button.js`
    // script (which is loaded on all pages) will be the one to add the
    // support button. This guarantees a consistent look and feel.
  }
});