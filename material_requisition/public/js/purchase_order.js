// Custom script for Purchase Order to add Promep navigation
frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {
        // Add custom button to open related Material Request in Promep
        if (frm.doc.name && !frm.doc.__islocal) {
            // Check if this PO has related Material Requests
            const material_requests = get_material_requests_from_po(frm);
            
            if (material_requests.length > 0) {
                // If single MR, direct link
                if (material_requests.length === 1) {
                    frm.add_custom_button(__('View in Promep'), function() {
                        const promep_url = `/promep/request/${material_requests[0]}`;
                        window.open(promep_url, '_blank');
                    }, __('Actions'));
                } else {
                    // If multiple MRs, show submenu
                    material_requests.forEach(mr => {
                        frm.add_custom_button(mr, function() {
                            const promep_url = `/promep/request/${mr}`;
                            window.open(promep_url, '_blank');
                        }, __('View in Promep'));
                    });
                }
            } else {
                // If no specific MR, link to line items view for PO creation
                frm.add_custom_button(__('Open Promep'), function() {
                    const promep_url = `/promep/line-items`;
                    window.open(promep_url, '_blank');
                }, __('Actions'));
            }
            
            // Add icons to buttons
            setTimeout(() => {
                const buttons = frm.page.btn_secondary.find(`[data-label*="Promep"]`);
                buttons.each(function() {
                    if (!$(this).find('.fa-external-link').length) {
                        $(this).prepend('<i class="fa fa-external-link" style="margin-right: 5px;"></i>');
                    }
                });
            }, 100);
        }
    }
});

function get_material_requests_from_po(frm) {
    const material_requests = new Set();
    
    // Check items for material_request references
    if (frm.doc.items) {
        frm.doc.items.forEach(item => {
            if (item.material_request) {
                material_requests.add(item.material_request);
            }
        });
    }
    
    return Array.from(material_requests);
}
