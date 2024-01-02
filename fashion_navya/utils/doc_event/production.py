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
@frappe.whitelist()
def fetch_supplier(name=None):
	if not name:
		return

	doc=frappe.get_doc("Production Plan",name)
	if doc.sub_assembly_items:
		for i in doc.sub_assembly_items:
			split=i.parent_item_code.split("-")
			if "DP" in split:
				i.set("supplier","PRINTTECH")
			if "BP" in split:
				i.set("supplier","Samsudeen Aakil Khan")

			if "DP" not in split and "BP" not in split:
				i.set("supplier","Jiwan Singh and Sons")
	doc.save()



@frappe.whitelist()
def remove_without_bom(doc,method):
	if doc.po_items:
		for i in doc.po_items:
			if not i.bom_no:
				doc.get('po_items').remove(i)


@frappe.whitelist()
def production_plan_set_fg_warehouse(doc,method):
	if doc.po_items:
		for i in doc.po_items:
			i.set("warehouse","Navya Store Office - NAVYA")
