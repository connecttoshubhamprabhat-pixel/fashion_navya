import frappe
from erpnext.stock.dashboard.item_dashboard import get_data

#re order by code
@frappe.whitelist(allow_guest=True)
def make_mr_reorder(doc,method):
    items_reorder=[]
    if doc.doctype=="Sales Invoice":
        for i in doc.items:
