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
