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



@frappe.whitelist()
def update_images_item():
	get_items=frappe.db.sql("""select name from `tabItem` where item_group='Sample' and disabled=0 and variant_of is not null and image is not null  """,as_dict=1)
	for i in get_items:
		doc=frappe.get_doc("Item",i['name'])
		name=doc.name
		template=doc.variant_of
		if not template:
			return

		size=[]
		for a in doc.attributes:
			if a.attribute=="Size":
				size.append(a.attribute_value)
		template=doc.variant_of
		images_items=[]
		get_child_items=frappe.db.sql("""select name from `tabItem` where item_group!="Sample"  and variant_of='{}' and disabled=0 and name!='{}' and image is null """.format(template,name),as_dict=1)
		if get_child_items:
			for k in get_child_items:
				child=frappe.get_doc("Item",k['name'])
				for b in child.attributes:
					if b.attribute=="Size":
						if b.attribute_value in size:
							images_items.append(k['name'])
		for m in images_items:
			print(m,'mmmmmmmmmmmmm')
			try:
				image_doc=frappe.get_doc("Item",m)
				image_doc.db_set("image",doc.image, update_modified=False)
				image_doc.save(ignore_permissions=True)
				frappe.db.commit()
			except:
				continue
