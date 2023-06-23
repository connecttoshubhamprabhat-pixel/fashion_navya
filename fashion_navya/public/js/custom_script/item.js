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




// additional validation on dates
frappe.ui.form.on('Item',  'refresh',  function(frm) {
	var user=frappe.session.user
	var user_list=['neha@navyacustom.com','sweetyd@navyacustom.com','vivekd@navyacustom.com','sosowon@navyacustom.com']
    if (user_list.includes(user)) {
        $('#item-inventory_section').hide();
        $('#item-details').hide();
	$('#item-inventory_section').hide();
        $('#item-sales_details').hide();
	$('#item-purchasing_tab').hide();
	$('#item-manufacturing').hide();
	$('#item-accounting').hide();
	$('#item-manufacturing').hide();
    }
});

//---------------
