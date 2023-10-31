frappe.ui.form.on("Sales Order Item", "item_code", function(frm, cdt, cdn) {

    let row = frappe.get_doc(cdt, cdn);
    var item_1=row['item_code']
    if(item_1 && cur_frm.doc.customer){
    frappe.call({
        method: "fashion_navya.utils.doc_event.sales_order.show_live_update",
        args: {
            item: item_1,
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
			row['delivery_date']=frappe.datetime.nowdate()
                    //frappe.msgprint("Please handle by POS")
                    //var idx=row['idx']-1
                    //console.log(row['idx'],'idx')
                    //cur_frm.get_field("items").grid.grid_rows[idx].remove();
                    //row['item_code']=undefined


                  }



            }

        


        }
    });
}
});


// frappe.ui.form.on("Sales Order", "refresh", function(frm) {
//     frm.fields_dict['sample_table'].grid.get_field('item').get_query = function(doc, cdt, cdn) {
//         var child = locals[cdt][cdn];
//         //console.log(child);
//         return {    
//             filters:[
//                 ['item_group', '=',"Sample"]
//             ]
//         }
//     }
// });

//delivery date set for customize item
frappe.ui.form.on("Sales Order Item", "item_code", function(frm, cdt, cdn) {

    var row = frappe.get_doc(cdt, cdn);
    var item = row['item_code']

    if(cur_frm.doc.customer){
	if (row['item_type']=="Customize"){
		var td=frappe.datetime.add_days(cur_frm.doc.transaction_date, 26)
		row['delivery_date'] = td
}
	if	(row['item_type']=="Measure"){
		var td=frappe.datetime.add_days(cur_frm.doc.delivery_date, 30)
		row['delivery_date'] = td

	}

}

})



//delivery date set for customize item
// frappe.ui.form.on("Sales Order", "refresh", function(frm, cdt, cdn) {
//     var user = frappe.session.user
//     var user_list = ["amita@navya.biz", "paawasthy11@gmail.com", "Administrator"]


//     if (!user_list.includes(user)) {
//         frm.set_df_property("delivery_date", "read_only", 1);

//     }


// })


// frappe.ui.form.on("Sales Order", "onload", function(frm, cdt, cdn) {

//     cur_frm.doc.items[0].item_code=""
    


// })
