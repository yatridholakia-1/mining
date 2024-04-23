// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Batch Packing", {
	refresh(frm) {
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["batch_state", "in", ["Production", "Ready-Made Production"]]
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
        if (frm.doc.qc_accepted_qty) {
        frm.set_value("packing_quantity", frm.doc.qc_accepted_qty)
        }
    },
    batch(frm){
        if (frm.doc.readymade_batch){
            frm.set_value("production_warehouse", "Ready-Made Warehouse")
        }
    },
    pallet_required_qty(frm){
        if(frm.doc.pallet_required_qty) {
            frm.set_value("pallet_quantity", frm.doc.pallet_required_qty)
        }
    }
});
