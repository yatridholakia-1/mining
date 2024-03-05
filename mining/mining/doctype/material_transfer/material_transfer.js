// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

const production_warehouse_filter = (frm, warehouse) => {
    frm.set_query(warehouse, "material_transfer", function(doc, cdt, cdn) {
        return {
            filters: [
                ["Warehouse", "warehouse_type", "=", "Production Warehouse"]
            ]
        }
    });
}

const clear_child_table = (frm) => {
    frm.clear_table('material_transfer')
    frm.refresh_field('material_transfer');
}


frappe.ui.form.on("Material Transfer", {
	refresh(frm) {
        //Filter in Batch Field, Batch status should be "Created"
        frm.set_query("batch", function() {
            return {
                filters: [
                    ["batch_state", "in", ["Created", "Production"]]
                ]
            }
        });

        frm.set_query("material", "material_transfer", function(doc, cdt, cdn) {
            return {
                filters: [
                    ["Material", "material_type", "in", ["Bag", "Pallet", "Polymer"]]
                ]
            }
        });
	},

    type: function(frm) {
        clear_child_table(frm)
        if (frm.doc.type == "Material Issue") {
            production_warehouse_filter(frm, "target_warehouse")
        }
        else if (frm.doc.type == "Material Return") {
            production_warehouse_filter(frm, "source_warehouse")
        }

    },

    batch: function(frm) {
        clear_child_table(frm)
        if (frm.doc.batch) {
            frappe.model.with_doc('Batch', frm.doc.batch, function() {
                let batch_doc = locals['Batch'][frm.doc.batch]
        
                if (batch_doc && batch_doc.batch_materials_required) {
                    let materials_required = batch_doc.batch_materials_required.map(function(row) {
                        return row.material;
                    });
        
                    frm.set_query("material", "material_transfer", function(doc, cdt, cdn) {
                        return {
                            filters: [
                                ["Material", "material_code", "in", materials_required]
                            ]
                        };
                    });
                }
            });
        }


    }
});

frappe.ui.form.on('Material Transfer Child', {
	refresh(frm) {
		
	},
    material_transfer_add(frm, cdt, cdn){
        if (!frm.doc.type){
            frappe.throw("Please Select Material Transfer Type To Continue.")
        }
        else if(frm.doc.type == "Material Issue"){
            row = locals[cdt][cdn]
            row.source_warehouse = "Store"
            frm.refresh_field('material_transfer');
            
        }
        else if(frm.doc.type == "Material Return"){
            row = locals[cdt][cdn]
            row.target_warehouse = "Store"
            frm.refresh_field('material_transfer');
        }

        if (!frm.doc.batch){
            frappe.throw("Please Select Batch To Continue.")
        }
    }
})