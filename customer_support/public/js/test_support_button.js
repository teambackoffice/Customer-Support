/**
 * TEST: Simple Support Button
 * This is a simplified version for testing
 */

console.log('Test support button script loaded!');

// Simple test button
frappe.ui.form.on('*', {
	refresh: function(frm) {
		console.log('Form refresh triggered for:', frm.doc ? frm.doc.doctype : 'unknown');
		
		// Don't add on HD Ticket
		if (frm.doc && frm.doc.doctype === 'HD Ticket') {
			console.log('Skipping HD Ticket');
			return;
		}
		
		// Check if button exists
		if (document.getElementById('test-support-btn')) {
			console.log('Button already exists');
			return;
		}
		
		console.log('Adding test support button...');
		
		// Add simple test button
		const html = `
			<style>
				#test-support-btn {
					position: fixed;
					bottom: 24px;
					right: 24px;
					padding: 12px 20px;
					background: #1c1c1a;
					color: #ffffff;
					border: none;
					border-radius: 999px;
					cursor: pointer;
					z-index: 9999;
					font-size: 15px;
				}
			</style>
			<button id="test-support-btn">🎧 Support TEST</button>
		`;
		
		$('body').append(html);
		
		$('#test-support-btn').on('click', function() {
			alert('Support button clicked! DocType: ' + frm.doc.doctype);
			console.log('Creating ticket for:', frm.doc.doctype, frm.doc.name);
		});
		
		console.log('Test button added successfully!');
	}
});

console.log('Test support button script initialized!');
