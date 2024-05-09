import frappe

@frappe.whitelist()
def set_m_item_wo(doc,method):
	for i in doc.items:
		get_mitem_wo=frappe.db.sql("""select custom_mitem,work_order from `tabSubcontracting Order Item` where docstatus=1 and item_code='{}'  """.format(i.item_code),as_dict=1)
		if get_mitem_wo:
			if get_mitem_wo[0].work_order!=None:
				i.set("custom_work_order",get_mitem_wo[0].work_order)
			if get_mitem_wo[0].custom_mitem!=None:
				i.set("custom_mitem",get_mitem_wo[0].custom_mitem)

@frappe.whitelist()
def set_m_item_wo_old():
	get_sub=frappe.db.sql("""select name from `tabSubcontracting Receipt` where docstatus=1  """,as_dict=1)
	if get_sub:
		for  j in get_sub:
			doc=frappe.get_doc("Subcontracting Receipt",j['name'])
			for i in doc.items:
				get_mitem_wo=frappe.db.sql("""select custom_mitem,work_order from `tabSubcontracting Order Item` where docstatus=1 and item_code='{}'  """.format(i.item_code),as_dict=1)
				if get_mitem_wo:
					print(doc.name)
					if get_mitem_wo[0].work_order!=None:
						frappe.db.sql("""update `tabSubcontracting Receipt Item` set custom_work_order='{}' where docstatus=1 and item_code='{}' and parent='{}'  """.format(get_mitem_wo[0].work_order,i.item_code,doc.name))
						frappe.db.commit()
					if get_mitem_wo[0].custom_mitem!=None:
						frappe.db.sql("""update `tabSubcontracting Receipt Item` set custom_mitem='{}' where docstatus=1 and item_code='{}' and parent='{}'  """.format(get_mitem_wo[0].custom_mitem,i.item_code,doc.name))
						frappe.db.commit()
