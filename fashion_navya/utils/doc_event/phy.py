import frappe
from erpnext.stock.dashboard.item_dashboard import get_data

@frappe.whitelist()
def fetch_item_barcode(barcode=None):
	val=frappe.db.sql(""" select parent from `tabItem Barcode` where barcode='{}'  """.format(barcode),as_dict=1)
	if len(val)!=0:
		item=val[0]['parent']
		return item



@frappe.whitelist()
def calculate_stock_phy(doc,method):
	#yfrappe.msgprint("hello testing")
	a=[0]
	s=[0]
	if doc.items:
		for i in doc.items:
			s.append(i.sqty)
			stock=get_data(item_code=i.item_code,warehouse=doc.warehouse)
			if len(stock)!=0:
				a.append(stock[0]['actual_qty'] or 0)
				d=i.sqty-stock[0]['actual_qty']
				i.set('dqty',0)
				i.set('aqty',0)
				i.set('aqty',stock[0]['actual_qty'])
				i.set('dqty',d)

			else:
				d=i.sqty-0
				i.set('dqty',0)
				i.set('aqty',0)
				i.set('dqty',d)


	doc.set('total_qty',0)
	doc.set('total_qty',sum(s))
	doc.set('atotal',0)
	doc.set('atotal',sum(a))
