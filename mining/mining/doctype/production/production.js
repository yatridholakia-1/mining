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
	},
});
