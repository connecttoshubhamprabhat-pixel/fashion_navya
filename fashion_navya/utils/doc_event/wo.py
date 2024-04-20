import frappe
import json
import re
from frappe.utils import cint, flt
from frappe import utils
from frappe.model.naming import make_autoname

@frappe.whitelist(allow_guest=True)
def autoname_wo_custom(doc,method):
	today=utils.today()[2:4]
	if doc.project:
		get_project_no=re.findall(r'\d+',doc.project)
		if get_project_no:
			doc.name=make_autoname('WO-'+get_project_no[0]+"-"+today+"-"+".##")


@frappe.whitelist(allow_guest=True)
def fetch_msrement(doc,method):
	if doc.sales_order:
		item=doc.production_item.split("-")
		y=[]
		if "MTM"  in  item:
			y.append("a")
		so=frappe.get_doc("Sales Order",doc.sales_order)
		if so.measurements and y:
			doc.measurements_child=[]
			for i in so.measurements:
				row = doc.append("measurements_child", {})
				row.parameter=i.parameter
				row.round=i.round
				row.label=i.label


@frappe.whitelist(allow_guest=True)
def bom_stage_changes(doc,method):
	item=doc.production_item
	bom_no=doc.bom_no
	item_split=item.split("-")
	if bom_no and "MTM" in item_split:
		bom_tb=frappe.get_doc("BOM",bom_no)
		bom_tb.cancel()
		bom=frappe.get_doc({'doctype': 'BOM',
				'item':bom_tb.item,
				"default_pattern":bom_tb.default_pattern,
		})
		for item in   bom_tb.items:
			row=bom.append('items', {})
			row.item_code=item.item_code
			row.qty=item.qty
			row.uom=item.uom

		if len(bom_tb.scrap_items)!=0:
			for sc in bom_tb.scrap_items:
				row=bom.append('scrap_items', {})
				row.item_code=sc.item_code
				row.stock_qty=sc.stock_qty

		if len(bom_tb.exploded_items)!=0:
			for ei in bom_tb.exploded_items:
				row=bom.append('exploded_items', {})
				row.item_code=ei.item_code
				row.stock_qty=ei.stock_qty

		if bom_tb.operations:
			bom.routing=bom_tb.routing
			bom.set('operations',bom_tb.operations)
			bom.with_operations = 1

		bom.set('plc_conversion_rate',bom_tb.plc_conversion_rate)
		bom.set("project",bom_tb.project)
		bom.conversion_rate=bom_tb.conversion_rate
		bom.insert(ignore_permissions=True)
		if bom:
			create_todo_bom(name=bom.name)
		bom.db_set("workflow_state","Changes Pending", update_modified=False)
		frappe.db.commit()


@frappe.whitelist()
def create_todo_bom(name=None):
	doctype="BOM"
	user_list=['sujeets@navyacustom.com']
	for i in user_list:
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		d['description']="Please check bom,MTM Item"
		d['reference_name']=name
		d['assigned_by']="amita@navya.biz"
		d['allocated_to']=i
		td=frappe.get_doc(d)
		td.insert()




@frappe.whitelist(allow_guest=True)
def fetch_items_wo(values=None):
	values=json.loads(values)
	project=values.get("project")
	items=[]
	get_items=frappe.db.sql("""select qty,bom_no,production_item from `tabWork Order` where docstatus=0 and project='{}'   """.format(project),as_dict=1)
	if len(get_items)!=0:
		duplicate=[]
		for i in get_items:
			if i['production_item'] not in duplicate:
				d={}
				d['item_code']=i['production_item']
				d['qty']=i['qty']
				d['bom']=i['bom_no']
				items.append(d)
				duplicate.append(i['production_item'])
	return items

@frappe.whitelist(allow_guest=True)
def fetch_attributes_so(doc,method):
	if doc.sales_order and doc.docstatus==0:
		so=frappe.get_doc("Sales Order",doc.sales_order)
		for i in so.items:
			if i.item_code==doc.production_item:
				doc.set("tdress",i.tdress)
				doc.set("custom_attributes",i.custom_attributes)
				doc.set("bottom_length",i.bottom_length)
				doc.set("bottom_waist",i.bottom_waist)
				doc.set("sleeve_length",i.sleeve_length)
				doc.set("plus",i.plus)
				doc.set("minus",i.minus)
				doc.set("custom_extra",i.custom_extra)
				doc.set("size",i.size)
				doc.set("custom_bust",i.custom_bust)
				doc.set("custom_top_waist",i.custom_top_waist)
				doc.set("custom_top_hip",i.custom_top_hip)
				doc.set("custom_lower_waist",i.custom_lower_waist)
				doc.set("custom_lower_hip",i.custom_lower_hip)
				doc.set("custom_sleeve_length",i.custom_sleeve_length)
				doc.set("custom_shoulder",i.custom_shoulder)
				doc.set("custom_bottom_length",i.custom_bottom_length)




#w/o items fetch status not started
@frappe.whitelist(allow_guest=True)
def wo_items_fetch_ns():
	items=[]
	get_items=frappe.db.sql("""select name,qty,bom_no,production_item from `tabWork Order` where docstatus=1 and status="Not Started"   """,as_dict=1)
	if len(get_items)!=0:
		duplicate=[]
		for i in get_items:
			if i['production_item'] not in duplicate:
				d={}
				d['item_code']=i['production_item']
				d['qty']=i['qty']
				d['bom']=i['bom_no']
				d['work_order']=i['name']
				items.append(d)
				duplicate.append(i['production_item'])
	return items





@frappe.whitelist(allow_guest=True)
def set_parent_item(doc,method):
	item=frappe.get_doc("Item",doc.production_item)
	if item.parent_item:
		if frappe.db.exists("Item",item.parent_item):
			doc.set("custom_item_smpl",item.parent_item)



#fetch sub order status of stock entry
@frappe.whitelist(allow_guest=True)
def fetch_status_in_wo(doc,method):
	if doc.stock_entry_type=="Send to Subcontractor" and doc.subcontracting_order and doc.custom_work_sub:
		sub_doc=frappe.get_doc("Work Order",doc.custom_work_sub)
		po_sub=frappe.get_doc("Subcontracting Order",doc.subcontracting_order)
		frappe.db.sql("""update `tabWork Order` set custom_supplier='{}' where docstatus=1 and name='{}'  """.format(po_sub.supplier,i['work_order']))
		frappe.db.sql("""update `tabWork Order` set custom_subcontracting_order='{}' where name='{}' """.format(doc.subcontracting_order,sub_doc.name))
		frappe.db.sql("""update `tabWork Order` set custom_materials_sent='{}' where name='{}' """.format(doc.workflow_state,doc.custom_work_sub))
		frappe.db.sql("""update `tabWork Order` set custom_date_sent='{}' where name='{}' """.format(doc.posting_date,sub_doc.name))
		get_sbr=frappe.db.sql("""select * from `tabSubcontracting Receipt` where docstatus=1 and purchase_order='{}'   """.format(po_sub.purchase_order),as_dict=1)
		if len(get_sbr)!=0:
			frappe.db.sql("""update `tabWork Order` set custom_subcontracting_receipt='{}' where docstatus=1 and name='{}'  """.format(get_sbr[0]['name'],i['work_order']))
			frappe.db.sql("""update `tabWork Order` set custom_sreceipt_date='{}' where docstatus=1 and name='{}'  """.format(get_sbr[0]['posting_date'],i['work_order']))
			frappe.db.sql("""update `tabWork Order` set custom_srstatus='{}' where docstatus=1 and name='{}'  """.format(get_sbr[0]['status'],i['work_order']))
			frappe.db.commit()




@frappe.whitelist(allow_guest=True)
def check_before_submit_disbaled_item(doc,method):
	for i in  doc.required_items:
		item=frappe.get_doc("Item",i.item_code)
		if item.disabled==1:
			msg="Disabled Item in Row {}".format(i.idx)
			frappe.throw(msg)






@frappe.whitelist(allow_guest=True)
def fetch_msrement_mr(doc,method):
	for s in doc.items:
		split_item=s.item_code.split("-")
		if "MTM" in split_item and s.sales_order:
			so=frappe.get_doc("Sales Order",s.sales_order)
			if so.measurements:
				doc.custom_mso=[]
				for i in so.measurements:
					row = doc.append("custom_mso", {})
					row.parameter=i.parameter
					row.round=i.round
					row.label=i.label



@frappe.whitelist(allow_guest=True)
def replace_items_wo(doc,method):
	items_problem=["SHNT50G.","POP001C","LYCFUSWHI"]
	if doc.required_items:
		for i in doc.required_items:
			if i.item_code in items_problem:
				if frappe.db.exists("Item",i.item_code+"-"+"New"):
					i.set("item_code",i.item_code+"-"+"New")
@frappe.whitelist(allow_guest=True)
def replace_items_bom(doc,method):
	items_problem=["SHNT50G.","POP001C","LYCFUSWHI"]
	if doc.items:
		for i in doc.items:
			if i.item_code in items_problem:
				if frappe.db.exists("Item",i.item_code+"-"+"New"):
					i.set("item_code",i.item_code+"-"+"New")


#fethc bin qty required_items
@frappe.whitelist(allow_guest=True)
def get_stock_raw(doc,method):
	lib_warehoues=['Libberheri  - NAVYA','Libberhedi finished Products - NAVYA','Semi Finished Libberhedi - NAVYA']
	delhi_warehoues=['Semi finished Sampling Unit - NAVYA','Navya Store Office - NAVYA','Sampling Unit - NAVYA']

	if doc.required_items:
		for i in doc.required_items:
			if doc.fg_warehouse not in delhi_warehoues and doc.fg_warehouse not in lib_warehoues:
				if frappe.db.exists("Warehouse","Purchase Station - NAVYA"):
					i.set('source_warehouse','Purchase Station - NAVYA')
				else:
					frappe.throw("Purchase Station - NAVYA is not exists")

			if doc.fg_warehouse in delhi_warehoues:
				get_bin_qty=frappe.db.sql("""select * from `tabBin` where item_code='{}' and actual_qty>0 and warehouse in (select name from `tabWarehouse` where parent_warehouse='Delhi Raw Material  - NAVYA')  """.format(i.item_code),as_dict=1)
				if len(get_bin_qty)!=0:
					for j in get_bin_qty:
						if j['actual_qty']>=i.required_qty:
							i.set('source_warehouse',j['warehouse'])
						else:
							if frappe.db.exists("Warehouse","Purchase Station - NAVYA"):
								i.set('source_warehouse','Purchase Station - NAVYA')
							else:
								frappe.throw("Purchase Station - NAVYA is not exists")
				else:
					if frappe.db.exists("Warehouse","Purchase Station - NAVYA"):
						i.set('source_warehouse','Purchase Station - NAVYA')
					else:
						frappe.throw("Purchase Station - NAVYA is not exists")





			if doc.fg_warehouse in lib_warehoues:
				get_bin_qty=frappe.db.sql("""select * from `tabBin` where item_code='{}' and actual_qty>0 and warehouse in (select name from `tabWarehouse` where parent_warehouse='Libberhedi Raw Material - NAVYA')   """.format(i.item_code),as_dict=1)
				if len(get_bin_qty)!=0:
					for j in get_bin_qty:
						if j['actual_qty']>=i.required_qty:
							i.set('source_warehouse',j['warehouse'])
						else:
							if frappe.db.exists("Warehouse","Purchase Station - NAVYA"):
								i.set('source_warehouse','Purchase Station - NAVYA')

							else:
								frappe.throw("Purchase Station - NAVYA is not exists")
				else:
					if frappe.db.exists("Warehouse","Purchase Station - NAVYA"):
						i.set('source_warehouse','Purchase Station - NAVYA')
					else:
						frappe.throw("Purchase Station - NAVYA is not exists")





@frappe.whitelist(allow_guest=True)
def finish_work_order_added_old():
	#split production items
	get_wo=frappe.db.sql("""select name from `tabWork Order` where docstatus=1 and CAST(creation as date) >= DATE_SUB(CURRENT_DATE, INTERVAL 3 MONTH) """,as_dict=1)
	for i in wo:
		wodoc=frappe.get_doc("Work Order",i['name'])
		item=wodoc.production_item.split("-")
		all_kits=["HEK","DPK","BPK","k"]
		get_last_word=item[-1]
		if get_last_word in kits:
			parent_item="-".join(item[:-1])
			if frappe.db.exists("Item",parent_item):
				if wodoc.production_plan:
					get_work_order=frappe.db.sql("""select name from `tabWork Order` where production_item='{}' and production_plan='{}'  """.format(parent_item,wodoc.production_plan),as_dict=1)
					if len(get_work_order)!=0:
						frappe.db.sql("""update `tabWork Order` set custom_finish_order='{}' where name='{}'  """.format(get_work_order[0]['name'],wodoc.name))
						#frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def finish_work_order_added_old():
    # get work order
	wo_list = frappe.get_all(
        "Work Order",
        filters={"docstatus": 1, "creation": (">", frappe.utils.add_months(frappe.utils.nowdate(), -3))},
        pluck="name"
    )

	for wo_name in wo_list:
		wodoc = frappe.get_doc("Work Order", wo_name)
		items = wodoc.production_item.split("-")
		last_word = items[-1]
		kits = ["HEK", "DPK", "BPK", "k"]
		if last_word in kits:
			parent_item = "-".join(items[:-1])
			if frappe.db.exists("Item", parent_item) and wodoc.production_plan:
				work_order = frappe.get_value(
                    "Work Order",
                    {"production_item": parent_item, "production_plan": wodoc.production_plan,"docstatus":1},
                    "name"
                )

				if work_order:
					print(work_order,"a")
					frappe.db.set_value("Work Order", wodoc.name, "custom_finish_order", work_order)
					frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def finish_work_order_added(doc,method):
	items = doc.production_item.split("-")
	last_word = items[-1]
	kits = ["HEK", "DPK", "BPK", "k"]
	if last_word in kits:
		parent_item = "-".join(items[:-1])
		if frappe.db.exists("Item", parent_item) and doc.production_plan:
			work_order = frappe.get_value(
                "Work Order",
                {"production_item": parent_item, "production_plan":doc.production_plan,"docstatus":1},
                "name"
            )

			if work_order:
				frappe.db.set_value("Work Order",doc.name, "custom_finish_order", work_order)
				frappe.db.commit()

#apr 20/2024 13:09
@frappe.whitelist(allow_guest=True)
def incharge_work_order(doc,method):
	get_warehouses=frappe.db.sql("""select user from `tabIncharge WO` where warehouse='{}'   """.format(doc.fg_warehouse),as_dict=1)
	if len(get_warehouses)!=0:
		doc.set("incharge",get_warehouses[0]['user'])

#apr 20/24 13:09
@frappe.whitelist(allow_guest=True)
def se_check_incharge_before_receive(doc, method):
	user = frappe.session.user
	user_warehouse_list = []

	# Get warehouses assigned to the user
	user_warehouses = frappe.get_all("Incharge WO", filters={"user": user}, fields=["warehouse"])
	user_warehouse_list = [wh["warehouse"] for wh in user_warehouses]


	if not doc.ignore_custom and doc.stock_entry_type == "Material Transfer for Manufacture" and doc.work_order:
		wo_doc = frappe.get_doc("Work Order", doc.work_order)
		if wo_doc.incharge:

			incharge_warehouse = wo_doc.fg_warehouse

			if incharge_warehouse not in user_warehouse_list:
				msg = f"Only {wo_doc.incharge} can receive because they are in charge of this Work Order. You can verify in the 'Incharge' field of the Work Order."
				frappe.throw(msg)
