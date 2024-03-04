// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

const validation = frm => {
    frm.set_value("source_warehouse", "")
    frm.set_value("target_warehouse", "")
    if (frm.doc.stock_entry_for && frm.doc.stock_entry_for === "Batch") {
        if(frm.doc.stock_entry_type) {
            if (frm.doc.stock_entry_type === "Stock Out"){
                frm.set_value("source_warehouse", "Batch Warehouse")
            }
            else if (frm.doc.stock_entry_type === "Stock In"){
                frm.set_value("target_warehouse", "Batch Warehouse")
            }
        }
    }

    else if (frm.doc.stock_entry_for && frm.doc.stock_entry_for === "Blend") {
            if(frm.doc.stock_entry_type) {
                if (frm.doc.stock_entry_type === "Stock Out"){
                    frm.set_value("source_warehouse", "Blend Warehouse")
                }
                else if (frm.doc.stock_entry_type === "Stock In"){
                    frm.set_value("target_warehouse", "Blend Warehouse")
                }
            }
    }
    else if (frm.doc.stock_entry_for && frm.doc.stock_entry_for === "Material") {
        if(frm.doc.stock_entry_type) {
            if (frm.doc.stock_entry_type === "Stock Out"){
                frm.set_value("source_warehouse", "Store")
            }
            else if (frm.doc.stock_entry_type === "Stock In"){
                frm.set_value("target_warehouse", "Store")
            }
        }
}
}
frappe.ui.form.on("Stock Management", {
	refresh(frm) {
        //Filter in Child Table Materils Required
        frm.set_query("stock_entry_for", function(doc, cdt, cdn) {
            return {
                filters: [
                    ["DocType", "name", "in", ["Material", "Batch", "Blend"]]
                ]
            }
        });
	},
    stock_entry_type: function(frm){
       validation(frm)    
    },
    stock_entry_for: function(frm){
        validation(frm)  
    },
    validate(frm){
        if((frm.doc.stock_entry_type === "Stock Transfer") && (frm.doc.stock_entry_for === "Batch" || frm.doc.stock_entry_for === "Blend")){
            frappe.throw("Stock Transfer Not Allowed in Batch Or Blend")
        }
    }
});
