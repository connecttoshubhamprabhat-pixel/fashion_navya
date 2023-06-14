frappe.listview_settings['Project'] = frappe.listview_settings['Project'] || {};
    
 
 
 frappe.listview_settings['Project'].refresh = function(listview) {
     listview.page.add_inner_button("Add Item Tag", function() {
		 		tag_add(listview)
     });
 		
     
     var checks=has_common(frappe.user_roles, ["Administrator",'pardeep','Managing Director'])
     if(checks){
    
		 listview.page.add_inner_button("Delete Record", function() {
		 		return new Promise(function(resolve, reject) {
                                                frappe.confirm(
                                                    'Are you sure you want to proceed?',
                                                    function() {
                                                        
                                                        delete_doc(listview)

                                                        var negative = 'frappe.validated = false';
                                                        resolve(negative);
                                                    },
                                                    function() {
                                                        reject();
                                                    }
                                                )
                                            })
           
           
        });
     }
	}
       
	
	function delete_doc(listview){
		var k=cur_list.get_checked_items()
		var list_name=[]
		for(var i=0;i< k.length;i++){
		    list_name.push(k[i].name)
		    
		}
		console.log(list_name)
		frappe.call({
				method: "navya.api_folder.py.test.bulk_delete_doc",
						args: {
							"items":list_name,
							"doc":"Project",
						},
						callback(r) {
						    console.log(r.message,999)

						}
			});
   
        
	
	
	}
	
	//----------item tag
	
	 function tag_add(listview){
		var k=cur_list.get_checked_items()
		var list_name=[]
		for(var i=0;i< k.length;i++){
		    list_name.push(k[i].name)
		    
		}
		
		function removeDuplicates(arr) {
        var unique = arr.reduce(function (acc, curr) {
            if (!acc.includes(curr))
                acc.push(curr);
            return acc;
        }, []);
        return unique;
    }
        var items=removeDuplicates(list_name)
		console.log(items,"project56666")
		frappe.call({
				method: "navya.api_folder.py.test.create_item_tag_bulk",
						args: {
							"items":items,
							"doc":"Project",
						},
						callback(r) {
						    console.log(r.message,999)

						}
			});
   
        
	
	
	}
//------------delete
	
	
