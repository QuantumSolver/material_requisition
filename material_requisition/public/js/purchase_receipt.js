// Custom script for Purchase Receipt to add Promep navigation
frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        // Add custom button to open in Promep
        if (frm.doc.name && !frm.doc.__islocal) {
            frm.add_custom_button(__('Open in Promep'), function() {
                // Open Promep Purchase Receipt detail page in new tab
                const promep_url = `/promep/receipt/${frm.doc.name}`;
                window.open(promep_url, '_blank');
            }, __('Actions'));
            
            // Check if this receipt has related Material Requests
            const material_requests = get_material_requests_from_receipt(frm);
            
            if (material_requests.length > 0) {
                // If single MR, direct link
                if (material_requests.length === 1) {
                    frm.add_custom_button(__('View Material Request in Promep'), function() {
                        const promep_url = `/promep/request/${material_requests[0]}`;
                        window.open(promep_url, '_blank');
                    }, __('Actions'));
                } else {
                    // If multiple MRs, show submenu
                    material_requests.forEach(mr => {
                        frm.add_custom_button(mr, function() {
                            const promep_url = `/promep/request/${mr}`;
                            window.open(promep_url, '_blank');
                        }, __('View Material Requests in Promep'));
                    });
                }
            }
            
            // Check if this receipt has related Purchase Orders
            const purchase_orders = get_purchase_orders_from_receipt(frm);
            
            if (purchase_orders.length > 0) {
                // If single PO, direct link
                if (purchase_orders.length === 1) {
                    frm.add_custom_button(__('View Purchase Order in Promep'), function() {
                        const promep_url = `/promep/purchase-order/${purchase_orders[0]}`;
                        window.open(promep_url, '_blank');
                    }, __('Actions'));
                } else {
                    // If multiple POs, show submenu
                    purchase_orders.forEach(po => {
                        frm.add_custom_button(po, function() {
                            const promep_url = `/promep/purchase-order/${po}`;
                            window.open(promep_url, '_blank');
                        }, __('View Purchase Orders in Promep'));
                    });
                }
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

function get_material_requests_from_receipt(frm) {
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

function get_purchase_orders_from_receipt(frm) {
    const purchase_orders = new Set();
    
    // Check items for purchase_order references
    if (frm.doc.items) {
        frm.doc.items.forEach(item => {
            if (item.purchase_order) {
                purchase_orders.add(item.purchase_order);
            }
        });
    }
    
    return Array.from(purchase_orders);
}
