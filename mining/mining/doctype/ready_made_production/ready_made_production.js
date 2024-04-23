// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Ready-Made Production", {
	refresh(frm) {
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["ready_made_product", "=", true]
                ]
            }
        });
	},
});
