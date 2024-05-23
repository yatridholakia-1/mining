// Copyright (c) 2024, ArkayApps and contributors
// For license information, please see license.txt

const deadstock_batch = (frm) => {
    if (frm.doc.docstatus === 0  && frm.doc.transfer_type === "Dead-Stock To Batch"){
            frappe.db.get_list('Stock Balance', {
                filters: [
                    ['warehouse', '=', 'Dead-Stock Warehouse'],
                    ['quantity', '>', 0]
                ],
                fields: ['entry_item']
            }).then(dead_batch_list => {
                console.log(dead_batch_list)
                frm.set_query("from_batch", function() {
                    return {
                        filters: [
                            ["batch_code", "in", dead_batch_list.map(item => item["entry_item"])]
                        ]
                    };
                });
            });
    }
}
frappe.ui.form.on("Batch Transfer", {
	refresh(frm) {
        deadstock_batch(frm)
	},
    transfer_type(frm){
        frm.set_value("from_batch", "")
        frm.set_value("to_batch", "")
        deadstock_batch(frm)
    } 
});
