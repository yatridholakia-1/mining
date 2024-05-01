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
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["batch_state", "in", ["Production", "Blend Assigned"]],
                    ["batch_state", "!=", "Delivered"]
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
    before_workflow_action: async function(frm) {
        if (frm.selected_workflow_action === 'Cancel') {
            // Create a promise to handle the confirmation dialog
            let promise = new Promise((resolve, reject) => {
                frappe.dom.unfreeze()
                frappe.confirm('Are you sure you want to cancel?',
                    () => resolve(), // If 'Yes', resolve the promise
                    () => reject()  // If 'No', reject the promise
                );
            });

            // Await the promise and catch any rejection
            await promise.catch(() => {
                frm.selected_workflow_action = null;
                frappe.msgprint('Cancellation aborted.');
                throw new Error('User cancelled the workflow action.'); // Prevent the workflow action
            });
        }
    }
});
