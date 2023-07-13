// cur_frm.cscript.custom_validate = function(frm) {
// 	//if(doc.purpose == "Material Receipt") {
// 		$.each(frappe.model.get("Pattern",{item_code:cur_frm.doc.item_code}), function(i, d) {
// 			console.log(d,22)
// 			//if(d.t_warehouse=="WarehouseX" && !d.material_request) {
// 			//	msgprint("You must receive against Material Request");
// 				//validated = false;
// 				//return;
// 			//}
// 		})
// 	//}
// }


frappe.ui.form.on("Child Patterns", "comment", function(frm,cdt,cdn) {
         let row = frappe.get_doc(cdt, cdn);
		 //comment
		 cur_frm.set_value("comment_",row.comment)
		 })
		 

frappe.ui.form.on("Child Patterns", "is_approved", function(frm,cdt,cdn) {
         let row = frappe.get_doc(cdt, cdn);
		 //comment
		 if(row.is_approved==1){
            		 console.log(row.size,row.pattern_attachment,'llllll')
            		 var childTable = cur_frm.add_child("sizes");
            		 childTable.size=row.size
            		 childTable.width_fabric=row.width
            		 childTable.fabric_1=row.fabric_1
            		 childTable.fabric_2=row.fabric_2
            		 
            		 childTable.image_ptrn=row.pattern_attachment
            		 
            		 cur_frm.refresh_fields("sizes");
		 }
		 
		 
		 })

frappe.ui.form.on("Pattern", "validate", function(frm,cdt,cdn) {
         let row = frappe.get_doc(cdt, cdn);
            let tb=cur_frm.doc.sizes
            if (tb==undefined && cur_frm.doc.__islocal==undefined){
                    frm.set_df_property("sizes", "reqd", 1);
            }
		 
		 })


		
	frappe.ui.form.on("Pattern", "validate", function(frm,cdt,cdn) {
         let row = frappe.get_doc(cdt, cdn);
            let tb=cur_frm.doc.patterns
            if (cur_frm.doc.__islocal==undefined && tb==[]){
                    frm.set_df_property("sizes", "reqd", 1);
            }
		 
		 })
	
		 
		 
	frappe.ui.form.on("Pattern", {
	    setup: function(frm) {
	    	frm.set_query("item_code", function() {
		    	return {
		    		filters: [
		    			["Item","has_variants", "=",1]
			    		
			    	]
		    	}
	    	});
    	}
});










//----------
// frappe.ui.form.on("Pattern", "on_submit", function(frm,cdt,cdn) {
					
// 					 $.each(frm.doc.patterns, function(index, row){
// 					     if(row.is_approved==1){
//          	 		        var childTable = cur_frm.add_child("sizes");
// 					        childTable.size=row.size
// 					         childTable.fabric_1=row.fabric_1
// 					        childTable.fabric_2=row.fabric_2
// 				             childTable.image_ptrn=row.pattern_attachment
// 				            // cur_frm.get_field("patterns").grid.grid_rows[row.idx-1].remove()
// 				             console.log("helosdsd")
// 					     }
//      		   });
//      		   cur_frm.refresh_fields("sizes");
//      		   frm.doc.patterns=[]
// 		 })
// //-------------------------
		 
		 
frappe.ui.form.on('Pattern', {
        refresh(frm,cdt,cdn) {
                // your code here
                if(cur_frm.doc.__islocal==undefined){
                //if (frappe.model.can_read("Task")) {
             frm.add_custom_button(__("SheetView"), function () {


                                frappe.route_options = {
                                              "item_code":frm.doc.item_code
                                      };
                                        frappe.set_route("List", "Pattern", "list");
                                        //cur_frm.reload_doc()



                                });
        //}
        }
        }
})



//-------------------------
frappe.ui.form.on("Pattern", "before_workflow_action", function(frm,cdt,cdn) {
         let row = frappe.get_doc(cdt, cdn);
            let tb=cur_frm.doc.pattern_sample
            if (cur_frm.doc.__islocal==undefined && tb.length==0 && cur_frm.doc.sheet_no==4){
                    console.log("aasasa")
                    frm.set_df_property("pattern_sample", "reqd", 1);
            }
		 
		 })
	

frappe.ui.form.on("Pattern", "refresh", function(frm,cdt,cdn) {
         let row = frappe.get_doc(cdt, cdn);
            let tb=cur_frm.doc.pattern_sample
            if (cur_frm.doc.sheet_no==4){
                    console.log("aasasa")
                    frm.set_df_property("sample", "reqd", 1);
            }

                 })

