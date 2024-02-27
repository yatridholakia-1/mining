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
	},
});
