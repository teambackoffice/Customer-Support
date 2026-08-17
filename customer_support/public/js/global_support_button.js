/**
 * Global Support Button
 * Adds a floating support button (like Sales Invoice) to all DocType forms
 * Allows users to create HD Tickets from any form
 */

// Debug: Log when this script loads
console.log('Global Support Button script loaded for:', window.location.pathname);

// Simple approach - wait for form to be ready and add button
$(document).ready(function() {
	console.log('Document ready, setting up global support button');
	
	// Wait a bit for Frappe form to initialize
	setTimeout(function() {
		add_support_button_if_needed();
	}, 500);
	
	// Also try when frappe is ready
	if (typeof frappe !== 'undefined') {
		frappe.ready(function() {
			setTimeout(add_support_button_if_needed, 500);
		});
	}
});

// Set up form event listener
if (typeof frappe !== 'undefined' && frappe.ui && frappe.ui.form) {
	frappe.ui.form.on('*', {
		refresh: function(frm) {
			console.log('Form refresh triggered for:', frm.doc ? frm.doc.doctype : 'unknown');
			setTimeout(function() {
				add_support_button_if_needed(frm);
			}, 100);
		}
	});

	// Also, listen for global route changes to hide the button on non-form views like lists.
	if (frappe.router) {
		frappe.router.on('change', () => {
			const route = frappe.get_route();
			// If the new route is not a Form view, ensure the button is removed.
			if (!route || route[0] !== 'Form') {
				$('#global-support-btn').remove();
				console.log('Route changed to a non-Form view, removing support button.');
			}
		});
	}
}

function add_support_button_if_needed(frm) {
	console.log('Checking if support button should be added...');

	// New check: Only run on Form views, not List views.
	const route = frappe.get_route();
	if (!route || route[0] !== 'Form') {
		// If we are not in a form view, ensure the button is removed and stop.
		$('#global-support-btn').remove();
		console.log('Not in a Form view, skipping or removing support button.');
		return;
	}

	// Get current form if not provided
	if (!frm && typeof cur_frm !== 'undefined') {
		frm = cur_frm;
	}

	// Don't add button on HD Ticket itself
	if (frm.doc.doctype === 'HD Ticket') {
		$('#global-support-btn').remove(); // Also remove if it exists
		console.log('Skipping support button on HD Ticket form');
		return;
	}
	
	// Check if button already exists
	if (document.getElementById('global-support-btn')) {
		console.log('Support button already exists, skipping');
		return;
	}
	
	console.log('Adding support button for:', frm.doc.doctype);
	
	// Add floating support button
	add_floating_support_button(frm);
}

/**
 * Add floating support button (pill style)
 */
function add_floating_support_button(frm) {
	const supportHTML = `
		<style>
			/* Global Support Button - Floating Pill */
			#global-support-btn {
				position: fixed;
				bottom: 24px;
				right: 24px;
				display: flex;
				align-items: center;
				gap: 8px;
				padding: 12px 20px;
				background: #1c1c1a;
				color: #ffffff;
				border: none;
				border-radius: 999px;
				font-size: 15px;
				font-weight: 500;
				cursor: pointer;
				transition: background 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease;
				z-index: 999;
				box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
			}
			
			#global-support-btn:hover {
				background: #333330;
				transform: translateY(-2px);
				box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
			}
			
			#global-support-btn:active {
				transform: scale(0.97);
			}
			
			#global-support-btn svg {
				width: 20px;
				height: 20px;
				flex-shrink: 0;
			}
			
			/* Prevent button from overlapping with other fixed elements */
			@media (max-width: 768px) {
				#global-support-btn {
					bottom: 16px;
					right: 16px;
					padding: 10px 16px;
					font-size: 14px;
				}
				
				#global-support-btn svg {
					width: 18px;
					height: 18px;
				}
			}
		</style>
		
		<button id="global-support-btn" type="button">
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>
				<path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path>
			</svg>
			<span>Support</span>
		</button>
	`;
	
	// Append to body
	$('body').append(supportHTML);
	
	// Add click handler
	$('#global-support-btn').off('click').on('click', function() {
		// Always use the current form context (`cur_frm`) when the button is clicked.
		// This ensures that even when navigating between forms, we get the correct document details.
		if (typeof cur_frm !== 'undefined' && cur_frm.doc) {
			create_support_ticket(cur_frm);
		} else {
			frappe.msgprint(__('Could not find the current form. Please refresh the page.'));
		}
	});
}

/**
 * Create HD Ticket from current form - Opens dialog like Sales Invoice
 */
function create_support_ticket(frm) {
	// Prevent duplicate dialog
	if (document.getElementById('global-support-overlay')) return;

	// Prepare ticket data
	const doctype_name = frm.doc.doctype;
	const doc_name = frm.doc.name;
	const doc_title = frm.doc.name || frm.doc.title || frm.doc.subject || '';
	
	// Get module based on current doctype (using our mapping)
	const module = get_module_for_doctype(doctype_name);
	
	// Auto-generate subject like "Support request for Sales Order: SO250029-1"
	const auto_subject = `Support request for ${doctype_name}: ${doc_title}`;

	const supportHTML = `
        <style>
          /* Global Support Dialog - Same as Sales Invoice */
          .global-support-overlay {
            display:none;
            position:fixed;
            inset:0;
            background:rgba(0,0,0,0.45);
            align-items:center;
            justify-content:center;
            z-index:1000;
            padding:16px;
          }
          .global-support-overlay.open { display:flex; }
        
          .global-support-dialog {
            width:100%;
            max-width:420px;
            background:#ffffff;
            border-radius:12px;
            border:0.5px solid #e4e3dd;
            box-shadow:0 20px 50px rgba(0,0,0,0.2);
            overflow:hidden;
            animation:globalSupportPop .15s ease;
            text-align: left;
            font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
            color:#1c1c1a;
          }
          @keyframes globalSupportPop {
            from{ opacity:0; transform:translateY(8px) scale(.98); }
            to{ opacity:1; transform:translateY(0) scale(1); }
          }
        
          .global-support-dialog-header {
            display:flex;
            align-items:center;
            justify-content:space-between;
            padding:1rem 1.25rem;
            border-bottom:0.5px solid #e4e3dd;
          }
          .global-support-dialog-header h3 {
            margin:0;
            font-size:16px;
            font-weight:500;
            display:flex;
            align-items:center;
            gap:10px;
            color:#1c1c1a;
          }
          .global-support-dialog-header h3 svg { width:20px; height:20px; color:#0c447c; }
          .global-support-close-btn {
            background:none;
            border:none;
            cursor:pointer;
            color:#9a9a94;
            padding:4px;
            line-height:0;
            border-radius:6px;
          }
          .global-support-close-btn:hover { color:#1c1c1a; }
        
          .global-support-dialog-body {
            padding:1.25rem;
            display:flex;
            flex-direction:column;
            gap:16px;
          }
        
          .global-support-field label {
            display:block;
            font-size:13px;
            color:#6b6b66;
            margin-bottom:6px;
          }
          .global-support-field select,
          .global-support-field input[type="text"],
          .global-support-field textarea {
            width:100%;
            height:36px;
            padding:0 12px;
            font-size:14px;
            border:0.5px solid #c9c8c0;
            border-radius:8px;
            background:#fff;
            color:#1c1c1a;
            font-family:inherit;
            outline:none;
            transition:border-color .15s ease, box-shadow .15s ease;
            box-sizing: border-box;
          }
          .global-support-field select:focus,
          .global-support-field input[type="text"]:focus,
          .global-support-field textarea:focus {
            border-color:#0c447c;
            box-shadow:0 0 0 3px rgba(12,68,124,0.12);
          }
          .global-support-field textarea { height:auto; min-height:72px; padding:10px 12px; resize:vertical; }
        
          /* screenshot attach dropzone */
          .global-support-dropzone {
            border:1px dashed #c9c8c0;
            border-radius:8px;
            padding:20px;
            text-align:center;
            cursor:pointer;
            color:#9a9a94;
            transition:border-color .15s ease, background .15s ease;
          }
          .global-support-dropzone:hover, .global-support-dropzone.dragover {
            border-color:#0c447c;
            background:rgba(12,68,124,0.04);
          }
          .global-support-dropzone svg { width:22px; height:22px; margin-bottom:6px; }
          .global-support-dropzone p { margin:0; font-size:13px; }
          .global-support-dropzone input { display:none; }
        
          .global-support-file-preview {
            display:none;
            align-items:center;
            gap:10px;
            margin-top:10px;
            padding:8px 10px;
            border:0.5px solid #e4e3dd;
            border-radius:8px;
            font-size:13px;
          }
          .global-support-file-preview.show { display:flex; }
          .global-support-file-preview img {
            width:36px; height:36px; object-fit:cover; border-radius:4px; flex-shrink:0;
          }
          .global-support-file-preview .name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
          .global-support-file-preview button {
            background:none; border:none; cursor:pointer; color:#9a9a94; padding:2px;
          }
          .global-support-file-preview button:hover { color:#a32d2d; }
        
          .global-support-dialog-footer {
            display:flex;
            justify-content:flex-end;
            gap:10px;
            padding:1rem 1.25rem;
            border-top:0.5px solid #e4e3dd;
          }
          .global-support-btn-action {
            padding:8px 16px;
            font-size:14px;
            font-weight:500;
            border-radius:8px;
            cursor:pointer;
            border:0.5px solid #c9c8c0;
            background:#fff;
            color:#1c1c1a;
            transition:background .15s ease;
          }
          .global-support-btn-action:hover { background:#f5f5f2; }
          .global-support-btn-primary {
            background:#1c1c1a;
            border-color:#1c1c1a;
            color:#ffffff;
          }
          .global-support-btn-primary:hover { background:#333330; }
        </style>
        
        <!-- Global Support Dialog -->
        <div class="global-support-overlay" id="global-support-overlay">
          <div class="global-support-dialog" role="dialog" aria-modal="true" aria-labelledby="global-dialog-title">
        
            <div class="global-support-dialog-header">
              <h3 id="global-dialog-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.93 4.93a10 10 0 1 1 0 14.14M12 8v4l3 3"/></svg>
                Raise a support ticket
              </h3>
              <button class="global-support-close-btn" id="global-support-close-btn" aria-label="Close" type="button">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
              </button>
            </div>
        
            <form class="global-support-dialog-body" id="global-support-ticket-form">
        
              <div class="global-support-field">
                <label for="global-support-module">Module</label>
                <select id="global-support-module" required>
                  <option value="" disabled selected>Select a module</option>
                  <option>Accounts</option>
                  <option>Selling</option>
                  <option>Buying</option>
                  <option>Stock</option>
                  <option>HR</option>
                  <option>Manufacturing</option>
                  <option>CRM</option>
                  <option>Projects</option>
                  <option>Support</option>
                  <option>Assets</option>
                  <option>Quality</option>
                </select>
              </div>
        
              <div class="global-support-field">
                <label for="global-support-subject">Subject</label>
                <input type="text" id="global-support-subject" placeholder="Briefly describe the issue" required>
              </div>
        
              <div class="global-support-field">
                <label for="global-support-description">Description</label>
                <textarea id="global-support-description" placeholder="Add any extra detail that will help us resolve this"></textarea>
              </div>
        
              <div class="global-support-field">
                <label>Screenshot</label>
                <div class="global-support-dropzone" id="global-support-dropzone">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05 12.25 20.24a5 5 0 0 1-7.07-7.07L14.68 3.55a3.5 3.5 0 0 1 4.95 4.95L10.13 18a2 2 0 0 1-2.83-2.83l8.49-8.49"/></svg>
                  <p>Attach a file or drag it here</p>
                  <input type="file" id="global-support-screenshot" accept="image/*">
                </div>
                <div class="global-support-file-preview" id="global-support-file-preview">
                  <img id="global-support-preview-img" src="" alt="">
                  <span class="name" id="global-support-preview-name"></span>
                  <button type="button" id="global-support-clear-file" aria-label="Remove file">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
                  </button>
                </div>
              </div>
        
            </form>
        
            <div class="global-support-dialog-footer">
              <button type="button" class="global-support-btn-action" id="global-support-cancel-btn">Cancel</button>
              <button type="submit" form="global-support-ticket-form" class="global-support-btn-action global-support-btn-primary" id="global-support-submit-btn">Create ticket</button>
            </div>
        
          </div>
        </div>`;

	$(document.body).append(supportHTML);

	const overlay = document.getElementById('global-support-overlay');
	const dropzone = document.getElementById('global-support-dropzone');
	const fileInput = document.getElementById('global-support-screenshot');
	const filePreview = document.getElementById('global-support-file-preview');
	const previewImg = document.getElementById('global-support-preview-img');
	const previewName = document.getElementById('global-support-preview-name');
	const form = document.getElementById('global-support-ticket-form');
	const moduleSelect = document.getElementById('global-support-module');
	const subjectInput = document.getElementById('global-support-subject');

	// Auto-select module and set subject
	moduleSelect.value = module;
	subjectInput.value = auto_subject;

	// Show dialog
	overlay.classList.add('open');

	const closeDialog = () => {
		overlay.classList.remove('open');
		setTimeout(() => {
			overlay.remove();
		}, 200);
	};

	// Event listeners
	document.getElementById('global-support-close-btn').addEventListener('click', closeDialog);
	document.getElementById('global-support-cancel-btn').addEventListener('click', closeDialog);
	
	overlay.addEventListener('click', (e) => { if (e.target === overlay) closeDialog(); });
	document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDialog(); });

	// File handling
	dropzone.addEventListener('click', () => fileInput.click());

	function showFile(file) {
		if (!file) return;
		previewName.textContent = file.name;
		const reader = new FileReader();
		reader.onload = (e) => { previewImg.src = e.target.result; };
		reader.readAsDataURL(file);
		filePreview.classList.add('show');
	}

	fileInput.addEventListener('change', () => {
		if (fileInput.files.length) showFile(fileInput.files[0]);
	});

	document.getElementById('global-support-clear-file').addEventListener('click', (e) => {
		e.stopPropagation();
		fileInput.value = '';
		filePreview.classList.remove('show');
	});

	// Drag and drop
	['dragenter', 'dragover'].forEach(evt =>
		dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add('dragover'); })
	);
	['dragleave', 'drop'].forEach(evt =>
		dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove('dragover'); })
	);
	dropzone.addEventListener('drop', (e) => {
		const file = e.dataTransfer.files[0];
		if (file) {
			fileInput.files = e.dataTransfer.files;
			showFile(file);
		}
	});

	// Form submission
	form.addEventListener('submit', (e) => {
		e.preventDefault();

		const module_selected = document.getElementById('global-support-module').value;
		const subject = document.getElementById('global-support-subject').value;
		let description = document.getElementById('global-support-description').value || '';
		const file = fileInput.files[0];

		// Show loading state
		const submitBtn = document.getElementById('global-support-submit-btn');
		const originalBtnText = submitBtn.textContent;
		submitBtn.textContent = 'Creating...';
		submitBtn.disabled = true;

		frappe.call({
			method: 'frappe.client.insert',
			args: {
				doc: {
					doctype: 'HD Ticket',
					subject: subject,
					description: description,
					raised_by: frappe.session.user,
					custom_module: module_selected,
					module: module_selected,
					reference_doctype: doctype_name,
					reference_name: doc_name,
					custom_reference_document: doctype_name,
					custom_reference_document_name: doc_name
				}
			},
			freeze: true,
			callback: function (r) {
				if (r.message) {
					const ticket_name = r.message.name;

					if (file) {
						// Upload file
						const formData = new FormData();
						formData.append('file', file, file.name);
						formData.append('doctype', 'HD Ticket');
						formData.append('docname', ticket_name);
						formData.append('is_private', 1);
						formData.append('fieldname', 'custom_screenshot_');
						formData.append('docfield', 'custom_screenshot_');
						formData.append('attached_to_field', 'custom_screenshot_');

						fetch('/api/method/upload_file', {
							method: 'POST',
							headers: {
								'X-Frappe-CSRF-Token': frappe.csrf_token
							},
							body: formData
						})
							.then(res => res.json())
							.then(data => {
								const file_url = data.message ? data.message.file_url : '';
								
								if (file_url) {
									frappe.call({
										method: 'frappe.client.set_value',
										args: {
											doctype: 'HD Ticket',
											name: ticket_name,
											fieldname: 'custom_screenshot_',
											value: file_url
										},
										callback: function(r) {
											frappe.msgprint({
												title: __('Success'),
												indicator: 'green',
												message: __('Support Ticket {0} created successfully with attachment.', ['<b>' + ticket_name + '</b>'])
											});
											closeDialog();
										}
									});
								} else {
									frappe.msgprint({
										title: __('Warning'),
										indicator: 'orange',
										message: __('Ticket {0} created, but failed to retrieve attachment URL.', ['<b>' + ticket_name + '</b>'])
									});
									closeDialog();
								}
								
								submitBtn.textContent = originalBtnText;
								submitBtn.disabled = false;
							})
							.catch(err => {
								frappe.msgprint({
									title: __('Warning'),
									indicator: 'orange',
									message: __('Ticket {0} created, but failed to upload attachment.', ['<b>' + ticket_name + '</b>'])
								});
								closeDialog();
								submitBtn.textContent = originalBtnText;
								submitBtn.disabled = false;
							});
					} else {
						frappe.msgprint({
							title: __('Success'),
							indicator: 'green',
							message: __('Support Ticket {0} created successfully.', ['<b>' + ticket_name + '</b>'])
						});
						closeDialog();
						submitBtn.textContent = originalBtnText;
						submitBtn.disabled = false;
					}
				} else {
					submitBtn.textContent = originalBtnText;
					submitBtn.disabled = false;
				}
			},
			error: function (err) {
				submitBtn.textContent = originalBtnText;
				submitBtn.disabled = false;
			}
		});
	});
}

/**
 * Get module based on doctype (same mapping as auto-module detection)
 */
function get_module_for_doctype(doctype) {
	const DOCTYPE_MODULE_MAPPING = {
		// HR Module
		'Attendance': 'HR',
		'Employee': 'HR',
		'Leave Application': 'HR',
		'Leave Type': 'HR',
		'Salary Slip': 'HR',
		'Salary Structure': 'HR',
		'Appraisal': 'HR',
		'Training Event': 'HR',
		'Job Applicant': 'HR',
		'Job Opening': 'HR',
		'Payroll Entry': 'HR',
		'Shift Type': 'HR',
		'Shift Assignment': 'HR',
		
		// Accounts Module
		'Sales Order': 'Accounts',
		'Sales Invoice': 'Accounts',
		'Purchase Order': 'Accounts',
		'Purchase Invoice': 'Accounts',
		'Payment Entry': 'Accounts',
		'Journal Entry': 'Accounts',
		'Customer': 'Accounts',
		'Supplier': 'Accounts',
		'Account': 'Accounts',
		'Cost Center': 'Accounts',
		'Payment Request': 'Accounts',
		'POS Invoice': 'Accounts',
		
		// Stock Module
		'Item': 'Stock',
		'Stock Entry': 'Stock',
		'Delivery Note': 'Stock',
		'Purchase Receipt': 'Stock',
		'Material Request': 'Stock',
		'Warehouse': 'Stock',
		'Stock Reconciliation': 'Stock',
		'Packing Slip': 'Stock',
		
		// CRM Module
		'Lead': 'CRM',
		'Opportunity': 'CRM',
		'Campaign': 'CRM',
		'Prospect': 'CRM',
		
		// Projects Module
		'Project': 'Projects',
		'Task': 'Projects',
		'Timesheet': 'Projects',
		'Project Template': 'Projects',
		
		// Manufacturing Module
		'Work Order': 'Manufacturing',
		'BOM': 'Manufacturing',
		'Production Plan': 'Manufacturing',
		'Job Card': 'Manufacturing',
		
		// Support Module
		'Issue': 'Support',
		'Warranty Claim': 'Support',
		
		// Selling Module
		'Quotation': 'Selling',
		'Sales Partner': 'Selling',
		
		// Buying Module
		'Supplier Quotation': 'Buying',
		'Request for Quotation': 'Buying',
		
		// Asset Module
		'Asset': 'Assets',
		'Asset Maintenance': 'Assets',
		'Asset Repair': 'Assets',
		
		// Quality Module
		'Quality Inspection': 'Quality',
		'Quality Goal': 'Quality',
	};
	
	return DOCTYPE_MODULE_MAPPING[doctype] || 'Support';
}
