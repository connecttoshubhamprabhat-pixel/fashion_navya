import frappe
import json
from navya.api_folder.py.project import make_custom_variants_so

@frappe.whitelist()
def check_estimate_paid(doc,method):
	if doc.estimate_sheet:
		est=frappe.get_doc("Estimate Sheet",doc.estimate_sheet)
		if int(est.base_net_total)==0:
			frappe.throw("payment is still not received after Estimate Sheet")


@frappe.whitelist()
def make_custom_item(item_list=None,customer=None):
	if not customer or not item_list:
		return
	custom=[]
	items=json.loads(item_list)
	#frappe.throw("Inprogress")
	if items:
		for i in items:
			item=make_custom_variants_so(items=i,customer=customer)
			custom.append(item)

	if custom:
		frappe.msgprint("Item created")
		return custom
	else:
		return []
