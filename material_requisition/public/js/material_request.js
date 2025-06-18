// Custom script for Material Request to add Promep navigation
frappe.ui.form.on('Material Request', {
    refresh: function(frm) {
        // Add custom button to open in Promep
        if (frm.doc.name && !frm.doc.__islocal) {
            frm.add_custom_button(__('Open in Promep'), function() {
                // Open Promep Material Request detail page in new tab
                const promep_url = `/promep/request/${frm.doc.name}`;
                window.open(promep_url, '_blank');
            }, __('Actions'));
            
            // Add icon to the button
            setTimeout(() => {
                const button = frm.page.btn_secondary.find(`[data-label="${__('Open in Promep')}"]`);
                if (button.length) {
                    button.prepend('<i class="fa fa-external-link" style="margin-right: 5px;"></i>');
                }
            }, 100);
        }
    }
});
