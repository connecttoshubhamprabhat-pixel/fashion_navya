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




@frappe.whitelist()
def fetch_details_wo():
	#get_po=frappe.db.sql("""select name,work_order from `tabPurchase Order` where work_order is not null and is_subcontracted=1 and docstatus=1 """,as_dict=1)
	get_po=frappe.db.sql(""" select DISTINCT parent as name,work_order from `tabPurchase Order Item` where work_order is not null and docstatus=1 """,as_dict=1)
	if get_po:
		for i in get_po:
			print(i['name'],"po")
			get_sbo=frappe.db.sql("""select * from `tabSubcontracting Order` where docstatus=1 and purchase_order='{}'  """.format(i['name']),as_dict=1)
			if len(get_sbo)!=0:
				frappe.db.sql("""update `tabWork Order` set custom_supplier='{}' where docstatus=1 and name='{}'  """.format(get_sbo[0]['supplier'],i['work_order']))
				get_se=frappe.db.sql("""select * from `tabStock Entry` where docstatus <2 and subcontracting_order='{}'   """.format(get_sbo[0]['name']),as_dict=1)
				if len(get_se)!=0:
					print(i['name'],"s")
					frappe.db.sql("""update `tabWork Order` set custom_materials_sent='{}' where docstatus=1 and name='{}'  """.format(get_se[0]['workflow_state'],i['work_order']))
					frappe.db.sql("""update `tabWork Order` set custom_date_sent='{}' where docstatus=1 and name='{}'  """.format(get_se[0]['posting_date'],i['work_order']))
					frappe.db.sql("""update `tabWork Order` set custom_subcontracting_order='{}' where docstatus=1 and name='{}'  """.format(get_sbo[0]['name'],i['work_order']))
					frappe.db.commit()
				get_sbr=frappe.db.sql("""select * from `tabSubcontracting Receipt` where docstatus=1 and purchase_order='{}'  """.format(i['name']),as_dict=1)
				if len(get_sbr)!=0:
					frappe.db.sql("""update `tabWork Order` set custom_subcontracting_receipt='{}' where docstatus=1 and name='{}'  """.format(get_sbr[0]['name'],i['work_order']))
					frappe.db.sql("""update `tabWork Order` set custom_sreceipt_date='{}' where docstatus=1 and name='{}'  """.format(get_sbr[0]['posting_date'],i['work_order']))
					frappe.db.sql("""update `tabWork Order` set custom_srstatus='{}' where docstatus=1 and name='{}'  """.format(get_sbr[0]['status'],i['work_order']))
					frappe.db.commit()



@frappe.whitelist(allow_guest=True)
def fetch_msrement():
	get_mr=frappe.db.sql("""select DISTINCT name from `tabWork Order` where material_request is not null or sales_order is not null and docstatus=1  """,as_dict=1)
	if get_mr:
		for w in get_mr:
			doc=frappe.get_doc("Work Order",w['name'])
			sos=[]
			if len(doc.measurements_child)==0:
				continue
			if doc.sales_order:
				sos.append(doc.sales_order)
			else:
				if doc.material_request:
					mrd=frappe.get_doc("Material Request",doc.material_request)
					for me in mrd.items:
						sos.append(me.sales_order)
			if sos:
				item=doc.production_item.split("-")
				y=[]
				if "MTM"  in  item:
					y.append("a")

				

@frappe.whitelist()
def check_subconrcat(doc,method):
	name=doc.name
	split=name.split("-")
	if 'RTW' in  split or  'MTM' in split:
		doc.set("is_sub_contracted_item",1)
