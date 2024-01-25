import frappe

#only subcontracting
@frappe.whitelist(allow_guest=True)
def set_sell_item_po(doc,method):
	if doc.is_subcontracted:
		for i in doc.items:
			if i.production_plan:
				get_bom=frappe.db.sql("""select * from `tabProduction Plan Sub Assembly Item` where docstatus=1 and production_item='{}' and parent='{}'  """.format(i.fg_item,i.production_plan),as_dict=1)
				if len(get_bom)!=0:
					for p in get_bom:
						item=frappe.get_doc("Item",p['parent_item_code'])
						i.set("fg_parent",item.name)
						i.set("fg_name_parent",item.item_name)
						i.set("project",item.project)
						get_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus=1 and production_item='{}' and status in ('In Process','Not Started') """.format(item.name),as_dict=1)
						if get_wo:
							i.set("work_order",get_wo[0]['name'])
							continue

			else:
				if i.fg_item:
					names=i.fg_item
					ns=names.split("-")
					names_1=ns[:-1]
					join_name="-".join(names_1)
					#frappe.msgprint("aa {}".format(i.fg_item))
					if frappe.db.exists("Item",join_name):
						i.set("fg_parent",join_name)
						check_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus=1 and production_item='{}'  """.format(join_name),as_dict=1)
						if len(check_wo)!=0:
							i.set("work_order",check_wo[0]['name'])
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




frappe.whitelist(allow_guest=True)
def get_wo_set_po(doc,method):
	if doc.is_subcontracted and doc.docstatus==0 and doc.custom_skip_work_order==0:
		for i in doc.items:
			if i.fg_parent:
				get_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus=1 and production_item='{}'  and status in ('In Process','Not Started')  """.format(i.fg_parent),as_dict=1)
				if get_wo:
					i.set('work_order',get_wo[0]['name'])
				else:
					frappe.throw("Work order is missing for row :- {}".format(i.idx))
