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

                  if(r.message[1]!="POS"){
                    row['delivery_date']=r.message[0]
                    row['delivery_order']=r.message[1]
                  }

                  if(r.message[1]=="POS"){
                    frappe.msgprint("Please handle by POS")
                    var idx=row['idx']-1
                    console.log(row['idx'],'idx')
                    cur_frm.get_field("items").grid.grid_rows[idx].remove();
                    row['item_code']=undefined


                  }



            }

            if (r.message) {


            }


        }
    });
});


frappe.ui.form.on("Sales Order", "refresh", function(frm) {
    frm.fields_dict['sample_table'].grid.get_field('item').get_query = function(doc, cdt, cdn) {
        var child = locals[cdt][cdn];
        //console.log(child);
        return {    
            filters:[
                ['item_group', '=',"Sample"]
            ]
        }
    }
});

