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
    for_quantity(frm){
        frm.set_value("accepted_quantity", "");
        frm.set_value("rejected_quantity", "");
        frm.set_value("quality_reject_reason", "");
    },
    accepted_quantity(frm){
        let new_rejected_quantity = frm.doc.for_quantity - frm.doc.accepted_quantity;
        if (new_rejected_quantity < 0){
            frappe.throw("Accepted Quantity cannot be more than: " + frm.doc.for_quantity, title="Error")
        }
        if (frm.doc.rejected_quantity !== new_rejected_quantity) {
            frm.set_value("rejected_quantity", new_rejected_quantity);
        }
    },
    rejected_quantity(frm){
        let new_accepted_quantity = frm.doc.for_quantity - frm.doc.rejected_quantity;
        if (new_accepted_quantity < 0){
            frappe.throw("Rejected Quantity cannot be more than: " + frm.doc.for_quantity, title="Error")
        }
        if (frm.doc.accepted_quantity !== new_accepted_quantity) {
            frm.set_value("accepted_quantity", new_accepted_quantity);
        }
    }
});
