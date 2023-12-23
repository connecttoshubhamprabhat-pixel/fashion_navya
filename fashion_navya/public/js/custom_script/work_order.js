


// hide section
frappe.ui.form.on('Work Order',  {
    refresh: function(frm) {
        if (!cur_frm.doc.sales_order ){
          let user=frappe.session.user
         // let user_list=['pawasthy11@gmail.com','neha@navyacustom.com','sosowon@navyacustom.com','ksvwon@navyacustom.com']
          //if (user_list.includes(user)){
            //$('.section-body').hide();
          //}

        }
    }
});

