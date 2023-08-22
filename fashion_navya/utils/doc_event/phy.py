import frappe
from erpnext.stock.dashboard.item_dashboard import get_data

@frappe.whitelist()
def fetch_item_barcode(barcode=None):
	val=frappe.db.sql(""" select parent from `tabItem Barcode` where barcode='{}'  """.format(barcode),as_dict=1)
	if len(val)!=0:
		item=val[0]['parent']
		return item



@frappe.whitelist()
def  calculate_stock_phy(doc,method):
	if doc.items:
		for i in doc.items:
			stock=get_data(item_code=i.item_code,warehouse=doc.warehouse)
			bqty=0
			if len(stock)!=0:
				for j in  stock:
					if  j['actual_qty']>0:
						bqty+=j['actual_qty']
