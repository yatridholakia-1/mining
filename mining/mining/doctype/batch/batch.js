// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

const KILO_TO_MT_CONVERSTION_FACTOR = parseFloat("1000")

frappe.ui.form.on("Batch", {
    
        refresh: function(frm){
            //Filter in Child Table Materils Required
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

            //Add "Assign Blend" Custom Button
            if (frm.doc.docstatus === 1 && frm.doc.batch_state === "Created") {
                frm.add_custom_button(__("Assign Blend"), function(){
                    frappe.new_doc('Assign Blend', {
                        'batch': frm.doc.batch_code
                    });
                  });
            }

            //Set Validations in Date Picker
            if (frm.doc.docstatus !== 1) {
                frm.fields_dict.expected_production_completion_date.datepicker.update({
                    minDate: new Date(frappe.datetime.get_today())
                });
                frm.fields_dict.expected_dispatch_date.datepicker.update({
                    minDate: new Date(frappe.datetime.get_today())
                });
        }
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
