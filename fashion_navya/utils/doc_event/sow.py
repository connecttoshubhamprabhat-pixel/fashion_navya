import frappe


@frappe.whitelist()
def set_warehouse_target_mr(doc,method):
	for i in doc.items:
		item_split=i.item_code.split("-")
		if doc.custom_is_so==1 and doc.material_request_type=="Material Transfer":
			so=frappe.get_doc("Sales Order",i.sales_order)
			if so.delivery_type!="Courier":
				shop=frappe.get_doc("Shop Location",so.custom_shop_location)
				doc.set("set_warehouse",shop.default_warehouse)
				
			if so.delivery_type=="Courier":
				doc.set("set_warehouse","Courier Station - NAVYA")
				i.set("warehouse","Courier Station - NAVYA")
				
		if doc.material_request_type=="Manufacture" and doc.custom_is_so==0:
			if "RTW" in item_split and "BP" in item_split:
				i.set("warehouse","Libberheri  - NAVYA")
			else:
				i.set("warehouse","Navya Store Office - NAVYA")
				
		if doc.material_request_type=="Manufacture" and doc.custom_is_so==1:
			i.set("warehouse","Navya Store Office - NAVYA")
		
				
		if doc.material_request_type=="Material Transfer" and doc.custom_is_so==0:
			if "RTW" in item_split and "BP" in item_split:
				i.set("warehouse","Libberheri  - NAVYA")
				
			else:
				i.set("warehouse","Navya Store Office - NAVYA")




	


