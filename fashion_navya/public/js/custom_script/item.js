// hide section
frappe.ui.form.on('Item',  {
    refresh: function(frm) {
        if (!cur_frm.doc.sales_order ){
          let user=frappe.session.user
          let user_list=['neha@navyacustom.com','sosowon@navyacustom.com','ksvwon@navyacustom.com']
          if (user_list.includes(user)){
            //$('.section-body').hide();
          }

        }
    }
});

