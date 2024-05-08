// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material", {
	refresh(frm) {
		   //Material Inward
		   if(frappe.user.has_role("System Manager") || frappe.user.has_role("Managing Director") || frappe.user.has_role("Purchase Manager")){
			if(!frm.is_new()){
				frm.add_custom_button(__("Material Inward"), function(){
					frappe.new_doc('Material Inward', {
						
						'material_type': frm.doc.material_type,
						'material' : frm.doc.material_code
					});
				}, __("Actions"));
			}
		}
	}
});
