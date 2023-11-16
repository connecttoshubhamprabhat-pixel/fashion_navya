import frappe


@frappe.whitelist(allow_guest=True)
def fetch_attribues(doc,method):
	if doc.sales_order:
		so=frappe.get_doc("Sales Order",doc.sales_order)
		items=[]
		for i in so.items:
			items.append(i.item_code)
		for j in  doc.purposes:
			if j.item_code  not in items:
				frappe.throw("This is not an item on the sales order")

			get_val=frappe.db.sql("""select * from `tabSales Order Item` where docstatus=1 and item_code='{}' and parent='{}'  """.format(j.item_code,so.name),as_dict=1)
			if get_val:
				for m in get_val:
					j.set("custom_bust",m['custom_bust'])
					j.set("custom_top_waist",m['custom_top_waist'])
					j.set("custom_top_hip",m['custom_top_hip'])
					j.set("custom_lower_waist",m['custom_lower_waist'])
					j.set("custom_lower_hip",m['custom_lower_hip'])
					j.set("custom_sleeve_length",m['custom_sleeve_length'])
					j.set("custom_bottom_length",m['custom_bottom_length'])
			j.set("custom_sales_order",so.name)


@frappe.whitelist(allow_guest=True)
def custom_maintence_visit(doc,method):
	for i in doc.purposes:
		if i.custom_sales_order:
			so=frappe.get_doc("Sales Order",i.custom_sales_order)
			for j in so.items:
				if j.item_code==i.item_code:
					frappe.db.sql("""update `tabSales Order Item` set custom_maintenance_visit='{}' where parent='{}' and docstatus=1  """.format(doc.name,so.name))
					frappe.db.commit()
