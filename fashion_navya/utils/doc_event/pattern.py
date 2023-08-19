import frappe
import re

@frappe.whitelist()
def create_version_ppt(name=None):
	if not name:
		return


@frappe.whitelist()
def fetch_silvit(doc,method):
	if doc.item_code:
		item=frappe.get_doc("Item",doc.item_code)
		if item.variant_of:
			e=re.findall(r'\d+',item.variant_of)
			m=[]
			for i in e:
				m.append(int(i))
			get_no=min(m)
			get_slit=frappe.db.sql("""select name from `tabSilhouette` where silhouette_no='{}'  """.format(str(get_no)),as_dict=1)
			if get_slit:
				doc.set("svitname",get_slit[0]['name'])
