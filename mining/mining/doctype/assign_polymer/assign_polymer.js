// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Assign Polymer", {
	refresh(frm) {
          //Filter in Child Table Materils Required
          frm.set_query("polymer", "polymers", function(doc, cdt, cdn) {
            return {
                filters: [
                    ["Material", "material_type", "=", "Polymer"]
                ]
            }
        })

        //Filter in Batch Field, Batch status should be "Created"
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["batch_state", "=", "Blend Assigned"]
                ]
            }
        })

        //Re-Assign Blend Custom Button
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Re-Assign Polymer"), function(){
                frappe.new_doc('Assign Polymer', {
                    'batch': frm.doc.batch,
                    'reassigned_from': frm.doc.name
                });
                });
        }
    }
});
