import frappe
import json
from frappe import utils

#only subcontracting
@frappe.whitelist(allow_guest=True)
def set_sell_item_po(doc,method):
	if doc.is_subcontracted:
		for i in doc.items:
			if i.fg_item:
				names=i.fg_item
				ns=names.split("-")
				names_1=ns[:-1]
				join_name="-".join(names_1)
				if frappe.db.exists("Item",join_name):
					i.set("fg_parent",join_name)
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
	#frappe.throw("apr42")
	if doc.is_subcontracted and  doc.custom_skip_work_order==0:
		#frappe.throw("apr4")
		for i in doc.items:
			if i.fg_parent and not  i.production_plan:
				get_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus=1 and production_item='{}'  and status in ('In Process','Not Started')  """.format(i.fg_parent),as_dict=1)
				if get_wo:
					i.set('work_order',get_wo[0]['name'])
				else:
					frappe.throw("Work order is missing for row :- {}".format(i.idx))


			if i.fg_parent and i.production_plan:
				get_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus=1 and production_item='{}'  and status in ('In Process','Not Started') and production_plan='{}' """.format(i.fg_parent,i.production_plan),as_dict=1)
				if get_wo:
					i.set('work_order',get_wo[0]['name'])
				else:
					frappe.throw("Work order is missing for row :- {}".format(i.idx))




@frappe.whitelist(allow_guest=True)
def level_wise_po(items=None,name=None):
	#frappe.throw("hello")
	date=str(utils.today())
	items=json.loads(items)
	po=frappe.get_doc("Purchase Order",name)
	level_zero=[]
	level_one=[]
	level_two=[]
	level_three=[]
	if items:
		for i in items:
			if i.get("production_plan"):
				pp=frappe.get_doc("Production Plan",i.get("production_plan"))
				get_level=frappe.db.sql(""" select  bom_level from `tabProduction Plan Sub Assembly Item` where docstatus=1 and production_item='{}' and parent='{}'  """.format(i.get("fg_item"),pp.name),as_dict=1)
				if get_level:
					if get_level[0]['bom_level']==0:
						level_zero.append(i.get("fg_item"))

					if get_level[0]['bom_level']==1:
						level_one.append(i.get("fg_item"))

					if get_level[0]['bom_level']==2:
						level_two.append(i.get("fg_item"))
					if get_level[0]['bom_level']==3:
						level_three.append(i.get("fg_item"))


	if level_zero:
		d={"doctype":"Purchase Order","supplier":"Production Plan"}
		d['schedule_date']=date
		d['is_subcontracted']=1
		d['custom_bom_level']=0
		d['custom_automated']=1
		doc=frappe.get_doc(d)
		for i in level_zero:
			get_items_details=frappe.db.sql(""" select * from `tabPurchase Order Item` where fg_item='{}' and parent='{}' """.format(i,name),as_dict=1)
			row = doc.append("items", {})
			row.fg_item=i
			row.schedule_date=date
			row.item_code="DP-2024"
			row.qty=1
			if len(get_items_details)!=0:
				row.fg_item_qty=get_items_details[0]['fg_item_qty']
				row.production_plan=get_items_details[0]['production_plan']
				row.production_plan=get_items_details[0]['production_plan']
				row.bom=get_items_details[0]['bom']
				row.description=get_items_details[0]['description']

		doc.insert(ignore_permissions=True)
		frappe.msgprint("Level 0 created")


	if level_one:
		d={"doctype":"Purchase Order","supplier":"Production Plan"}
		d['schedule_date']=date
		d['is_subcontracted']=1
		d['custom_bom_level']=1
		d['custom_automated']=1
		doc=frappe.get_doc(d)
		for i in level_one:
			get_items_details=frappe.db.sql(""" select * from `tabPurchase Order Item` where fg_item='{}' and parent='{}' """.format(i,name),as_dict=1)
			row = doc.append("items", {})
			row.schedule_date=date
			row.fg_item=i
			row.item_code="DP-2024"
			row.qty=1
			if len(get_items_details)!=0:
				row.fg_item_qty=get_items_details[0]['fg_item_qty']
				row.production_plan=get_items_details[0]['production_plan']
				row.production_plan=get_items_details[0]['production_plan']
				row.bom=get_items_details[0]['bom']
				row.description=get_items_details[0]['description']

		doc.insert(ignore_permissions=True)
		frappe.msgprint("Level 1 created")


	if level_two:
		d={"doctype":"Purchase Order","supplier":"Production Plan"}
		d['schedule_date']=date
		d['is_subcontracted']=1
		d['custom_bom_level']=2
		d['custom_automated']=1
		doc=frappe.get_doc(d)
		for i in level_two:
			get_items_details=frappe.db.sql(""" select * from `tabPurchase Order Item` where fg_item='{}' and parent='{}' """.format(i,name),as_dict=1)
			row = doc.append("items", {})
			row.schedule_date=date
			row.fg_item=i
			row.item_code="DP-2024"
			row.qty=1
			if len(get_items_details)!=0:
				row.fg_item_qty=get_items_details[0]['fg_item_qty']
				row.production_plan=get_items_details[0]['production_plan']
				row.production_plan=get_items_details[0]['production_plan']
				row.bom=get_items_details[0]['bom']
				row.description=get_items_details[0]['description']

		doc.insert(ignore_permissions=True)
		frappe.msgprint("Level 2 created")



	if level_three:
		d={"doctype":"Purchase Order","supplier":"Production Plan"}
		d['schedule_date']=date
		d['is_subcontracted']=1
		d['custom_bom_level']=3
		doc=frappe.get_doc(d)
		for i in level_three:
			get_items_details=frappe.db.sql(""" select * from `tabPurchase Order Item` where fg_item='{}' and parent='{}' """.format(i,name),as_dict=1)
			row = doc.append("items", {})
			row.fg_item=i
			row.schedule_date=date
			row.item_code="DP-2024"
			row.qty=1
			if len(get_items_details)!=0:
				row.fg_item_qty=get_items_details[0]['fg_item_qty']
				row.production_plan=get_items_details[0]['production_plan']
				row.production_plan=get_items_details[0]['production_plan']
				row.bom=get_items_details[0]['bom']
				row.description=get_items_details[0]['description']

		doc.insert(ignore_permissions=True)
		frappe.msgprint("Level 3 created")





@frappe.whitelist(allow_guest=True)
def check_automated_po(doc,method):
	plan=[]
	if doc.items:
		for i in doc.items:
			if i.idx==0 and i.production_plan:
				plan.append(i.production_plan)


	if plan and doc.custom_automated==0:
		pl=frappe.get_doc("Production Plan",plan[0])
		if pl.custom_automated==1:
			doc.set("custom_automated",1)

	if doc.is_subcontracted and doc.items:
		for i in doc.items:
			i.set("qty",i.fg_item_qty)



@frappe.whitelist(allow_guest=True)
def subcontacted_check(doc,method):
	po=[]
	for j in doc.items:
		if j.idx==0 and j.purchase_order:
			po.append(j.purchase_order)

	if po:
		pdoc=frappe.get_doc("Purchase Order",po[0])
		if pdoc.is_subcontracted:
			get_so=frappe.db.sql(""" select name from `tabSubcontracting Receipt` where purchase_order='{}' and docstatus=1 """.format(po[0]),as_dict=1)
			if len(get_so)==0:
				frappe.throw("Subcontracting Receipt is not submitted")




@frappe.whitelist(allow_guest=True)
def check_purchase_from_production(doc,method):
	production=[]
	for i in doc.items:
		if i.idx==0:
			if i.material_request:
				mr=frappe.get_doc("Material Request",i.material_request)
				for j in mr.items:
					if j.production_plan:
						production.append("yes")
	if production:
		doc.set("custom_from_p",1)






frappe.whitelist(allow_guest=True)
def get_wo_set_po_condition(doc,method):
	if doc.is_subcontracted and  doc.custom_skip_work_order==0 and doc.workflow_state in ['Authorisation Pending','Authorised']:
		for i in doc.items:
			if i.fg_parent and not  i.production_plan:
				get_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus=1 and production_item='{}'  and status in ('In Process','Not Started')  """.format(i.fg_parent),as_dict=1)
				if get_wo:
					i.set('work_order',get_wo[0]['name'])
				else:
					frappe.throw("Work order is missing for row :- {}".format(i.idx))


			if i.fg_parent and i.production_plan:
				get_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus=1 and production_item='{}'  and status in ('In Process','Not Started') and production_plan='{}' """.format(i.fg_parent,i.production_plan),as_dict=1)
				if get_wo:
					i.set('work_order',get_wo[0]['name'])
				else:
					frappe.throw("Work order is missing for row :- {}".format(i.idx))



@frappe.whitelist(allow_guest=True)
def get_wo_set_po_condition_btn(name=None):
		po = frappe.get_doc("Purchase Order", name)
		work_order_lists=[]
		for item in po.items:
				if not item.item_code:
						frappe.throw("Service Item is missing")
				fg_item = item.fg_item.split("-")
				fg_parent = "-".join(fg_item[:-1])
				idx = item.idx
				# Check if the parent item exists
				if not frappe.db.exists("Item", fg_parent):
						frappe.throw("Row No {} parent does not exist".format(idx))

				# Define filter conditions for the work order query
				filters = {"docstatus": 1, "production_item": fg_parent, "status": ["in", ["In Process", "Not Started"]]}
				if item.production_plan:
						filters["production_plan"] = item.production_plan

				# Fetch relevant work orders
				work_orders = frappe.get_list("Work Order", filters=filters, fields=["name", "qty"], limit=10)
				# Handle cases where work orders are missing
				if not work_orders:
					frappe.throw("Work order is missing for row: {}".format(idx))


				# Update Purchase Order item fields
				item.fg_parent = fg_parent
				for  mqty in  work_orders:
					if mqty['name'] not in work_order_lists:
						check_wo=frappe.db.sql("""select name from `tabPurchase Order Item` where docstatus<2 and work_order='{}'  """.format(mqty['name']),as_dict=1)
						if len(check_wo)==0:
							item.work_order = mqty['name']
							item.custom_qtywo=mqty['qty']
							work_order_lists.append(mqty['name'])

		po.save()
		frappe.msgprint("updated successfully")
