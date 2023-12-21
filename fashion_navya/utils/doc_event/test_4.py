import frappe


@frappe.whitelist()
def bom_notify():
	get_mr=frappe.db.sql("""select name from `tabMaterial Request` where  material_request_type='Manufacture' and  docstatus<2 and custom_bom=0  """.format(),as_dict=1)
	if get_mr:
		for m in get_mr:
			doc=frappe.get_doc("Material Request",m['name'])
			if doc.custom_bom==0:
				doctype=doc.doctype
				des=" Measurement के हिसाब से BOM  को सेट करो ||,MR No:- {}".format(doc.name)
				user_list=['vivekd@navyacustom.com','gaurav@example.com']
				for i in user_list:
					d={'doctype':"ToDo","priority":"High","reference_type":doctype}
					d['description']=des
					d['reference_name']=doc.name
					d['assigned_by']="amita@navya.biz"
					d['allocated_to']=i
					td=frappe.get_doc(d)
					td.insert()
					frappe.db.commit()





@frappe.whitelist()
def wo_notify():
	get_mr=frappe.db.sql("""select name from `tabWork Order` where docstatus<2 and status='Not Started'  """.format(),as_dict=1)
	if get_mr:
		for m in get_mr:
			doc=frappe.get_doc("Work Order",m['name'])
			doctype=doc.doctype
			des=" Work Order is created||,Work order No:- {}".format(doc.name)
			user_list=['vivekd@navyacustom.com','gaurav@example.com']
			for i in user_list:
				d={'doctype':"ToDo","priority":"High","reference_type":doctype}
				d['description']=des
				d['reference_name']=doc.name
				d['assigned_by']="amita@navya.biz"
				d['allocated_to']=i
				td=frappe.get_doc(d)
				td.insert()
				frappe.db.commit()




#remove uoms uplicate in Items
@frappe.whitelist()
def remove_duplicate_uoms(item_group=None):
	get_items=frappe.db.sql("""select name from `tabItem` where item_group='{}' and disabled=0  """.format(item_group),as_dict=1)
	added_attributes=[]
	get_items=get_items
	for i in get_items:
		print(i['name'])
		if i['name'] not in ["0587SS18DBPP02.1-TUR-M-CHA\\"]:
			if frappe.db.exists("Item",i['name']) and i['name'] not in ["0587SS18DBPP02.1-TUR-M-CHA\\"]:
				dup=[]
				flag=[]
				doc_item=frappe.get_doc("Item",i['name'])
				doc_as_dict=doc_item.as_dict()
				doc_item.uoms=[]
				doc_item.attributes=[]
				doc_item.item_defaults=[]
				for m in doc_as_dict.attributes:
					if m['attribute'] not in dup:
						row=doc_item.append("attributes",{})
						row.attribute=m['attribute']
						row.attribute_value=m['attribute_value']
						dup.append(m['attribute'])
					else:
						flag.append('aa')
				if flag:
					doc_item.save(ignore_permissions=True)
					frappe.db.commit()



@frappe.whitelist()
def remove_duplicate_uoms_manual(name=None):
	get_items=frappe.db.sql("""select name from `tabItem` where name='{}' and disabled=0  """.format(name),as_dict=1)
	added_attributes=[]
	get_items=get_items
	for i in get_items:
		print(i['name'])
		if i['name'] not in ["0587SS18DBPP02.1-TUR-M-CHA\\"]:
			if frappe.db.exists("Item",i['name']) and i['name'] not in ["0587SS18DBPP02.1-TUR-M-CHA\\"]:
				dup=[]
				flag=[]
				doc_item=frappe.get_doc("Item",i['name'])
				doc_as_dict=doc_item.as_dict()
				doc_item.uoms=[]
				doc_item.attributes=[]
				doc_item.item_defaults=[]
				for m in doc_as_dict.attributes:
					if m['attribute'] not in dup:
						row=doc_item.append("attributes",{})
						row.attribute=m['attribute']
						row.attribute_value=m['attribute_value']
						dup.append(m['attribute'])
					else:
						flag.append('aa')
				if flag:
					doc_item.save(ignore_permissions=True)
					frappe.db.commit()




@frappe.whitelist()
def remove_duplicate_uoms_cron():
	get_items=frappe.db.sql("""select name from `tabItem` where item_group in ('Smaple','Ready Stock','M kit') disabled=0  """,as_dict=1)
	added_attributes=[]
	get_items=get_items
	for i in get_items:
		print(i['name'])
		if i['name'] not in ["0587SS18DBPP02.1-TUR-M-CHA\\"]:
			if frappe.db.exists("Item",i['name']) and i['name'] not in ["0587SS18DBPP02.1-TUR-M-CHA\\"]:
				dup=[]
				flag=[]
				doc_item=frappe.get_doc("Item",i['name'])
				doc_as_dict=doc_item.as_dict()
				doc_item.uoms=[]
				doc_item.attributes=[]
				doc_item.item_defaults=[]
				for m in doc_as_dict.attributes:
					if m['attribute'] not in dup:
						row=doc_item.append("attributes",{})
						row.attribute=m['attribute']
						row.attribute_value=m['attribute_value']
						dup.append(m['attribute'])
					else:
						flag.append('aa')
				if flag:
					doc_item.save(ignore_permissions=True)
					frappe.db.commit()
