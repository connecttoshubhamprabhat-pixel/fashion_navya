
# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import copy
import json
import datetime

import frappe
from frappe import _, msgprint
from frappe import _, msgprint
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.query_builder.functions import IfNull, Sum
from frappe.utils import (
	add_days,
	ceil,
	cint,
	comma_and,
	flt,
	get_link_to_form,
	getdate,
	now_datetime,
	nowdate,
)
from frappe.utils.csvutils import build_csv_response
from pypika.terms import ExistsCriterion

from erpnext.manufacturing.doctype.bom.bom import get_children as get_bom_children
from erpnext.manufacturing.doctype.bom.bom import validate_bom_no
from erpnext.manufacturing.doctype.work_order.work_order import get_item_details
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.get_item_details import get_conversion_factor
from erpnext.stock.utils import get_or_make_bin
from erpnext.utilities.transaction_base import validate_uom_is_integer

from erpnext.manufacturing.doctype.production_plan.production_plan import(ProductionPlan,
get_items_for_material_requests,get_warehouse_list,get_exploded_items,get_bin_details,
get_material_request_items,get_materials_from_other_locations)


class CustomProductionPlan(ProductionPlan):
	@frappe.whitelist()
	def get_pending_material_requests(self):
		bom = frappe.qb.DocType("BOM")
		mr = frappe.qb.DocType("Material Request")
		mr_item = frappe.qb.DocType("Material Request Item")

		pending_mr_query = (
				frappe.qb.from_(mr)
			.from_(mr_item)
			.select(mr.name, mr.transaction_date)
			.distinct()
			.where(
				(mr_item.parent == mr.name)
				& (mr.material_request_type == "Manufacture")
				& (mr.docstatus == 1)
				&(mr.custom_bom==1)
				& (mr.status != "Stopped")
				& (mr.company == self.company)
				& (mr_item.qty > IfNull(mr_item.ordered_qty, 0))
				& (
					ExistsCriterion(
						frappe.qb.from_(bom)
						.select(bom.name)
						.where((bom.item == mr_item.item_code) & (bom.is_active == 1))
					)
				)
			)
		)

		if self.from_date:
			pending_mr_query = pending_mr_query.where(mr.transaction_date >= self.from_date)

		if self.to_date:
			pending_mr_query = pending_mr_query.where(mr.transaction_date <= self.to_date)

		if self.warehouse:
			pending_mr_query = pending_mr_query.where(mr_item.warehouse == self.warehouse)

		if self.item_code:
			pending_mr_query = pending_mr_query.where(mr_item.item_code == self.item_code)

        #custom code
		if self.custom_production_plan_type=="Sales Order":
			pending_mr_query = pending_mr_query.where(mr.custom_is_so==1)
			pending_mr_query = pending_mr_query.where(mr.custom_bom==1)

		if self.custom_production_plan_type=="Without Sales Order":
			pending_mr_query = pending_mr_query.where(mr.custom_is_so==0)
			pending_mr_query = pending_mr_query.where(mr.custom_bom==1)


		pending_mr = pending_mr_query.run(as_dict=True)
		print(pending_mr,'pending_mr')
		self.add_mr_in_table(pending_mr)


	def create_work_order(self, item):
		from erpnext.manufacturing.doctype.work_order.work_order import OverProductionError
		if flt(item.get("qty")) <= 0:
			return

		wo = frappe.new_doc("Work Order")
		wo.update(item)
		wo.planned_start_date = item.get("planned_start_date") or item.get("schedule_date")
		if item.get("warehouse"):
			wo.fg_warehouse = item.get("warehouse")

		wo.set_work_order_operations()
		wo.set_required_items()
		print(wo.material_request,"aaa")
		if wo.material_request:
			mdoc=frappe.get_doc("Material Request",wo.material_request)
			if mdoc.custom_issue_description:
				wo.set("custom_issue_description",mdoc.custom_issue_description)
				
			if mdoc.custom_issue_image:
				wo.set("custom_issue_image",mdoc.custom_issue_image)
				
			for im in mdoc.items:
				if im.custom_sales_order_illustration:
					wo.set("custom_illustration_image",im.custom_sales_order_illustration)

			so_name=[]
			for qtr in mdoc.items:
				if qtr.sales_order:
					wo.sales_order=qtr.sales_order
					so_name.append(qtr.sales_order)
					break
			#new
			if so_name:
					sow=frappe.get_doc("Sales Order",so_name[-1])
					wo.set("over_all_level",sow.over_all_level)
					wo.set("custom_outfit",sow.outfit)
					for so_t in sow.items:
						if so_t.item_code==wo.production_item:
							wo.set("tdress",so_t.custom_top_length)
							wo.set("custom_attributes",so_t.custom_attributes)
							wo.set("custom_armhole",so_t.custom_armhole)
							wo.set("custom_waist",so_t.custom_waists)
							wo.set("bottom_length",so_t.bottom_length)
							wo.set("bottom_waist",so_t.custom_bottom_waist)
							wo.set("sleeve_length",so_t.sleeve_length)
							wo.set("plus",so_t.plus)
							wo.set("minus",so_t.minus)
							wo.set("custom_extra",so_t.custom_extra)
							wo.set("size",so_t.size)
							wo.set("overall_fit",so_t.custom_overall_fit)
							wo.set("custom_bust",so_t.custom_bust)
							wo.set("custom_top_waist",so_t.custom_top_waist)
							wo.set("custom_top_hip",so_t.custom_top_hip)
							wo.set("custom_lower_waist",so_t.custom_lower_waist)
							wo.set("custom_lower_hip",so_t.custom_lower_hip)
							wo.set("custom_sleeve_length",so_t.custom_sleeve_length)
							wo.set("custom_shoulder",so_t.custom_shoulder)
							wo.set("custom_bottom_length",so_t.custom_bottom_length)
		
			
		#frappe.throw("hellodd")
		try:
			wo.flags.ignore_mandatory = True
			wo.flags.ignore_validate = True
			wo.insert()
			if wo.production_plan:
				pp=frappe.get_doc("Production Plan",wo.production_plan)
				if pp.custom_automated==1:
					wo.set("status","Not Started")
					wo.submit()
				#return wo.name
		except Exception as e:
			custom_logs(py_method="create_work_order",error_name=e)
			pass





@frappe.whitelist(allow_guest=True)
def automated_plan():
	warehouses_mr=["Purchase Station - NAVYA"]
	d={"doctype":"Production Plan","get_items_from":"Material Request","custom_automated":1}
	d['custom_production_plan_type']="Sales Order"
	doc=frappe.get_doc(d)
	pending_mr=get_pending_material_requests_custom()
	doc.set("material_requests", [])
	for data in pending_mr:
		doc.append(
                "material_requests",
				            {"material_request": data.name, "material_request_date": data.transaction_date},
			)

	doc_dict=doc.as_dict()
	get_mr_items_custom(doc)
	get_sub_assembly_items(doc, manufacturing_type=None)
	doc.insert()
	doc.set("for_warehouse","Purchase Station - NAVYA")
	for w in warehouses_mr:
		warehouse_list_mr=[{"warehouse":w}]
		dump_Warehoues=json.dumps(warehouse_list_mr)
		mr_items=get_items_for_material_requests_custom(doc,warehouses=dump_Warehoues,get_parent_warehouse_data=None)
		if mr_items:
			for d in mr_items:
				print(d.get("item_code"))
				item_doc=frappe.get_doc("Item",d.get("item_code"))
				if item_doc.disabled==1:
					continue

				doc.append(
					"mr_items",
					{
							"item_code":d.get("item_code"),
						"item_name":d.get("item_name"),
						"description":d.get("description"),
						"stock_uom":d.get("stock_uom"),
						"warehouse":d.get("warehouse"),
						"required_bom_qty":d.get("required_bom_qty"),
						"projected_qty":d.get("projected_qty"),
						"actual_qty":d.get("actual_qty"),
						"ordered_qty":d.get("ordered_qty"),
						"planned_qty":d.get("planned_qty"),
						"reserved_qty_for_production":d.get("reserved_qty_for_production"),
						"safety_stock":d.get("safety_stock"),
						"quantity":d.get("quantity"),
						"material_request_type":d.get("material_request_type"),


						},
					)


	doc.submit()
	make_material_request_custom(doc)
	make_work_order(doc)
	frappe.db.commit()



@frappe.whitelist()
def make_work_order(self):
	from erpnext.manufacturing.doctype.work_order.work_order import get_default_warehouse

	wo_list, po_list = [], []
	subcontracted_po = {}
	default_warehouses = get_default_warehouse()

	self.make_work_order_for_finished_goods(wo_list, default_warehouses)
	self.make_work_order_for_subassembly_items(wo_list, subcontracted_po, default_warehouses)
	print(type(subcontracted_po),'subcontracted_po')
	print(po_list,'po_lists')
	make_subcontracted_purchase_order_custom(self,subcontracted_po, po_list)
	self.show_list_created_message("Work Order",wo_list)
	self.show_list_created_message("Purchase Order",po_list)

	if not wo_list:
		frappe.msgprint(_("No Work Orders were created"))

def make_work_order_for_finished_goods(self, wo_list, default_warehouses):
	items_data = self.get_production_items()

	for key, item in items_data.items():
		if self.sub_assembly_items:
			item["use_multi_level_bom"] = 0

		set_default_warehouses(item, default_warehouses)
		work_order = self.create_work_order(item)
		frappe.db.commit()




@frappe.whitelist(allow_guest=True)
def automated_plan_without_so():
	warehouses_mr=["Purchase Station - NAVYA"]
	warehouse_list_mr=[{"warehouse":"Purchase Station - NAVYA"}]
	dump_Warehoues=json.dumps(warehouse_list_mr)
	d={"doctype":"Production Plan","get_items_from":"Material Request","custom_automated":1}
	d['custom_production_plan_type']="Without Sales Order"
	doc=frappe.get_doc(d)
	pending_mr=get_pending_material_requests_without_wo()
	doc.set("material_requests", [])
	for data in pending_mr:
		print(data,'mr')
		doc.append(
                "material_requests",
				            {"material_request": data.name, "material_request_date": data.transaction_date},
			)

	doc_dict=doc.as_dict()
	get_mr_items_custom(doc)
	get_sub_assembly_items(doc, manufacturing_type=None)
	doc.insert()
	#doc_into_dumps=json.loads(doc_dict)
	dump_doc=json.dumps(doc_dict,default=datetime_handler)
	doc.set("for_warehouse","Purchase Station - NAVYA")
	# print(dump_doc,"dumpdoc")
	for w in warehouses_mr:
		warehouse_list_mr=[{"warehouse":w}]
		dump_Warehoues=json.dumps(warehouse_list_mr)
		mr_items=get_items_for_material_requests_custom(doc,warehouses=dump_Warehoues,get_parent_warehouse_data=None)

		if mr_items:
			for d in mr_items:
				print(d.get("item_code"))
				item_doc=frappe.get_doc("Item",d.get("item_code"))
				if item_doc.disabled==1:
					continue
				doc.append(
				"mr_items",
				{
						"item_code":d.get("item_code"),
						"item_name":d.get("item_name"),
						"description":d.get("description"),
						"stock_uom":d.get("stock_uom"),
						"warehouse":d.get("warehouse"),
						"required_bom_qty":d.get("required_bom_qty"),
						"projected_qty":d.get("projected_qty"),
						"actual_qty":d.get("actual_qty"),
						"ordered_qty":d.get("ordered_qty"),
						"planned_qty":d.get("planned_qty"),
						"reserved_qty_for_production":d.get("reserved_qty_for_production"),
						"safety_stock":d.get("safety_stock"),
						"quantity":d.get("quantity"),
						"material_request_type":d.get("material_request_type"),


						},
					)
	doc.submit()
	make_material_request_custom(doc)
	# print(doc.name,"doc.name")
	make_work_order(doc)
	frappe.db.commit()





@frappe.whitelist(allow_guest=True)
def get_pending_material_requests_custom():
	bom = frappe.qb.DocType("BOM")
	mr = frappe.qb.DocType("Material Request")
	mr_item = frappe.qb.DocType("Material Request Item")
	# pending_mr_query = (
	# 	frappe.qb.from_(mr)
	# 	.from_(mr_item)
	# 	.select(mr.name, mr.transaction_date)
	# 	.distinct()
	# 	.where(
	# 		(mr_item.parent == mr.name)
	# 		& (mr.material_request_type == "Manufacture")
	# 		& (mr.docstatus == 1)
	# 		& (mr.custom_is_so == 1)
	# 		& (mr.custom_bom == 1)
	# 		& (mr.status != "Stopped")
	# 		& (mr.company ==frappe.defaults.get_user_default("company"))
	# 		& (mr_item.qty > IfNull(mr_item.ordered_qty, 0))
	# 		& (
	# 			ExistsCriterion(
	# 				frappe.qb.from_(bom)
	# 				.select(bom.name)
	# 				.where((bom.item == mr_item.item_code) & (bom.is_active == 1))
	# 			)
	# 		)
	# 	)
	# )

	pending_mr_query = """
SELECT DISTINCT
    mr.name, 
    mr.transaction_date
FROM 
    `tabMaterial Request` mr
JOIN 
    `tabMaterial Request Item` mr_item ON mr_item.parent = mr.name
WHERE 
    mr.material_request_type = 'Manufacture'
    AND mr.docstatus = 1
    AND mr.custom_is_so = 1
    AND mr.custom_bom = 1
    AND mr.status != 'Stopped'
    AND mr_item.qty > IFNULL(mr_item.ordered_qty, 0)
	
"""

	# pending_mr = pending_mr_query.run(as_dict=True)
	pending_mr = frappe.db.sql(pending_mr_query,as_dict=True)
	print('pending_mr-----',pending_mr)
	return pending_mr



@frappe.whitelist(allow_guest=True)
def get_pending_material_requests_without_wo():
	bom = frappe.qb.DocType("BOM")
	mr = frappe.qb.DocType("Material Request")
	mr_item = frappe.qb.DocType("Material Request Item")
	pending_mr_query = (
		frappe.qb.from_(mr)
		.from_(mr_item)
		.select(mr.name, mr.transaction_date)
		.distinct()
		.where(
			(mr_item.parent == mr.name)
			& (mr.material_request_type == "Manufacture")
			& (mr.docstatus == 1)
			& (mr.custom_is_so == 0)
			& (mr.custom_bom == 1)
			& (mr.status != "Stopped")
			& (mr.company ==frappe.defaults.get_user_default("company"))
			& (mr_item.qty > IfNull(mr_item.ordered_qty, 0))
			& (
				ExistsCriterion(
					frappe.qb.from_(bom)
					.select(bom.name)
					.where((bom.item == mr_item.item_code) & (bom.is_active == 1))
				)
			)
		)
	)

	pending_mr = pending_mr_query.run(as_dict=True)
	return pending_mr


@frappe.whitelist(allow_guest=True)
def get_mr_items_custom(self):
	print("131",self.get("material_requests"))
	if not self.get("material_requests") or not self.get_so_mr_list(
		"material_request", "material_requests"
		):
		frappe.throw(
			_("Please fill the Material Requests table"), title=_("Material Requests Required")
		)


	mr_list = self.get_so_mr_list("material_request", "material_requests")
	print(mr_list)

	bom = frappe.qb.DocType("BOM")
	mr_item = frappe.qb.DocType("Material Request Item")

	items_query = (
		frappe.qb.from_(mr_item)
		.select(
			mr_item.parent,
			mr_item.name,
			mr_item.item_code,
			mr_item.warehouse,
			mr_item.description,
			((mr_item.qty - mr_item.ordered_qty) * mr_item.conversion_factor).as_("pending_qty"),
		)
		.distinct()
		.where(
			(mr_item.parent.isin(mr_list))
			& (mr_item.docstatus == 1)
			& (mr_item.qty > mr_item.ordered_qty)
			& (
				ExistsCriterion(
					frappe.qb.from_(bom)
					.select(bom.name)
					.where((bom.item == mr_item.item_code) & (bom.is_active == 1))
				)
			)
		)
	)

	if self.item_code:
		items_query = items_query.where(mr_item.item_code == self.item_code)

	items = items_query.run(as_dict=True)

	self.add_items(items)
	self.calculate_total_planned_qty()




@frappe.whitelist()
def get_sub_assembly_items(self, manufacturing_type=None):
    #print("a2Z")
    "Fetch sub assembly items and optionally combine them."
    self.sub_assembly_items = []
    sub_assembly_items_store = []  # temporary store to process all subassembly items
    for row in self.po_items:
        if self.skip_available_sub_assembly_item and not row.warehouse:
            frappe.throw(_("Row #{0}: Please select the FG Warehouse in Assembly Items").format(row.idx))

        if not row.item_code:
            frappe.throw(_("Row #{0}: Please select Item Code in Assembly Items").format(row.idx))

        if not row.bom_no:
            frappe.throw(_("Row #{0}: Please select the BOM No in Assembly Items").format(row.idx))

        bom_data = []
        warehouse = (
            (self.sub_assembly_warehouse or row.warehouse)
            if self.skip_available_sub_assembly_item
            else None
        )

        get_sub_assembly_items_custom(row.bom_no, bom_data, row.planned_qty, self.company, warehouse=warehouse)
        self.set_sub_assembly_items_based_on_level(row, bom_data, manufacturing_type)
        sub_assembly_items_store.extend(bom_data)

    if self.combine_sub_items:
        # Combine subassembly items
        sub_assembly_items_store = self.combine_subassembly_items(sub_assembly_items_store)

    sub_assembly_items_store.sort(key=lambda d: d.bom_level, reverse=True)  # sort by bom level
    for idx, row in enumerate(sub_assembly_items_store):
        row.idx = idx + 1
        self.append("sub_assembly_items", row)

    self.set_default_supplier_for_subcontracting_order()




def get_sub_assembly_items_custom(bom_no, bom_data, to_produce_qty, company, warehouse=None, indent=0):
    data = get_bom_children(parent=bom_no)
    for d in data:
        if d.expandable:
            parent_item_code = frappe.get_cached_value("BOM", bom_no, "item")
            stock_qty = (d.stock_qty / d.parent_bom_qty) * flt(to_produce_qty)

            if warehouse:
                bin_dict = get_bin_details(d, company, for_warehouse=warehouse)

                if bin_dict and bin_dict[0].projected_qty > 0:
                    if bin_dict[0].projected_qty > stock_qty:
                        continue
                    else:
                        stock_qty = stock_qty - bin_dict[0].projected_qty

            bom_data.append(frappe._dict(
					{
						"parent_item_code": parent_item_code,
						"description": d.description,
						"production_item": d.item_code,
						"item_name": d.item_name,
						"stock_uom": d.stock_uom,
						"uom": d.stock_uom,
						"bom_no": d.value,
						"is_sub_contracted_item": d.is_sub_contracted_item,
						"bom_level": indent,
						"indent": indent,
						"supplier":"Production Plan",
						"stock_qty": stock_qty,
					}
				)
			)

            if d.value:
                get_sub_assembly_items_custom(d.value, bom_data, stock_qty, company, warehouse, indent=indent + 1)



@frappe.whitelist(allow_guest=True)
def send_nofify_wo(doc,method):
	item=doc.production_item.split("-")
	if "MTM" in item:
		user_list=['sujeets@navyacustom.com']
		for i in user_list:
			d={'doctype':"ToDo","priority":"High","reference_type":doc.doctype}
			d['description']="MTM WOrd Order"
			d['reference_name']=doc.name
			d['assigned_by']="amita@navya.biz"
			d['allocated_to']=i
			td=frappe.get_doc(d)
			td.insert()
			frappe.db.commit()


	if "RTW" in item and "DP" in item and doc.fg_warehouse=="Navya Store Office - NAVYA":
		user_list=['veer@example.com']
		for i in user_list:
			d={'doctype':"ToDo","priority":"High","reference_type":doc.doctype}
			d['description']="RTW WOrd Order"
			d['reference_name']=doc.name
			d['assigned_by']="amita@navya.biz"
			d['allocated_to']=i
			td=frappe.get_doc(d)
			td.insert()
			frappe.db.commit()

	if "RTW" in item and "BP" in item and doc.fg_warehouse=="Libberheri  - NAVYA":
		user_list=['anchala@example.com','akansha@example.com']
		for i in user_list:
			d={'doctype':"ToDo","priority":"High","reference_type":doc.doctype}
			d['description']="RTW WOrd Order for Libberheri"
			d['reference_name']=doc.name
			d['assigned_by']="amita@navya.biz"
			d['allocated_to']=i
			td=frappe.get_doc(d)
			td.insert()
			frappe.db.commit()




def create_work_order_custom(self, item):
    from erpnext.manufacturing.doctype.work_order.work_order import OverProductionError
    if flt(item.get("qty")) <= 0:
        return

    wo = frappe.new_doc("Work Order")
    wo.update(item)
    wo.planned_start_date = item.get("planned_start_date") or item.get("schedule_date")

    if item.get("warehouse"):
        wo.fg_warehouse = item.get("warehouse")

    wo.set_work_order_operations()
    wo.set_required_items()

    try:
        wo.flags.ignore_mandatory = True
        wo.flags.ignore_validate = True
        frappe.db.msgprint("a1")
        print('aprint')
        wo.insert()
        wo.submit()
        frappe.db.commit()
        return wo.name
    except OverProductionError:
        pass



@frappe.whitelist(allow_guest=True)
def submit_work_order(doc,method):
    if doc.production_plan and doc.material_request and doc.docstatus==0:
        pp=frappe.get_doc("Production Plan",doc.production_plan)
        if pp.custom_automated==1:
            doc.submit()


@frappe.whitelist(allow_guest=True)
def send_nofify_mr_custom():
	get_mr=frappe.db.sql("""select name from `tabMaterial Request` where docstatus<2 and custom_bom=0 and custom_is_so=1  """,as_dict=1)
	mrs=[]
	if get_mr:
		for m in get_mr:
			mrs.append(m['name'])

		mr_str=" ".join(mrs)
		user_list=['veer@example.com']
		for i in user_list:
			print("a2")
			d={'doctype':"ToDo","priority":"High","reference_type":"Material Request"}
			d['description']=mr_str
			d['reference_name']
			d['assigned_by']="amita@navya.biz"
			d['allocated_to']=i
			td=frappe.get_doc(d)
			td.insert()
			frappe.db.commit()


@frappe.whitelist()
def get_items_for_material_requests_custom(doc, warehouses=None, get_parent_warehouse_data=None):
	#if isinstance(doc, str):
		#doc = frappe._dict(json.loads(doc))
	doc=doc.as_dict()
	print(type(doc),"type2")
	print(doc,'doc9')

	if warehouses:
		warehouses=[{"warehouse":"Raw material - NAVYA"}]
		warehouses = list(set(get_warehouse_list_custom(warehouses)))

		if (
			doc.get("for_warehouse")
			and not get_parent_warehouse_data
			and doc.get("for_warehouse") in warehouses
		):
			warehouses.remove(doc.get("for_warehouse"))
			if "Libberheri Work In Progress - NAVYA" in warehouses:
				warehouses.remove("Libberheri Work In Progress - NAVYA")
			if "Libberheri  - NAVYA" in warehouses:
				warehouses.remove("Libberheri  - NAVYA")

			if "Sampling Unit - NAVYA" in warehouses:
				warehouses.remove('Sampling Unit - NAVYA')


	doc["mr_items"] = []

	po_items = doc.get("po_items") if doc.get("po_items") else doc.get("items")

	if doc.get("sub_assembly_items"):
		for sa_row in doc.sub_assembly_items:
			sa_row = frappe._dict(sa_row)
			if sa_row.type_of_manufacturing == "Material Request":
				po_items.append(
					frappe._dict(
						{
							"item_code": sa_row.production_item,
							"required_qty": sa_row.qty,
							"include_exploded_items": 0,
						}
					)
				)

	# Check for empty table or empty rows
	if not po_items or not [row.get("item_code") for row in po_items if row.get("item_code")]:
		frappe.throw(
			_("Items to Manufacture are required to pull the Raw Materials associated with it."),
			title=_("Items Required"),
		)

	company = doc.get("company")
	ignore_existing_ordered_qty = doc.get("ignore_existing_ordered_qty")
	include_safety_stock = doc.get("include_safety_stock")

	so_item_details = frappe._dict()

	sub_assembly_items = {}
	if doc.get("skip_available_sub_assembly_item"):
		for d in doc.get("sub_assembly_items"):
			sub_assembly_items.setdefault((d.get("production_item"), d.get("bom_no")), d.get("qty"))

	for data in po_items:
		if not data.get("include_exploded_items") and doc.get("sub_assembly_items"):
			data["include_exploded_items"] = 1

		planned_qty = data.get("required_qty") or data.get("planned_qty")
		ignore_existing_ordered_qty = (
			data.get("ignore_existing_ordered_qty") or ignore_existing_ordered_qty
		)
		warehouse = doc.get("for_warehouse")

		item_details = {}
		if data.get("bom") or data.get("bom_no"):
			if data.get("required_qty"):
				bom_no = data.get("bom")
				include_non_stock_items = 1
				include_subcontracted_items = 1 if data.get("include_exploded_items") else 0
			else:
				bom_no = data.get("bom_no")
				include_subcontracted_items = doc.get("include_subcontracted_items")
				include_non_stock_items = doc.get("include_non_stock_items")

			if not planned_qty:
				frappe.throw(_("For row {0}: Enter Planned Qty").format(data.get("idx")))

			if bom_no:
				if (
					data.get("include_exploded_items")
					and doc.get("sub_assembly_items")
					and doc.get("skip_available_sub_assembly_item")
				):
					item_details = get_raw_materials_of_sub_assembly_items(
						item_details,
						company,
						bom_no,
						include_non_stock_items,
						sub_assembly_items,
						planned_qty=planned_qty,
					)

				elif data.get("include_exploded_items") and include_subcontracted_items:
					# fetch exploded items from BOM
					item_details = get_exploded_items(
						item_details, company, bom_no, include_non_stock_items, planned_qty=planned_qty, doc=doc
					)
				else:
					item_details = get_subitems(
						doc,
						data,
						item_details,
						bom_no,
						company,
						include_non_stock_items,
						include_subcontracted_items,
						1,
						planned_qty=planned_qty,
					)
		elif data.get("item_code"):
			item_master = frappe.get_doc("Item", data["item_code"]).as_dict()
			purchase_uom = item_master.purchase_uom or item_master.stock_uom
			conversion_factor = (
				get_uom_conversion_factor(item_master.name, purchase_uom) if item_master.purchase_uom else 1.0
			)

			item_details[item_master.name] = frappe._dict(
				{
					"item_name": item_master.item_name,
					"default_bom": doc.bom,
					"purchase_uom": purchase_uom,
					"default_warehouse": item_master.default_warehouse,
					"min_order_qty": item_master.min_order_qty,
					"default_material_request_type": item_master.default_material_request_type,
					"qty": planned_qty or 1,
					"is_sub_contracted": item_master.is_subcontracted_item,
					"item_code": item_master.name,
					"description": item_master.description,
					"stock_uom": item_master.stock_uom,
					"conversion_factor": conversion_factor,
					"safety_stock": item_master.safety_stock,
				}
			)

		sales_order = doc.get("sales_order")

		for item_code, details in item_details.items():
			so_item_details.setdefault(sales_order, frappe._dict())
			if item_code in so_item_details.get(sales_order, {}):
				so_item_details[sales_order][item_code]["qty"] = so_item_details[sales_order][item_code].get(
					"qty", 0
				) + flt(details.qty)
			else:
				so_item_details[sales_order][item_code] = details

	mr_items = []
	for sales_order, item_code in so_item_details.items():
		item_dict = so_item_details[sales_order]
		for details in item_dict.values():
			bin_dict = get_bin_details(details, doc.company, warehouse)
			bin_dict = bin_dict[0] if bin_dict else {}

			if details.qty > 0:
				items =get_material_request_items_custom(
					details,
					sales_order,
					company,
					ignore_existing_ordered_qty,
					include_safety_stock,
					warehouse,
					bin_dict,
				)
				if items:
					mr_items.append(items)

	if (not ignore_existing_ordered_qty or get_parent_warehouse_data) and warehouses:
		new_mr_items = []
		for item in mr_items:
			get_materials_from_other_locations(item, warehouses, new_mr_items, company)

		mr_items = new_mr_items

	if not mr_items:
		to_enable = frappe.bold(_("Ignore Existing Projected Quantity"))
		warehouse = frappe.bold(doc.get("for_warehouse"))
		message = (
			_(
				"As there are sufficient raw materials, Material Request is not required for Warehouse {0}."
			).format(warehouse)
			+ "<br><br>"
		)
		message += _("If you still want to proceed, please enable {0}.").format(to_enable)

		frappe.msgprint(message, title=_("Note"))


	#print(mr_items,"aaaaaaa")
	return mr_items

def myconverter(o):
	if isinstance(o, datetime.datetime):
		return o.__str__()

def datetime_handler(x):
	if isinstance(x, datetime.datetime):
		return x.isoformat()





@frappe.whitelist()
def make_material_request_custom(self):
	"""Create Material Requests grouped by Sales Order and Material Request Type"""
	material_request_list = []
	material_request_map = {}

	for item in self.mr_items:
		item_doc = frappe.get_cached_doc("Item", item.item_code)

		material_request_type = item.material_request_type or item_doc.default_material_request_type

		# key for Sales Order:Material Request Type:Customer
		key = "{}:{}:{}".format(item.sales_order, material_request_type, item_doc.customer or "")
		schedule_date = item.schedule_date or add_days(nowdate(), cint(item_doc.lead_time_days))

		if not key in material_request_map:
			# make a new MR for the combination
			material_request_map[key] = frappe.new_doc("Material Request")
			material_request = material_request_map[key]
			material_request.update(
				{
					"transaction_date": nowdate(),
					"status": "Draft",
					"company": self.company,
					"material_request_type": material_request_type,
					"customer": item_doc.customer or "",
				}
			)
			material_request_list.append(material_request)
		else:
			material_request = material_request_map[key]

		# add item
		material_request.append(
			"items",
			{
				"item_code": item.item_code,
				"from_warehouse": item.from_warehouse
				if material_request_type == "Material Transfer"
				else None,
				"qty": item.quantity,
				"schedule_date": schedule_date,
				"warehouse": item.warehouse,
				"sales_order": item.sales_order,
				"production_plan": self.name,
				"material_request_plan_item": item.name,
				"project": frappe.db.get_value("Sales Order", item.sales_order, "project")
				if item.sales_order
				else None,
			},
		)

	for material_request in material_request_list:
		material_request.flags.ignore_permissions = 1
		material_request.run_method("set_missing_values")
		material_request.save(ignore_permissions=True)
		#material_request.submit()
		frappe.db.commit()




@frappe.whitelist()
def create_mr_for_reorder(items=None,values=None,project=None):
	items=json.loads(items)
	values=json.loads(values)
	mrq=values.get("mrq")
	request_for=values.get("warehouse")
	rlevel=values.get("rlevel")
	rqty=values.get("rqty")
	parent=frappe.db.sql("""select parent_warehouse from `tabWarehouse` where name='{}'  """.format(request_for),as_dict=1)
	if len(parent)==0:
		frappe.throw("This warehouse is not under Any warehouse")
		return

	if items:
		get_re_order_items=[]
		project_doc=frappe.get_doc("Project",project)
		if project_doc.re_order:
			for p in project_doc.re_order:
				get_re_order_items.append(p.item_code)
		project_saved=0

		for i in items:
			print(i)
			doc=frappe.get_doc("Item",i)
			row = doc.append("reorder_levels", {})
			row.warehouse_reorder_level=rlevel
			row.warehouse_reorder_qty=rqty
			row.material_request_type=mrq
			row.warehouse=request_for
			row.warehouse_group=parent[0]['parent_warehouse']
			doc.save(ignore_permissions=True)
			frappe.msgprint("Added Reorder")
			#code for project
			if i not in get_re_order_items:
				project_saved+=1
				rowp =project_doc.append("re_order", {})
				rowp.item_code=i
				rowp.warehouse=request_for
				rowp.min=rqty

		if project_saved>0:
			project_doc.save()




def get_warehouse_list_custom(warehouses):
	warehouse_list = []
	if isinstance(warehouses, str):
		warehouses = json.loads(warehouses)

	for row in warehouses:
		child_warehouses = frappe.db.get_descendants("Warehouse", row.get("warehouse"))
		if child_warehouses:

			warehouse_list.extend(child_warehouses)
		else:
			warehouse_list.append(row.get("warehouse"))

	if "Sampling Unit - NAVYA" in warehouse_list:
		warehouse_list.remove("Sampling Unit - NAVYA")
	return warehouse_list


@frappe.whitelist()
def custom_logs(py_method=None,error_name=None):
	d={"doctype":"Custom Logs","info":error_name}
	doc=frappe.get_doc(d)
	try:
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
	except:
		pass



@frappe.whitelist()
def create_todo_wo(wo=None):
	doctype="Work Order"
	user_list=['vivekd@navyacustom.com']
	#drawing_user=["sweetyd@navyacustom.com"]
	for i in user_list:
		d={'doctype':"ToDo","priority":"High","reference_type":doctype}
		d['description']="Please Its Bom,May have issue"
		d['reference_name']=wo
		d['assigned_by']="amita@navya.biz"
		d['allocated_to']=i
		try:
			td=frappe.get_doc(d)
			td.insert()
			frappe.db.commit()
		except:
			pass




def get_material_request_items_custom(row, sales_order, company, ignore_existing_ordered_qty, include_safety_stock, warehouse, bin_dict
):
	total_qty = row["qty"]
	required_qty = 0
	if ignore_existing_ordered_qty or bin_dict.get("projected_qty", 0) < 0:
		required_qty = total_qty
	elif total_qty > bin_dict.get("projected_qty", 0):
		required_qty = total_qty - bin_dict.get("projected_qty", 0)
	if required_qty > 0 and required_qty < row["min_order_qty"]:
		required_qty = row["min_order_qty"]
	item_group_defaults = get_item_group_defaults(row.item_code, company)

	if not row["purchase_uom"]:
		row["purchase_uom"] = row["stock_uom"]

	if row["purchase_uom"] != row["stock_uom"]:
		if not (row["conversion_factor"] or frappe.flags.show_qty_in_stock_uom):
			print()
			pass

			if required_qty>0:
				required_qty = required_qty / 1
			else:
				required_qty=1

	if frappe.db.get_value("UOM", row["purchase_uom"], "must_be_whole_number"):
		required_qty = ceil(required_qty)

	if include_safety_stock:
		required_qty += flt(row["safety_stock"])

	item_details = frappe.get_cached_value(
		"Item", row.item_code, ["purchase_uom", "stock_uom"], as_dict=1
	)
	conversion_factor = 1.0
	if (
		row.get("default_material_request_type") == "Purchase"
		and item_details.purchase_uom
		and item_details.purchase_uom != item_details.stock_uom
	):
		conversion_factor = (
			get_conversion_factor(row.item_code, item_details.purchase_uom).get("conversion_factor") or 1.0
		)

	if required_qty > 0:
		return {
			"item_code": row.item_code,
			"item_name": row.item_name,
			"quantity": required_qty / conversion_factor,
			"conversion_factor": conversion_factor,
			"required_bom_qty": total_qty,
			"stock_uom": row.get("stock_uom"),
			"warehouse": warehouse
			or row.get("source_warehouse")
			or row.get("default_warehouse")
			or item_group_defaults.get("default_warehouse"),
			"safety_stock": row.safety_stock,
			"actual_qty": bin_dict.get("actual_qty", 0),
			"projected_qty": bin_dict.get("projected_qty", 0),
			"ordered_qty": bin_dict.get("ordered_qty", 0),
			"reserved_qty_for_production": bin_dict.get("reserved_qty_for_production", 0),
			"min_order_qty": row["min_order_qty"],
			"material_request_type": row.get("default_material_request_type"),
			"sales_order": sales_order,
			"description": row.get("description"),
			"uom": row.get("purchase_uom") or row.get("stock_uom"),
		}




@frappe.whitelist()
def get_subcontracting_boms_for_finished_goods_custom(fg_items: str | list) -> dict:
	frappe.throw("aa")
	if fg_items:
		if type(fg_items)=="set":
			fg_items=list(fg_items)
		print(fg_items,"gf91hello")
		filters = {"is_active": 1}

		if isinstance(fg_items, list):
			filters["finished_good"] = ["in", fg_items]
		else:
			filters["finished_good"] = fg_items

		if subcontracting_boms := frappe.get_all("Subcontracting BOM", filters=filters, fields=["*"]):
			if isinstance(fg_items, list):
				return {d.finished_good: d for d in subcontracting_boms}
			else:
				return subcontracting_boms[0]

	return {}


@frappe.whitelist()
def make_subcontracted_purchase_order_custom(self, subcontracted_po, purchase_orders):
	print("hello1035")
	if not subcontracted_po:
		return

	print(subcontracted_po,'subcontracted_po')
	print(purchase_orders,'purchase_orders')
	print(type(purchase_orders),"purchase_orders")
	print(type(subcontracted_po),"subcontracted_po")

	for supplier, po_list in subcontracted_po.items():
		po = frappe.new_doc("Purchase Order")
		po.company = self.company
		po.supplier = supplier
		po.schedule_date = getdate(po_list[0].schedule_date) if po_list[0].schedule_date else nowdate()
		po.is_subcontracted = 1
		for row in po_list:
			po_data = {
				"fg_item": row.production_item,
				"warehouse": row.fg_warehouse,
				"production_plan_sub_assembly_item": row.name,
				"bom": row.bom_no,
				"production_plan": self.name,
				"fg_item_qty": row.qty,
			}

			for field in [
				"schedule_date",
				"qty",
				"description",
				"production_plan_item",
			]:
				po_data[field] = row.get(field)

			po.append("items", po_data)

		#po.set_service_items_for_finished_goods()
		po.set_missing_values()
		po.flags.ignore_mandatory = True
		po.flags.ignore_validate = True
		po.insert()
		purchase_orders.append(po.name)




@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	doc = get_mapped_doc(
		"Pick List",
		source_name,
		{
			"Pick List": {
				"doctype": "Stock Entry",
				"field_map": {"stock_entry_type":"Material Transfer","pick_list":"name","rfse":"Stock Transfer"},
				"validation": {"docstatus": ["=", 1]},
			},
			"Pick List Item": {
				"doctype": "Stock Entry Detail",
				"field_map": {"item_code": "item_code", "picked_qty:": "qty","warehouse":"s_warehouse",
				"stock_uom":"stock_uom","stock_uom":"uom"},
			},
		},
		target_doc,
	)



	return doc
