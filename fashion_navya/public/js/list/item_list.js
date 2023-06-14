 frappe.listview_settings['Item'] = frappe.listview_settings['Item'] || {};
 
 frappe.listview_settings['Item'].refresh = function(listview) {
    // add button to menu
    // var docnames = listview.get_checked_items(true);
    //      listview.page.add_action_item(__("Delete Manual"), function() {
    //     	delete_doc(listview)
    //   });
       listview.page.add_inner_button("Add To Events", function() {
           
           test( listview )
        });
        listview.page.add_inner_button("Search", function() {
            add_filter(listview)
           
           
        });
    //}

    //------
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
	//000000000000000

//}

};

function test(value)
{
	var k=value.get_checked_items();
	console.log
	dillogs(k);
}
	
	
function dillogs(k){
    var k=k;
//----------------------------
    let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
            
        {
				"fieldtype" : "Select", 
				"options" 	:['Sample',"Ready Stock"],
				"label" 	: __("Select Table"),
				"fieldname" : "table_name",
				default:" ",
				"reqd":1
			},
    
        {
				"fieldtype" : "Link", 
				"options" 	: "Events",
				"label" 	: __("Event Name"),
				"fieldname" : "event_name",
				"reqd":1
			},

        
    ],
    primary_action_label: 'Submit',
    primary_action(values) {
        console.log(k,values);
        frappe.call({
		"method": "navya.api_folder.py.events.set_values_tb",
		args: {
		items:k,
		values:values
		},
		callback:function(r){
		}
		});

        d.hide();
    }
});

d.show();

}


//-----------
function delete_doc(value)
{
	var k=value.get_checked_items();
	alert('aaa')
	
}


function add_filter(listview){
     
   
   let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
        {
            label: 'Attribues',
            fieldname: 'att_val',
            fieldtype: 'Data'
        }
        
    ],
    primary_action_label: 'Search',
    primary_action(values) {
        console.log(values.att_val);
        var v=values.att_val;
        var url=`https://erp.navyacustom.com/app/item/view/image?attribute_value=${v}`
       window.location =url;
            
    }
});

d.show();

        
     
 }
 
 //--------------------s
 
 
 
 
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
							"doc":"Item",
						},
						callback(r) {
						    console.log(r.message,999)

						}
			});
   
        
	
	
	}
	
	
