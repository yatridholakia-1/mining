// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Production", {
	refresh(frm) {
        if(frm.is_new()){
            frm.set_value("batch_insights_row", "")
        }
        frm.set_query("production_warehouse", function() {
            return {
                filters: [
                    ["Warehouse", "warehouse_type", "=", "Production Warehouse"]
                ]
            }
        });

        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Machine Downtime"), function(){
                frappe.new_doc('Machine Downtime', {
                    
                });
              });
        }
	},
    before_workflow_action: function (frm) {
        if (frm.selected_workflow_action === 'Cancel') {
            frappe.confirm('Are you sure you want to cancel?',
                () => {
                    frm.doc.workflow_state = 'Cancelled';
                    frm.save();
                },
                () => {
                    frm.selected_workflow_action = null; 
                    return false;
                });
        }
    }


});
