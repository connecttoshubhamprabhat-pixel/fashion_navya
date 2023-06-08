frappe.ui.form.on('Stock Entry',  {
    refresh: function(frm) {
			if(cur_frm.doc.stock_entry_type=="Material Transfer"){
				frm.set_df_property('rfse', 'reqd',1)
			}else{
				frm.set_df_property('rfse', 'reqd',0)

			}
		console.log('yes445')
    }
});



// workflow condition
frappe.ui.form.on('Stock Entry', {
            before_save: function(frm) {
                var states = ["Draft", "Authorisation Pending"]
                var wk = frm.doc.workflow_state
                var onr = [frm.doc.owner]
                var user = frappe.session.user
		console.log(user,'user')
		console.log(onr,'onr')
		console.log(wk,'wk')
                if (!states.includes(wk)) {
                    if (states.includes(user)) {
                        //throw ("Sorry You can not proceed  ,because you have made changes in pervious state.for example,if you authrized then you can not receive")
                          //  return 
			    //frm.disable_save(); 
			    //cur_frm.reload_doc();

                        }




                    }



                }
            });
