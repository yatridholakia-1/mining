// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt


frappe.ui.form.on("Batch Quality", {
	refresh(frm) {
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["batch_state", "=", "Production"]
                ]
            }
        });
	},
    accepted_quantity(frm){
        let new_rejected_quantity = frm.doc.for_quantity - frm.doc.accepted_quantity;
        if (frm.doc.rejected_quantity !== new_rejected_quantity) {
            frm.set_value("rejected_quantity", new_rejected_quantity);
        }
    },
    rejected_quantity(frm){
        let new_accepted_quantity = frm.doc.for_quantity - frm.doc.rejected_quantity;
        if (frm.doc.accepted_quantity !== new_accepted_quantity) {
            frm.set_value("accepted_quantity", new_accepted_quantity);
        }
    }
});
