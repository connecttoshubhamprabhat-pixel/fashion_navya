import frappe


@frappe.whitelist()
def make_tag(warehouse=None):
	if warehouse:
		pass
