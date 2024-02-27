// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

const update_total_percentage = (frm) => {
    let total_cents = flt(0)
    $.each(frm.doc.lumps, function(i, row) {
        total_cents += flt(row.percentage)
    });

    $.each(frm.doc.blend, function(i, row) {
        total_cents += flt(row.percentage)
    });

    frm.set_value("total_percentage", total_cents)
}

frappe.ui.form.on("Blend", {
       
    refresh: function(frm){
         //Add "Assign Blend" Custom Button
         if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Assign To Batch"), function(){
                frappe.new_doc('Assign Blend', {
                    'blend': frm.doc.blend_code
                });
              });
        }

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
	},

    before_save: function(frm){
        update_total_percentage(frm);
    }

});
