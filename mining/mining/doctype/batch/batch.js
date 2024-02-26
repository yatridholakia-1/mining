// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

const KILO_TO_MT_CONVERSTION_FACTOR = parseFloat("1000")

frappe.ui.form.on("Batch", {
    //Filter in Child Table Materils Required
        refresh: function(frm){
            frm.set_query("material", "batch_materials_required", function(doc, cdt, cdn) {
                return {
                    filters: [
                        ["Material", "material_type", "in", ["Bag", "Pallet"]]
                    ]
                }
            });

            //Filter in Product Code Field
            frm.set_query("product_code", function() {
                return {
                    filters: [
                        ["material_type", "=", "Product"]
                    ]
                }
            });

            //Set Validations in Date Picker
            frm.fields_dict.expected_production_completion_date.datepicker.update({
                minDate: new Date(frappe.datetime.get_today())
            });
            frm.fields_dict.expected_dispatch_date.datepicker.update({
                minDate: new Date(frappe.datetime.get_today())
            });
    }
});


frappe.ui.form.on('Batch Materials Required', {
	material: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
		if(row.bag_size && frm.doc.product_quantity){
            bag_size_in_mt = row.bag_size / KILO_TO_MT_CONVERSTION_FACTOR;
            estimated_bag_qt =  frm.doc.product_quantity / bag_size_in_mt;
            row.quantity = estimated_bag_qt
            frm.refresh_field("batch_materials_required")
        }
	}
})
