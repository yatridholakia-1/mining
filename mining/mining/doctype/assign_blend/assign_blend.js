// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assign Blend", {
	refresh(frm) {
        //Filter in Batch Field, Batch status should be "Created"
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["batch_state", "=", "Created"]
                ]
            }
        });

        //Re-Assign Blend Custom Button
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Re-Assign Blend"), function(){
                frappe.new_doc('Assign Blend', {
                    'batch': frm.doc.batch,
                    'reassigned_from': frm.doc.name
                });
              });
        }
	},
});
