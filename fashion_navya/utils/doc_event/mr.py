import frappe
import json

@frappe.whitelist()
def make_mr_project(name=None):
	if not name:
		return


	get_alls=frappe.db.sql("""select DISTINCT  name from `tabItem` where variant_of is not null and  project='{}'  """.format(name),as_dict=1)
	if get_alls:
		d={"doctype":"Material Request","material_request_type":"Manufacture","project":name}
		mr=frappe.get_doc(d)
		for i in get_alls:
			row = mr.append("items", {})
			row.item_code=i['name']
			row.description=i['name']
			row.uom="Nos"
			row.qty=1

		mr.insert()
		frappe.msgprint("MR Created")





@frappe.whitelist()
def make_mr_select(items=None,name=None):
	items=json.loads(items)
	if not name:
		return

	if items:
		d={"doctype":"Material Request","material_request_type":"Manufacture","project":name}
		mr=frappe.get_doc(d)
		for i in  items:
			row = mr.append("items", {})
			row.item_code=i
			row.description=i
			row.uom="Nos"
			row.qty=1

		mr.insert()
		frappe.msgprint("MR Created")
