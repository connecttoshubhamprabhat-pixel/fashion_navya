import frappe
import json
import re
from frappe.utils import cint, flt,today
from frappe import utils
from frappe.model.naming import make_autoname
from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry as ste

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
	so_name=[]
	if doc.material_request:
		mdoc=frappe.get_doc("Material Request",doc.material_request)
		for qtr in mdoc.items:
			if qtr.sales_order:
				so_name.append(qtr.sales_order)
				break
		if mdoc.custom_issue_description:
			doc.set("custom_issue_description",mdoc.custom_issue_description)
		
		for im in mdoc.items:
			if im.custom_sales_order_illustration:
				doc.set("custom_illustration_image",im.custom_sales_order_illustration)

	
	if doc.sales_order:
		so_name.append(doc.sales_order)
	
	else:
		if doc.production_plan:
			get_mr=[]
			pp=frappe.get_doc("Production Plan",doc.production_plan)
			for mr in pp.po_items:
				if mr.tem_code==doc.production_item:
					get_mr.append(mr.material_request)
					break
			
			if get_mr:
				mr_doc=frappe.get_doc("Material Request",get_mr[0])
				for mr_item in mr_doc.items:
					if mr_item.sales_order:
						so_name.append(mr_item.sales_order)
						break

	print(so_name,"so_name333333333333333333")		
	if so_name:
		so=frappe.get_doc("Sales Order",so_name[-1])
		doc.set("over_all_level",so.over_all_level)
		doc.set("custom_outfit",so.outfit)
		for i in so.items:
			if i.item_code==doc.production_item:
				doc.set("tdress",i.custom_top_length)
				doc.set("custom_attributes",i.custom_attributes)
				doc.set("custom_armhole",i.custom_armhole)
				doc.set("custom_waist",i.custom_waists)
				doc.set("bottom_length",i.bottom_length)
				doc.set("bottom_waist",i.custom_bottom_waist)
				doc.set("sleeve_length",i.sleeve_length)
				doc.set("plus",i.plus)
				doc.set("minus",i.minus)
				doc.set("custom_extra",i.custom_extra)
				doc.set("size",i.size)
				doc.set("overall_fit",i.custom_overall_fit)
				doc.set("custom_bust",i.custom_bust)
				doc.set("custom_top_waist",i.custom_top_waist)
				doc.set("custom_top_hip",i.custom_top_hip)
				doc.set("custom_lower_waist",i.custom_lower_waist)
				doc.set("custom_lower_hip",i.custom_lower_hip)
				doc.set("custom_sleeve_length",i.custom_sleeve_length)
				doc.set("custom_shoulder",i.custom_shoulder)
				doc.set("custom_bottom_length",i.custom_bottom_length)
				frappe.db.commit()
	
	frappe.db.commit()




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


	if doc.ignore_custom==0 and doc.stock_entry_type == "Material Transfer for Manufacture" and doc.work_order:
		wo_doc = frappe.get_doc("Work Order", doc.work_order)
		if wo_doc.incharge:

			incharge_warehouse = wo_doc.fg_warehouse

			if incharge_warehouse not in user_warehouse_list:
				msg = f"Only {wo_doc.incharge} can receive because they are in charge of this Work Order. You can verify in the 'Incharge' field of the Work Order."
				frappe.msgprint(msg)




@frappe.whitelist(allow_guest=True)
def set_kit_group(doc,method):
	item=doc.production_item
	split=item.split("-")
	kit_attributes=["k","BPK","DPK","HEK","RTW","SMPL","PRSMPL","PPSMPL"]
	name_att=split[-1]
	if name_att in kit_attributes:
		doc.db_set("custom_kit_item_group",name_att, update_modified=False)



@frappe.whitelist(allow_guest=True)
def set_kit_group_old():
	get_wo=frappe.db.sql(""" select name ,production_item from `tabWork Order` where  custom_kit_item_group is null and docstatus=1    """,as_dict=1)
	if get_wo:
		for i in get_wo:
			doc=frappe.get_doc("Work Order",i['name'])
			print(doc.name)
			item=doc.production_item
			split=item.split("-")
			kit_attributes=["k","BPK","DPK","HEK","PPSMPL","PRSMPL","RTW","SMPL"]
			name_att=split[-1]
			if name_att in kit_attributes:
				frappe.db.sql("""update `tabWork Order` set custom_kit_item_group='{}' where name='{}'   """.format(name_att,doc.name))
				frappe.db.commit()


#This code create the single stock entry for all selected work orders.
@frappe.whitelist(allow_guest=True)
def make_stock_entry(work_orders):
	pass
	# work_orders = json.loads(work_orders)
	# wo_list = []
	# for wo in work_orders:
	# 	wo_list.append(wo.get("name"))

	# try:
	# 	if not work_orders:
	# 		frappe.throw("No work orders provided.")
		

	# 	if not isinstance(work_orders, list) or len(work_orders) == 0:
	# 		frappe.throw("Work orders should be a non-empty list.")

	# 	stock_entry = frappe.new_doc("Stock Entry")
	# 	for wo in work_orders:
	# 		stock_entry.append("custom_work_order_link",{
	# 			"work_order":wo.get("name")
	# 		})
	# 	stock_entry.stock_entry_type = "Material Transfer for Manufacture"
	# 	stock_entry.custom_permitted = True

	# 	item_dict = {}  
	# 	work_order_ref = None  

	# 	for work_order in work_orders:
	# 		wo_doc = frappe.get_doc("Work Order", work_order)

	# 		if wo_doc.status == "Not Started":
	# 			wo_doc.update_status(status="In Progress")

	# 		if not work_order_ref:
	# 			work_order_ref = wo_doc.name
	# 			stock_entry.naming_series = "MAT-MTFM-.YYYY.-"
	# 			stock_entry.work_order = wo_doc.name
	# 			stock_entry.to_warehouse = wo_doc.wip_warehouse
	# 			stock_entry.db_set("from_bom", 1)
	# 			stock_entry.db_set("bom_no", wo_doc.bom_no)
	# 			stock_entry.custom_consolidated_transfer = 1
	# 			stock_entry.use_multi_level_bom = wo_doc.use_multi_level_bom
	# 			stock_entry.fg_completed_qty = flt(wo_doc.qty) - flt(wo_doc.produced_qty)

	# 		for item in wo_doc.required_items:
	# 			item_code = item.item_code
	# 			qty = item.required_qty
	# 			from_warehouse = item.source_warehouse

	# 			warehouse = frappe.db.get_value("Warehouse", from_warehouse)
	# 			if not warehouse:
	# 				frappe.throw(f"Warehouse {from_warehouse} does not exist for item {item_code}")

	# 			if item_code in item_dict:
	# 				item_dict[item_code]["qty"] += qty 
	# 			else:
	# 				item_dict[item_code] = {
	# 					"item_code": item_code,
	# 					"qty": qty,
	# 					"from_warehouse": from_warehouse
	# 				}

	# 	for item in item_dict.values():
	# 		stock_entry_item = stock_entry.append("items", {})
	# 		stock_entry_item.item_code = item["item_code"]
	# 		stock_entry_item.qty = item["qty"]
	# 		stock_entry_item.s_warehouse = item["from_warehouse"]

	# 	stock_entry.save(ignore_permissions = True)
	# 	return stock_entry.name

	# except Exception as e:
	# 	frappe.log_error(f"Error in make_stock_entry: {str(e)}", "make_stock_entry")
	# 	frappe.throw(f"Error processing work orders: {str(e)}")







@frappe.whitelist()
def make__consolidate_stock_entry(work_orders):
	qty=None
	target_warehouse=None
	work_orders = json.loads(work_orders)
	wo_list = []
	for wo in work_orders:
		wo_list.append(wo.get("name"))
		work_order_id = wo.get("name")
		purpose = "Manufacture"
		work_order = frappe.get_doc("Work Order", work_order_id)
		if not frappe.db.get_value("Warehouse", work_order.wip_warehouse, "is_group"):
			wip_warehouse = work_order.wip_warehouse
		else:
			wip_warehouse = None

		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.naming_series = "MAT-STE-.YYYY.-"
		stock_entry.purpose = purpose
		stock_entry.work_order = work_order_id
		stock_entry.company = work_order.company
		stock_entry.from_bom = 1
		stock_entry.bom_no = work_order.bom_no
		stock_entry.use_multi_level_bom = work_order.use_multi_level_bom
		# accept 0 qty as well
		stock_entry.fg_completed_qty = (
			qty if qty is not None else (flt(work_order.qty) - flt(work_order.produced_qty))
		)

		if work_order.bom_no:
			stock_entry.inspection_required = frappe.db.get_value("BOM", work_order.bom_no, "inspection_required")

		if purpose == "Material Transfer for Manufacture":
			stock_entry.to_warehouse = wip_warehouse
			stock_entry.project = work_order.project
		else:
			stock_entry.from_warehouse = wip_warehouse
			stock_entry.to_warehouse = work_order.fg_warehouse
			stock_entry.project = work_order.project

		if purpose == "Disassemble":
			stock_entry.from_warehouse = work_order.fg_warehouse
			stock_entry.to_warehouse = target_warehouse or work_order.source_warehouse

		stock_entry.set_stock_entry_type()
		stock_entry.get_items()

		if purpose != "Disassemble":
			stock_entry.set_serial_no_batch_for_finished_good()

		stock_entry.as_dict()
		stock_entry.save(ignore_permissions = True)
	



#<-----------this code is create the stock entry seperate for based on work order.--------------------->
@frappe.whitelist(allow_guest=True)
def make_stock_entry(work_orders):
	try:
		if not work_orders:
			frappe.throw("No work orders provided")
		
		if not work_orders:
			frappe.throw("Invalid work orders data")

		
		wo_doc = frappe.get_doc("Work Order", work_orders)
		qty=None
		if wo_doc.status == "Not Started":
			wo_doc.update_status(status="In Progress")
			stock_entry = frappe.new_doc("Stock Entry")
			stock_entry.stock_entry_type = "Material Transfer for Manufacture"
			stock_entry.work_order = wo_doc.name
			stock_entry.to_warehouse = wo_doc.wip_warehouse
			stock_entry.custom_permitted = True
			stock_entry.db_set("from_bom", 1)
			stock_entry.db_set("bom_no", wo_doc.bom_no)
			stock_entry.use_multi_level_bom = wo_doc.use_multi_level_bom

			stock_entry.fg_completed_qty = (
				qty if qty is not None else (flt(wo_doc.qty) - flt(wo_doc.produced_qty))
			)
			if not frappe.db.get_value("Warehouse", wo_doc.wip_warehouse, "is_group"):
				wip_warehouse = wo_doc.wip_warehouse
			else:
				wip_warehouse = None

			if wo_doc.bom_no:
				stock_entry.inspection_required = frappe.db.get_value("BOM", wo_doc.bom_no, "inspection_required")

			if stock_entry.stock_entry_type == "Material Transfer for Manufacture":
				stock_entry.db_set("to_warehouse",wip_warehouse)
				stock_entry.db_set("project",wo_doc.project)

			# stock_entry.set_stock_entry_type()
			# stock_entry.get_items()

			# if purpose != "Disassemble":
			# 	stock_entry.set_serial_no_batch_for_finished_good()


			items = []
			for item in wo_doc.required_items:
				items.append({
					"item_code": item.item_code,
					"qty": item.required_qty,
					"from_warehouse": item.source_warehouse,
					"target_warehouse": wo_doc.fg_warehouse})

			for item in items:
				warehouse = frappe.db.get_value("Warehouse", item['from_warehouse'])
				if not warehouse:
					frappe.throw(f"Warehouse {item['from_warehouse']} does not exist for item {item['item_code']}")

				stock_entry_item = stock_entry.append('items', {})
				stock_entry_item.item_code = item['item_code']
				stock_entry_item.qty = item['qty']
				stock_entry_item.s_warehouse = item['from_warehouse']
				
				# stock_entry_item.t_warehouse = item['target_warehouse']

			stock_entry.save()
			# wo_doc.db_set("status", "In Process")
			# wo_doc.save()
			# stock_entry.submit()

		return "Success"

	except json.JSONDecodeError as e:
		frappe.log_error(f"JSON Decode Error: {e}", "make_stock_entry")
		frappe.throw(f"Error processing work orders: {str(e)}")


def update_stock_entry(self,method):
	if self.stock_entry_type == "Material Transfer for Manufacture":
		doc = frappe.get_doc("Work Order", {"name":self.work_order})
		doc.db_set("status","In Process")
		doc.save()


@frappe.whitelist()
def submit_stock_entry(selected_docs):
	selected_docs = json.loads(selected_docs)
	for documents in selected_docs:
		doc = frappe.get_doc("Stock Entry",documents.get("name"))
		doc.submit()
		frappe.msgprint("Stock Entry Submitted Successfully ",doc.name)

		
@frappe.whitelist()
def make_stock_entry_production(name):
	get_data = frappe.get_doc("Production Plan", name)
	
	doc = frappe.new_doc("Stock Entry")
	doc.stock_entry_type = "Manufacture"
	doc.naming_series = "MAT-MF-.YYYY.-."
	doc.posting_date = today()
	doc.rfse = "Stock Transfer"
	doc.custom_linked_production_plan = name

	finished_good_added = False
	item_dict = {}

	for data in get_data.po_items:
		item_code = data.item_code
		qty = data.planned_qty
		target_warehouse = data.warehouse
		uom = data.stock_uom

		is_finished_item = not finished_good_added
		if is_finished_item:
			finished_good_added = True

		if item_code in item_dict:
			item_dict[item_code]["qty"] += qty 
		else:
			item_dict[item_code] = {
				"item_code": item_code,
				"uom": uom,
				"t_warehouse": "Navya Store Office - NAVYA",
				"qty": qty,
				"is_finished_item": is_finished_item
			}

	for raw in get_data.mr_items:
		item_code = raw.item_code
		qty = raw.quantity
		source_warehouse = raw.warehouse

		if item_code in item_dict:
			item_dict[item_code]["qty"] += qty  
		else:
			item_dict[item_code] = {
				"item_code": item_code,
				"s_warehouse": "Sujeet Ji WIP - NAVYA",
				"qty": qty
			}

	for item in item_dict.values():
		doc.append("items", item)

	doc.save(ignore_permissions=True)
	frappe.msgprint(f"Stock Entry {doc.name} Created.")

	return doc.name

@frappe.whitelist()
def make_stock_entry_from_material_request(name):
	get_data = frappe.get_doc("Material Request",name)
	
	if get_data.material_request_type == "Manufacture":
		doc = frappe.new_doc("Stock Entry")
		doc.stock_entry_type = "Manufacture"
		doc.posting_date = today()
		doc.rfse = "Stock Transfer"
		doc.custom_material_request = name

		finished_good_added = False
		for data in get_data.items:
			item_code = data.item_code
			qty = data.qty
			target_warehouse = data.warehouse
			uom = data.uom
			
			is_finished_item = not finished_good_added
			if is_finished_item:
				finished_good_added = True
			
			doc.append("items",{
				"item_code":item_code,
				"uom":uom,
				"t_warehouse":target_warehouse,
				"qty":qty,
				"is_finished_item": is_finished_item,
			})

		doc.save(ignore_permissions = True)
		frappe.msgprint("Stock Entry Created.",doc.name)
		return doc.name

@frappe.whitelist()
def create_stock_entry_from_poduction(name,source_warehouse,target_warehouse):
	get_data = frappe.get_doc("Production Plan", name)
	doc = frappe.new_doc("Stock Entry")
	doc.stock_entry_type = "Material Transfer for Manufacture"
	doc.naming_series = "MAT-MTFM-.YYYY.-.####"
	doc.posting_date = today()
	doc.custom_linked_production_plan = name
	for data in get_data.mr_items:
		doc.append("items",{
			"item_code" : data.item_code,
			"s_warehouse" : source_warehouse,
			"t_warehouse" : target_warehouse,
			"qty" : data.quantity,
		})


	doc.save(ignore_permissions=True)
	frappe.msgprint(f"Stock Entry {doc.name} Created.")
	return doc.name

@frappe.whitelist()
def create_stock_entry_from_poduction_mat_transf(name,source_warehouse,target_warehouse):
	get_data = frappe.get_doc("Production Plan", name)
	doc = frappe.new_doc("Stock Entry")
	doc.stock_entry_type = "Material Transfer"
	doc.naming_series = "MAT-MT-.YYYY.-.####"
	doc.posting_date = today()
	doc.custom_linked_production_plan = name
	for data in get_data.mr_items:
		doc.append("items",{
			"item_code" : data.item_code,
			"s_warehouse" : source_warehouse,
			"t_warehouse" : target_warehouse,
			"qty" : data.quantity,
		})


	doc.save(ignore_permissions=True)
	frappe.msgprint(f"Stock Entry {doc.name} Created.")
	return doc.name


@frappe.whitelist()
def create_sub_asmb_stock_entry_from_poduction(name,source_warehouse,target_warehouse):
	get_data = frappe.get_doc("Production Plan", name)
	doc = frappe.new_doc("Stock Entry")
	doc.stock_entry_type = "Material Transfer for Manufacture"
	doc.naming_series = "MAT-MTFM-.YYYY.-.####"
	doc.posting_date = today()
	doc.custom_linked_production_plan = name
	for data in get_data.sub_assembly_items:
		doc.append("items",{
			"item_code" : data.production_item,
			"s_warehouse" : source_warehouse,
			"t_warehouse" : target_warehouse,
			"qty" : data.qty,
		})


	doc.save(ignore_permissions=True)
	frappe.msgprint(f"Stock Entry {doc.name} Created.")
	return doc.name

	
@frappe.whitelist()
def create_sub_asmb_stock_entry_from_poduction_mat_transf(name,source_warehouse,target_warehouse):
	get_data = frappe.get_doc("Production Plan", name)
	doc = frappe.new_doc("Stock Entry")
	doc.stock_entry_type = "Material Transfer"
	doc.naming_series = "MAT-MT-.YYYY.-.####"
	doc.posting_date = today()
	doc.custom_linked_production_plan = name
	for data in get_data.sub_assembly_items:
		doc.append("items",{
			"item_code" : data.production_item,
			"s_warehouse" : source_warehouse,
			"t_warehouse" : target_warehouse,
			"qty" : data.qty,
		})


	doc.save(ignore_permissions=True)
	frappe.msgprint(f"Stock Entry {doc.name} Created.")
	return doc.name



@frappe.whitelist()
def create_sub_asmb_stock_entry_from_poduction_manufacturing(name,target_warehouse):
	get_data = frappe.get_doc("Production Plan", name)
	doc = frappe.new_doc("Stock Entry")
	doc.stock_entry_type = "Manufacture"
	doc.naming_series = "MAT-MF-.YYYY.-.####"
	doc.posting_date = today()
	doc.custom_linked_production_plan = name


	finished_good_added = False
	for data in get_data.sub_assembly_items:
		item_code = data.production_item
		qty = data.qty
		uom = data.uom
		
		is_finished_item = not finished_good_added
		if is_finished_item:
			finished_good_added = True
				
		doc.append("items",{
			"item_code":item_code,
			"uom":uom,
			"t_warehouse":target_warehouse,
			"qty":qty,
			"is_finished_item": is_finished_item,
		})


	doc.save(ignore_permissions=True)
	frappe.msgprint(f"Stock Entry {doc.name} Created.")
	return doc.name


@frappe.whitelist()
def create_poduction_asmb_stock_entry_manufacturing(name, source_warehouse, target_warehouse):
	get_data = frappe.get_doc("Production Plan", name)

	if not get_data.po_items:
		frappe.throw("No PO Items found in Production Plan.")

	for po_item in get_data.po_items:
		base_code = po_item.item_code
		qty = po_item.planned_qty
		uom = po_item.stock_uom

		doc = frappe.new_doc("Stock Entry")
		doc.stock_entry_type = "Manufacture"
		doc.posting_date = today()
		doc.rfse = "Stock Transfer"
		doc.naming_series = "MAT-MF-.YYYY.-."
		doc.custom_linked_production_plan = name

		doc.append("items", {
			"item_code": base_code,
			"uom": uom,
			"t_warehouse": target_warehouse,
			"qty": qty,
			"is_finished_item": 1
		})

		for sub in get_data.sub_assembly_items:
			if sub.production_item.startswith(base_code):
				doc.append("items", {
					"item_code": sub.production_item,
					"s_warehouse": source_warehouse,
					"qty": sub.qty
				})

		doc.save(ignore_permissions=True)
		frappe.msgprint(f"Stock Entry {doc.name} Created for {base_code}")
