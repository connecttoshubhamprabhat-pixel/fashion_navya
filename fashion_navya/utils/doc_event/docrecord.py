import frappe


@frappe.whitelist()
def fetch_po_items(name=None):
    if not name:
        return
        
    po=frappe.get_doc("Purchase Order",name)
    
