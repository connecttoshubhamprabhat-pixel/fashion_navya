import frappe

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
		bom.db_set("workflow_state","Changes Pending", update_modified=False)
		#bom.db_set("docstatus",1, update_modified=False)
		frappe.db.commit()



