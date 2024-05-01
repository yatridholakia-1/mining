// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

const KILO_TO_MT_CONVERSTION_FACTOR = parseFloat("1000")
const change_batch_state = (frm, state) => {
    frm.set_value("batch_state", state)
}
const update_batch_state = (frm) => {
    if (frm.doc.total_produced_qty > 0) {
        change_batch_state(frm, "Production")
    }
    if (frm.doc.total_delivered_qty > total_required_qty) {
        change_batch_state(frm, "Delivered")
    }
}

frappe.ui.form.on("Batch", {
    
        refresh: function(frm){

            //Filter in Child Table Materils Required
            frm.set_query("material_type", "batch_materials_required", function(doc, cdt, cdn) {
                return {
                    filters: [
                        ["Material Type", "name", "in", ["Bag", "Pallet"]]
                    ]
                }
            });
            
            //Filter based on material type selected
            
            frm.set_query('material', 'batch_materials_required', function(doc, cdt, cdn) {
                const row = locals[cdt][cdn];
                return {
                    filters: [
                        ["Material", "material_type", "=", row.material_type]
                    ]
                };
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
            if(frappe.user.has_role("System Manager") || frappe.user.has_role("Lab Manager") || frappe.user.has_role("Managing Director")){
                if (frm.doc.docstatus === 1 && frm.doc.blend_insights.length === 0) {
                    frm.add_custom_button(__("Assign Blend"), function(){
                        frappe.new_doc('Assign Blend', {
                            'batch': frm.doc.batch_code
                        });
                    }, __("Actions"));
                }

            //Add "Assign Polymer" Custom Button
            if (frm.doc.docstatus === 1 && frm.doc.blend_insights.length !== 0 && frm.doc.batch_polymer_insights.length === 0) {
                frm.add_custom_button(__("Assign Polymer"), function(){
                    frappe.new_doc('Assign Polymer', {
                        'batch': frm.doc.batch_code
                    });
                    }, __("Actions"));
            }
        }

            //Show Material Transfer in Batch
            if(frappe.user.has_role("System Manager") || frappe.user.has_role("Store Manager") || frappe.user.has_role("Managing Director")){
                    frm.add_custom_button(__("Material Issue"), function(){
                        frappe.new_doc('Material Transfer', {
                            'batch': frm.doc.batch_code,
                            'type': "Material Issue"
                        });
                    }, __("Actions"));
                    frm.add_custom_button(__("Material Return"), function(){
                        frappe.new_doc('Material Transfer', {
                            'batch': frm.doc.batch_code,
                            'type': "Material Return"
                        });
                    }, __("Actions"));
                }

                //Show Production in Batch
                if(frappe.user.has_role("System Manager") || frappe.user.has_role("Production Manager") || frappe.user.has_role("Managing Director")){
                    if(frm.doc.docstatus === 1 && frm.doc.blend_insights.length !== 0){
                        frm.add_custom_button(__("Production"), function(){
                            frappe.new_doc('Production', {
                                'batch': frm.doc.batch_code
                            });
                        }, __("Actions"));
                        frm.add_custom_button(__("Ready-Made Production"), function(){
                            frappe.new_doc('Ready-Made Production', {
                                'batch': frm.doc.batch_code
                            });
                        }, __("Actions"));
                    }
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
    },
    total_delivered_qty(frm){
            let delivery_progress = (frm.doc.total_delivered_qty / frm.doc.total_required_qty) * 100;
            frm.set_value("delivery_progress", delivery_progress)
    }
});


frappe.ui.form.on('Batch Materials Required', {
    material_type: function(frm, cdt, cdn) {
      
         const row = locals[cdt][cdn];
        // frm.set_query('material', 'batch_materials_required', function() {
        //     return {
        //         filters: [
        //             ["Material", "material_type", "=", row.material_type]
        //         ]
        //     };
        // });
        // frm.refresh_field("batch_materials_required")
        frm.fields_dict['batch_materials_required'].get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                            ["Material", "material_type", "=", row.material_type]
                         ]
            };
        };
        
    },

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
