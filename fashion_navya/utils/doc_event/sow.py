import frappe


@frappe.whitelist()
def set_warehouse_target_mr(doc,method):
	if doc.material_request_type=="Manufacture":
		doc.set("set_warehouse","Navya Store Office - NAVYA")

	if doc.material_request_type=="Material Transfer":
		doc.set("set_from_warehouse","Navya Store Office - NAVYA")
		for i in doc.items:
			if i.sales_order:
				so=frappe.get_doc("Sales Order",i.sales_order)
				if so.delivery_type!="Courier":
					shop=frappe.get_doc("Shop Location",so.custom_shop_location)
					doc.set("set_warehouse",shop.default_warehouse)

				if so.delivery_type=="Courier":
					doc.set("set_warehouse","Courier Station - NAVYA")
