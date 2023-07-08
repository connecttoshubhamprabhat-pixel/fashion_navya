import frappe


@frappe.whitelist()
def fetch_po_items(docname=None,po=None):
    if not po:
        return
    
    #doc=frappe.get_doc("Document Record",docname)
    po=frappe.get_doc("Purchase Order",po)
    items=[]
    count=0
    for i in po.items:
        d={}
        d['item_code']=i.item_code
        d['item_name']=i.item_name
        d['fg_item']=i.fg_item
        d['fg_name']=i.fg_name
        d['qty']=i.fg_item_qty
        items.append(d)
        
    return items





@frappe.whitelist()
def fetch_po_items_doc(doc,method):
    if doc.purchase_order:
        po=frappe.get_doc("Purchase Order",doc.purchase_order)
        items=[]
        count=0
        for i in po.items:
            row = doc.append("po_files", {})
            row.item_code=i.fg_item
            row.item_name=i.fg_name
            row.po_qty=i.fg_item_qty
            
        







