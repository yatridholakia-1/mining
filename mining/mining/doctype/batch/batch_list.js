

frappe.listview_settings['Batch'] = {
    add_fields: ["batch_state", "delivery_progress","production_progress"],
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
            if(doc.batch_state=="Ready-Made Production") {
                indicator[1] = "orange";
            }
            if(doc.batch_state=="Delivered") {
                indicator[1] = "green";
            }
            return indicator;
    },
    refresh: function(listview) {
        listview.$page.find('.list-row-container .list-row').each(function() {
          // Assuming 'production_progress' and 'delivery_progress' are data-fieldnames for the progress bars
          var productionProgress = $(this).find('[data-fieldname="production_progress"] .progress-bar');
          var deliveryProgress = $(this).find('[data-fieldname="delivery_progress"] .progress-bar');
          
          // Set the progress bar color based on the field value
          if (productionProgress.length) {
            productionProgress.css('background-color', '#2063FE'); // Replace with your color code
          }
          if (deliveryProgress.length && deliveryProgress.text().trim() === 'Delivery') {
            deliveryProgress.css('background-color', '#FE7B20'); // Replace with your color code
          }
        });
      }
};

// frappe.listview_settings['Batch'] = {
//     add_fields: ["batch_state", "delivery_progress", "production_progress"],
//     get_indicator: function(doc) {
//       var indicator;
//       // First, handle the batch_state indicators
//       switch (doc.batch_state) {
//         case "Created":
//           indicator = [__(doc.batch_state), "yellow", "status,=," + doc.batch_state];
//           break;
//         case "Blend Assigned":
//           indicator = [__(doc.batch_state), "blue", "status,=," + doc.batch_state];
//           break;
//         case "Production":
//           indicator = [__(doc.batch_state), "purple", "status,=," + doc.batch_state];
//           break;
//         case "Ready-Made Production":
//           indicator = [__(doc.batch_state), "orange", "status,=," + doc.batch_state];
//           break;
//         case "Delivered":
//           indicator = [__(doc.batch_state), "green", "status,=," + doc.batch_state];
//           break;
//         default:
//           indicator = [__(doc.batch_state), "grey", "status,=," + doc.batch_state];
//           break;
//       }
  
//       // Then, handle the progress bar color based on delivery_progress
//       if (doc.delivery_progress) {
//         let progress_color = "red"; // default color
//         if (doc.delivery_progress <= 25) {
//           progress_color = "red";
//         } else if (doc.delivery_progress <= 50) {
//           progress_color = "orange";
//         } else if (doc.delivery_progress <= 75) {
//           progress_color = "yellow";
//         } else {
//           progress_color = "green";
//         }
//         indicator = [__(doc.delivery_progress + "%"), progress_color, "progress,=," + doc.delivery_progress];
//       }
  
//       return indicator;
//     }
//   };
  