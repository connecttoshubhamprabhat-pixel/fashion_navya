import frappe

@frappe.whitelist()
def remove_disabled(doc,method):
	if doc.mr_items:
		for i in doc.mr_items:
			item=frappe.get_doc("Item",i.item_code)
			if item.disabled==1:
				msg="Row {} item is disabled ,Please remove Disabled Item".format(i.idx)
				frappe.throw(msg)


@frappe.whitelist()
def wo_stop_pp(doc,method):
	if doc.production_plan:
		pp=frappe.get_doc("Production Plan",doc.production_plan)
		if pp.custom_wo_items==1:
			frappe.throw("Sorry You can't make Work order for W/o Items")
