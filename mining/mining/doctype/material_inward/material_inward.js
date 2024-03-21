// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

const filter_material_type = (frm) => {
    if (frm.doc.material_type){
        frm.set_query("material", function() {
            return {
                filters: [
                    ["material_type", "=", frm.doc.material_type]
                ]
            }
        });
    }
}
frappe.ui.form.on("Material Inward", {
        refresh(frm) {
            filter_material_type(frm)
        },
        material_type(frm) {
            frm.set_value("material", "")
            filter_material_type(frm)
        }
});
