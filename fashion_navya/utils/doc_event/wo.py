import frappe
import json

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
	if doc.sales_order:
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
				doc.set("size",i.size)



#w/o items fetch status not started
@frappe.whitelist(allow_guest=True)
def wo_items_fetch_ns():
	items=[]
	get_items=frappe.db.sql("""select qty,bom_no,production_item from `tabWork Order` where docstatus=1 and status="Not Started"   """,as_dict=1)
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
