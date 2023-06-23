frappe.ui.form.on("Sales Order Item", "item_code", function(frm, cdt, cdn) {

    let row = frappe.get_doc(cdt, cdn);
    frappe.call({
        method: "fashion_navya.utils.doc_event.sales_order.show_live_update",
        args: {
            item: row['item_code'],
            customer:cur_frm.doc.customer

        },
        callback: function(r) {
            console.log(r.message,999)
              if(r.message){
                row['delivery_date']=r.message
            }

            if (r.message) {


            }


        }
    });
});


