// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material", {
	refresh(frm) {
        if(frappe.user.has_role("System Manager") || frappe.user.has_role("Managing Director") || frappe.user.has_role("Purchase Manager")){
                frm.add_custom_button(__("Pack"), function(){
                    frappe.new_doc('Material Inward', {
                        'material_code': frm.doc.material,
                        'material_type': frm.doc.material_type
                    });
                }, __("Actions"));
            }
        }
});
