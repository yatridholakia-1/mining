// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Blend", {
       
    refresh: function(frm){
         //Filter in Lumps Table
            frm.set_query("lumps", "lumps", function(doc, cdt, cdn) {
                return {
                    filters: [
                        ["Material", "material_type", "=", "Lumps"]
                    ]
                }
            });

            //Filter in Polymer Table
            frm.set_query("polymer", "polymer", function(doc, cdt, cdn) {
                return {
                    filters: [
                        ["Material", "material_type", "=", "Polymer"]
                    ]
                }
            });
	}
});
