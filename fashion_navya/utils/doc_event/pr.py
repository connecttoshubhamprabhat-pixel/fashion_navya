import frappe


@frappe.whitelist()
def  set_kit_parent_pr(doc,method):
	if doc.is_subcontracted==1:
		for i in doc.items:
			item=i.item_code
			get_po_item=frappe.db.sql(""" select fg_item,fg_parent from `tabPurchase Order Item` where docstatus=1 and item_code='{}' and parent='{}'   """.format(item,i.purchase_order),as_dict=1)
			if get_po_item:
				if get_po_item[0]['fg_parent']:
					docitem=frappe.get_doc("Item",get_po_item[0]['fg_parent'])
					doc.set("fg_parent",get_po_item[0]['fg_parent'])
					doc.set("fgkitem",get_po_item[0]['fg_item'])
					if  not doc.project:
						doc.set("project",docitem.project)
					get_bom=frappe.db.sql(""" select name from `tabBOM` where item='{}' and docstatus=1 and is_active=1 and is_default=1  """.format(get_po_item[0]['fg_parent']),as_dict=1)
					if get_bom:
						bomdoc=frappe.get_doc("BOM",get_bom[0]['name'])
						get_np=bomdoc.items[0].qty
						doc.set("nop",get_np)

#only subcontracting
@frappe.whitelist(allow_guest=True)
def set_sell_offline():
	pos=frappe.db.sql("""select name from `tabPurchase Receipt` where is_subcontracted=1 and docstatus < 2 """,as_dict=1)
	if pos:
		for j in  pos:
			doc=frappe.get_doc("Purchase Receipt",j['name'])
			for i in doc.items:
				get_po_item=frappe.db.sql(""" select fg_item,fg_parent from `tabPurchase Order Item` where docstatus=1 and  parent='{}'  and item_code='{}'  """.format(i.purchase_order,i.item_code),as_dict=1)
				if len(get_po_item)!=0:
						get_bom=frappe.db.sql(""" select name from `tabBOM` where item='{}' and docstatus=1 and is_active=1 and is_default=1  """.format(get_po_item[0]['fg_parent']),as_dict=1)
						if get_bom:
							bomdoc=frappe.get_doc("BOM",get_bom[0]['name'])
							get_np=bomdoc.items[0].qty
							print(doc.name)
							frappe.db.sql("""update `tabPurchase Receipt Item` set fgkitem='{}' ,nop={},fg_parent='{}'  where docstatus < 2 and parent='{}' """.format(get_po_item[0]['fg_item'],get_np,get_po_item[0]['fg_parent'],doc.name))
							frappe.db.commit()



@frappe.whitelist()
def perm_check_pr(doc,method):
	user=frappe.session.user
	user_list=["sujeets@navyacustom.com","vivekd@navyacustom.com","kalim@navyacustom.com"]
	if user in user_list:
		for i in doc.items:
			mr=frappe.get_doc("Material Request",i.material_request)
			if user!=mr.owner:
				frappe.throw("Material Request is not created by you.")


