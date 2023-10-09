import frappe

#barcode
@frappe.whitelist()
def set_barcode_all(group=None):
	items=frappe.db.sql(""" select name from `tabItem` where item_group='{}' and ignore_project=0   """.format(group),as_dict=1)
	for i in items:
		print(i['name'])
		doc=frappe.get_doc("Item",i['name'])
		
		try:
			doc.set("ignore_project",1)
			doc.save()
			frappe.db.commit()
		except:
			pass



@frappe.whitelist()
def mkit_item():
	items=frappe.db.sql("""select name from `tabItem` where item_group="M kit" and stock_uom="Meter"   """,as_dict=1)
	for i in items:
		print(i['name'])
		doc=frappe.get_doc("Item",i['name'])
		doc.set("stock_uom","Nos")
		try:
			doc.save()
			frappe.db.commit()
		except:
			continue



@frappe.whitelist()
def change_stock(g=None):
	items=frappe.db.sql("""select name from `tabItem` where item_group='{}' and ignore_project=0  """.format(g),as_dict=1)
	for i in  items:
		print(i['name'])
		doc=frappe.get_doc("Item",i['name'])
		doc.set("ignore_project",1)
		try:
			doc.save()
			frappe.db.commit()
		except:
			continue
@frappe.whitelist()
def update_items():
	w=[]
	ws=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Santushti - NAVYA' and disabled=0   """,as_dict=1)
	items=[]
	for i in ws:
		get_items=frappe.db.sql("""select DISTINCT item_code from `tabBin` where actual_qty>0 and warehouse='{}'  """.format(i),as_dict=1)
		if len(get_items)!=0:
			for j in get_items:
				if j['item_code'] not in items:
					items.append(j['item_code'])
