import frappe

#only subcontracting
@frappe.whitelist(allow_guest=True)
def set_sell_item_po(doc,method):
	if not doc.get("__islocal") and doc.is_subcontracted:
		for i in doc.items:
			getwo=frappe.db.sql(""" select qty from `tabWork Order` where docstatus=1 and production_item='{}'  """.format(i.fg_item),as_dict=1)
			if len(getwo)!=0:
				wqty=getwo[0]['qty']
				i.set('qty',wqty)
			if i.fg_item:
				fgdoc=frappe.get_doc("Item",i.fg_item)
				if fgdoc.parent_item!=None:
					if not doc.project:
						doc.set("project",fgdoc.project)
					i.db_set("fg_parent",fgdoc.parent_item, update_modified=False)
#only subcontracting
@frappe.whitelist(allow_guest=True)
def set_sell_offline():
	pos=frappe.db.sql("""select name from `tabPurchase Order` where is_subcontracted=1 and docstatus < 2 """,as_dict=1)
	if pos:
		for j in  pos:
			doc=frappe.get_doc("Purchase Order",j['name'])
			for i in doc.items:
				if i.fg_item:
					fgdoc=frappe.get_doc("Item",i.fg_item)
					if fgdoc.parent_item!=None:
						print(doc.name)
						get_bom=frappe.db.sql(""" select name from `tabBOM` where item='{}' and docstatus=1 and is_active=1 and is_default=1  """.format(fgdoc.parent_item),as_dict=1)
						if get_bom:
							bomdoc=frappe.get_doc("BOM",get_bom[0]['name'])
							get_np=bomdoc.items[0].qty
							frappe.db.sql("""update `tabPurchase Order Item` set fg_parent='{}' where docstatus < 2 and parent='{}' """.format(fgdoc.parent_item,doc.name))
							#frappe.db.commit()
							frappe.db.sql("""update `tabPurchase Order Item`  set nop={} where docstatus < 2 and parent='{}'  """.format(int(get_np),doc.name))
							frappe.db.commit()








@frappe.whitelist(allow_guest=True)
def set_parent_item_qty(item=None,nop=None):
	if not item:
		return

	doc=frappe.get_doc("Item",item)
	if not frappe.db.exists("Item",doc.parent_item):
		frappe.msgprint("Please Correct its Parent Item Name")
		return

	parent=frappe.get_doc("Item",doc.parent_item)
	bom=frappe.db.sql("""select name from `tabBOM` where item='{}' and docstatus=1 and is_active=1 and is_default=1 """.format(parent.name),as_dict=1)
	if len(bom)!=0:
		bdoc=frappe.get_doc("BOM",bom[0]['name'])
		n=bdoc.items[0].qty
		fqty=n*float(nop)
		f=round(fqty,3)
		return f or 0



frappe.whitelist(allow_guest=True)
def check_delete_draft(doc,method):
	user=frappe.session.user
	if user!="Administrator":
		if doc.owner!=user:
			users=['pawasthy11@gmail.com','erpsupport@uttamenergy.com','amita@navya.biz']
			if user not in users:
				frappe.throw("Sorry you can't delete")
