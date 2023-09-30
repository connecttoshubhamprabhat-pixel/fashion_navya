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
