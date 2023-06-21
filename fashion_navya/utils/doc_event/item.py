import frappe
from erpnext.stock.dashboard.item_dashboard import get_data


@frappe.whitelist(allow_guest=True)
def custom_title_fields(doc,method):
    if doc.item_code:
        #frappe.throw("custom_title_fields")
        docitem=frappe.get_doc("Item",doc.item_code)
        item=docitem.name
        net_stock=[0]
        get_stock=get_data(item_code=item)
        for jk in get_stock:
            if not jk['actual_qty']<0:
                net_stock.append(int(jk['actual_qty']))

        docitem.set("net_stock_value",0)

        docitem.db_set("net_stock_value",sum(net_stock), update_modified=False)
		#-------end-------------
        size=frappe.db.sql("""select attribute_value from `tabItem Variant Attribute` where attribute="Size" and parent='{}'  """.format(docitem.name),as_dict=1)
        if not size:
            data="Stock:{},Size:{}".format(sum(net_stock),'None')
            docitem.set('custom_title',data)
            docitem.save(ignore_permissions=True)
            return

        if size:
            size=size[0]['attribute_value']
            data="Stock:{},Size:{}".format(sum(net_stock) or 0,size)
            docitem.db_set("custom_title",data, update_modified=False)
            docitem.db_set("product_size",size, update_modified=False)
            docitem.save(ignore_permissions=True)
            return
