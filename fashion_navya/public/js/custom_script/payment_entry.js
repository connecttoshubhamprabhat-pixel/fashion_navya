frappe.ui.form.on('Payment Entry', {
	onload(frm,cdt,cdn) {
	    //console.log("aaaaaa"
	    if(cur_frm.doc.event_name!=undefined && cur_frm.doc.__islocal==1){
	       // console.log('ssssssssssss')
	            var k= frappe.db.get_value("Events",cur_frm.doc.event_name, "supplier");
	            console.log(k)
	            //var vl=m.message['supplier']
				frappe.model.set_value(cdt, cdn, "party_type","Supplier");
				//frappe.model.set_value(cdt, cdn, "party",vl);
			
		
			
	}
	}
	
})


frappe.ui.form.on('Payment Entry', {
	before_save(frm,cdt,cdn) {
	    //console.log("aaaaaa")
	   // if(frappe.user.has_role("Custom Account")==true && cur_frm.doc.mode_of_payment!="Cheque"){
	   //         frappe.throw("You can make Entry only for cheque")
	  
	   
	}
	
})


frappe.ui.form.on("Payment Entry", "validate", function(frm,cdt,cdn) {
         let row = frappe.get_doc(cdt, cdn);
            let tb=cur_frm.doc.references
        if (tb==undefined && cur_frm.doc.__islocal==1 && frappe.user.has_role("Managing Director")==false && cur_frm.doc.payment_type!="Receive"){
                   // frappe.msgprint(__('References Table Shold not be empty'))
                    frm.set_df_property("references", "reqd", 1);
            }
		 
		 })
		 
		 
	
	
	
//------------------estimate sheet
frappe.ui.form.on("Payment Entry", "refresh", function(frm, cdt, cdn) {

        setTimeout(set_estimate_value(frm), 5000);
});


function set_estimate_value(frm,cdt,cdn) {
        if (cur_frm.doc.__islocal && cur_frm.doc.estimate_sheet) {
            cur_frm.set_value("party_type", "Customer")
                

                frappe.db.get_value("Estimate Sheet", {
                        "name": cur_frm.doc.estimate_sheet
                }, ["customer","customer_name"], function(value) {
                       
                        console.log(value.customer)
                        frappe.model.set_value(cdt, cdn, "party", value.customer);
                        frappe.model.set_value(cdt, cdn, "party_name", value.customer_name);
                });
        }
};



//make ready only field
frappe.ui.form.on('Payment Entry',  'refresh',  function(frm) {
    make_field_read(frm)
});


//make ready only field
frappe.ui.form.on('Payment Entry',  'onload',  function(frm) {
    make_field_read(frm)
});

frappe.ui.form.on('Payment Entry',  'before_save',  function(frm) {
    make_field_read(frm)
});






function make_field_read(frm){
	if( !cur_frm.doc.__islocal && cur_frm.doc.customer_pe && cur_frm.doc.payment_type=="Internal Transfer"){
		cur_frm.set_df_property('paid_amount', 'read_only',1);
		cur_frm.set_df_property('paid_from', 'read_only',1);
		cur_frm.set_df_property('paid_to', 'read_only',1);
		cur_frm.set_df_property('received_amount', 'read_only',1);


	}

	if(cur_frm.doc.payment_type=="Internal Transfer"){
		cur_frm.set_df_property('ped', 'reqd', 1)

	}
	if(cur_frm.doc.__islocal && cur_frm.doc.payment_type=="Internal Transfer" && cur_frm.doc.ped=="Customer"){
		cur_frm.set_df_property('customer_pe', 'reqd', 1)
		cur_frm.add_fetch('customer_pe','paid_amount','paid_amount')



}


}

