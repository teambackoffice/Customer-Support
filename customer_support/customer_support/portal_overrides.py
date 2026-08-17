import frappe

def inject_helpdesk_script(response, *args, **kwargs):
    """
    Injects a script into the Helpdesk Vue SPA to hide specific fields 
    (Customer, Team, Assignee) from the portal/agent view.
    This runs via the after_request hook.
    """
    if not hasattr(frappe.local, 'request'):
        return response
        
    if frappe.local.request.path.startswith("/helpdesk"):
        if hasattr(response, 'mimetype') and response.mimetype == "text/html":
            if isinstance(response.data, bytes):
                # The Helpdesk portal is a Vue SPA.
                # We use CSS for fields with IDs and MutationObserver for dynamically rendered components.
                script = """
                <style>
                /* Hide Customer and Team fields based on their IDs in the Vue app */
                #customer, #agent_group { display: none !important; }
                </style>
                <script>
                document.addEventListener('DOMContentLoaded', () => {
                    const observer = new MutationObserver((mutations) => {
                        // Handle the Assignee component which doesn't have an ID
                        document.querySelectorAll('span').forEach(span => {
                            const text = span.innerText.trim();
                            if (text === 'Assignee' && span.classList.contains('text-ink-gray-5')) {
                                // The span is inside <div class="flex flex-col gap-1.5 w-full">
                                if (span.parentElement) {
                                    span.parentElement.style.display = 'none';
                                }
                            }
                            
                            // Handle the customer-facing portal sidebar (just in case)
                            if (['Team', 'Customer', 'Assignee'].includes(text) && 
                               (span.classList.contains('text-ink-gray-5') || span.classList.contains('text-sm'))) {
                                const parentRow = span.closest('.flex.items-center.text-base.leading-5');
                                if (parentRow) {
                                    parentRow.style.display = 'none';
                                }
                            }
                        });
                    });
                    observer.observe(document.body, { childList: true, subtree: true });
                });
                </script>
                """
                # Inject just before the closing </body> tag
                response.data = response.data.replace(b"</body>", script.encode('utf-8') + b"</body>")
                
    return response
