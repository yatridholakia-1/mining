// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bag Damage", {
	refresh(frm) {
        frm.set_query("production_warehouse", function() {
            return {
                filters: [
                    ["Warehouse", "warehouse_type", "=", "Production Warehouse"]
                ]
            }
        });

        frm.set_query("bag", function() {
            return {
                filters: [
                    ["material_type", "=", "Bag"]
                ]
            }
        });
	},
});
