// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Dispatch", {
	refresh(frm) {
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["batch_state", "=", "Production"]
                ]
            }
        });

	},
    packed_qty(frm){
        frm.set_value("quantity", frm.doc.packed_qty)
    }
});
