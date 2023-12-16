import frappe
import json

@frappe.whitelist()
def make_mr_project(name=None):
	if not name:
		return


	get_alls=frappe.db.sql("""select DISTINCT  name from `tabItem` where variant_of is not null and  project='{}'  """.format(name),as_dict=1)
	if get_alls:
		d={"doctype":"Material Request","material_request_type":"Manufacture","project":name}
		mr=frappe.get_doc(d)
		for i in get_alls:
			row = mr.append("items", {})
			row.item_code=i['name']
			row.description=i['name']
			row.uom="Nos"
			row.qty=1

		mr.insert()
		frappe.msgprint("MR Created")





@frappe.whitelist()
def make_mr_select(items=None,name=None):
	items=json.loads(items)
	if not name:
		return

	if items:
		d={"doctype":"Material Request","material_request_type":"Manufacture","project":name}
		mr=frappe.get_doc(d)
		for i in  items:
			row = mr.append("items", {})
			row.item_code=i
			row.description=i
			row.uom="Nos"
			row.qty=1

		mr.insert()
		frappe.msgprint("MR Created")







@frappe.whitelist()
def check_bom_mr(doc,method):
	for i in doc.items:
		check_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1 and item='{}'  """.format(i.item_code),as_dict=1)
		if len(check_bom)!=0:
			doc.set("custom_bom",1)

		if i.sales_order:
			doc.set("custom_is_so",1)

		split_code=i.item_code.split("-")
		if "MTM" in split_code:
			doc.set("custom_mtm",1)

		get_so_cms=frappe.db.sql("""select name from `tabSales Order Item` where item_type='Customize'  and  docstatus=1 and name='{}' and parent='{}'   """.format(i.sales_order_item,i.sales_order),as_dict=1)
		if len(get_so_cms)!=0:
			doc.set("custom_cms",1)





@frappe.whitelist()
def check_bom_mr_old():

	get_mr=frappe.db.sql("""select 	DISTINCT parent from `tabMaterial Request Item` where sales_order is not null   """,as_dict=1)
	if get_mr:
		for m in get_mr:
			print(m['parent'])
			doc=frappe.get_doc("Material Request",m['parent'])
			for i in doc.items:
				check_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and is_active=1 and is_default=1 and item='{}'  """.format(i.item_code),as_dict=1)
				if len(check_bom)!=0:
					#doc.set("custom_bom",1)
					frappe.db.sql("""update `tabMaterial Request` set custom_bom=1 where name='{}'  """.format(doc.name))

				if i.sales_order:
					#doc.set("custom_is_so",1)
					frappe.db.sql("""update `tabMaterial Request` set custom_is_so=1 where name='{}'  """.format(doc.name))

				split_code=i.item_code.split("-")
				if "MTM" in split_code:
					#doc.set("custom_mtm",1)
					frappe.db.sql("""update `tabMaterial Request` set custom_mtm=1 where name='{}'  """.format(doc.name))

				get_so_cms=frappe.db.sql("""select name from `tabSales Order Item` where item_type='Customize'  and  docstatus=1 and name='{}' and parent='{}'   """.format(i.sales_order_item,i.sales_order),as_dict=1)
				if len(get_so_cms)!=0:
					#doc.set("custom_cms",1)
					frappe.db.sql("""update `tabMaterial Request` set custom_cms=1 where name='{}'  """.format(doc.name))
				frappe.db.commit()





@frappe.whitelist()
def check_is_bom_mr(doc,method):
	if doc.is_active and doc.is_default:
		get_mr=frappe.db.sql(""" select DISTINCT  parent from `tabMaterial Request Item` where item_code='{}' and docstatus<2  """.format(doc.item),as_dict=1)
		if len(get_mr)!=0:
			for i in get_mr:
				frappe.db.sql("""update `tabMaterial Request` set custom_bom=1 where name='{}' and docstatus<2  """.format(i['parent']),as_dict=1)
				frappe.db.commit()


#on canel
@frappe.whitelist()
def uncheck_is_bom_mr(doc,method):
	check_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}' and is_active=1 and is_default=1  """.format(doc.item),as_dict=1)
	if len(check_bom)==0:
		get_mr=frappe.db.sql(""" select DISTINCT  parent from `tabMaterial Request Item` where item_code='{}' and docstatus<2  """.format(doc.item),as_dict=1)
		if len(get_mr)!=0:
			for i in get_mr:
				frappe.db.sql("""update `tabMaterial Request` set custom_bom=0 where name='{}' and docstatus<2  """.format(i['parent']),as_dict=1)
				frappe.db.commit()



@frappe.whitelist()
def automated_mr_se(doc,method):
	if doc.items and doc.stock_entry_type=="Material Transfer":
		mr_exists=doc.items[0].material_request
		if mr_exists:
			doc.set("add_to_transit",1)
			doc.set("custom_automated_mr",1)

#link so mr both
@frappe.whitelist()
def mr_links_transfer(doc,method):
	so_list=[]
	for i in doc.items:
		if i.sales_order not in so_list:
			so_list.append(i.sales_order)
	if so_list:
		for i in so_list:
			if doc.material_request_type=="Manufacture":
				get_mr_transfer=frappe.db.sql("""select DISTINCT parent from `tabMaterial Request Item`  where sales_order='{}' and parent in (select name from `tabMaterial Request` where docstatus<2 and material_request_type='Material Transfer' )  """.format(i),as_dict=1)
				if get_mr_transfer:
					frappe.db.sql("""update `tabMaterial Request` set custom_mrm='{}' where name='{}' and docstatus<2  """.format(doc.name,get_mr_transfer[0]['parent']))
					frappe.db.commit()

			if doc.material_request_type=="Material Transfer":
				get_mr_transfers=frappe.db.sql("""select DISTINCT parent from `tabMaterial Request Item`  where sales_order='{}' and parent in (select name from `tabMaterial Request` where docstatus<2 and material_request_type='Manufacture' )  """.format(i),as_dict=1)
				if get_mr_transfers:
					doc.set("custom_mrm",get_mr_transfers[0]['parent'])




@frappe.whitelist()
def check_bom_project(doc,method):
	for i in doc.items:
		get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}'  """.format(i.item_code),as_dict=1)
		if len(get_bom)!=0:
			doc.set("custom_bom",1)




@frappe.whitelist()
def check_bom_project_old():
	mr=frappe.db.sql("""select name from `tabMaterial Request`   where material_request_type='Manufacture' and docstatus=1 and custom_bom=0  """,as_dict=1)
	if mr:
		for m in mr:
			doc=frappe.get_doc("Material Request",m['name'])
			for i in doc.items:
				get_bom=frappe.db.sql("""select name from `tabBOM` where docstatus=1 and item='{}'  """.format(i.item_code),as_dict=1)
				if len(get_bom)!=0:
					frappe.db.sql("""update `tabMaterial Request` set custom_bom=1 where name='{}'  """.format(m['name']))
					frappe.db.commit()
