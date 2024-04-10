

frappe.listview_settings['Batch'] = {
    add_fields: ["batch_state"],
    get_indicator: function(doc) {
            var indicator = [__(doc.batch_state), frappe.utils.guess_colour(doc.batch_state), "status,=," + doc.batch_state];
            if(doc.batch_state=="Created") {
                    indicator[1] = "yellow";
            }
            if(doc.batch_state=="Blend Assigned") {
                indicator[1] = "blue";
            }
            if(doc.batch_state=="Production") {
                indicator[1] = "purple";
            }
            if(doc.batch_state=="Delivered") {
                indicator[1] = "green";
            }
            return indicator;
    },
};