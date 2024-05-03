// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt
const copy_planned_data = (frm) => {
    if(frm.doc.status === "Finished") {
        frm.set_value("actual_hours", frm.doc.expected_hours)
        frm.set_value("actual_quantity", frm.doc.expected_quantity)
        if(!frm.doc.external) {
            frm.doc.machines_required.forEach(function (row) {
                var newRow = frm.add_child('machines_used');
                newRow.machine = row.machine;
            });
            frm.refresh_fields('machines_used');
        }
    }
}
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
        if(frm.doc.workflow_state === "Pending" && frm.doc.status === "Finished"){
            if(frm.doc.actual_hours === 0 && frm.doc.actual_quantity === 0 && frm.doc.machines_used.length === 0){
                copy_planned_data(frm)
            }
        }
    },
    status(frm){
        copy_planned_data(frm)
    },
    workflow_state: function(frm) {
        // Your code here
        console.log("Workflow state changed to: " + frm.doc.workflow_state);
        // Call your function or write your logic here
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
        if (frm.selected_workflow_action === 'Finish'){
            copy_planned_data(frm)
        }
    }
});
