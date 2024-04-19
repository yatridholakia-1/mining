// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Batch Packing", {
	refresh(frm) {
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["batch_state", "=", "Production"]
                ]
            }
        });

        frm.set_query("production_warehouse", function() {
            return {
                filters: [
                    ["Warehouse", "warehouse_type", "=", "Production Warehouse"]
                ]
            }
        });
	},
    qc_accepted_qty(frm){
        frm.set_value("packing_quantity", frm.doc.qc_accepted_qty)
    }
});
