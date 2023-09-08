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
	a=[0]
	s=[0]
	dt=[0]
	if doc.items:
		for i in doc.items:
			s.append(i.sqty)
			w=frappe.get_doc("Warehouse",doc.warehouse)
			if w.is_group==0:
				stock=get_data(item_code=i.item_code,warehouse=doc.warehouse)
				if len(stock)!=0:
					a.append(stock[0]['actual_qty'] or 0)
					d=i.sqty-stock[0]['actual_qty']
					i.set('dqty',0)
					i.set('aqty',0)
					i.set('aqty',stock[0]['actual_qty'])
					i.set('dqty',d)
					d=abs(d)
					dt.append(d)
				else:
					d=i.sqty-0
					i.set('dqty',0)
					i.set('aqty',0)
					i.set('dqty',d)
					dt.append(d)

			if w.is_group==1:
				get_all_warehouse=frappe.db.sql("""select name from `tabWarehouse` where disabled=0 and parent_warehouse='{}'   """.format(doc.warehouse),as_dict=1)
				amt=0
				for n in get_all_warehouse:
					stocks=get_data(item_code=i.item_code,warehouse=n['name'])
					if len(stocks)!=0:
						for k in  stocks:
							if k['actual_qty']>0:
								amt+=k['actual_qty']

				d=i.sqty-amt
				i.set('dqty',0)
				i.set('aqty',0)
				i.set('aqty',amt)
				i.set('dqty',d)
				a.append(amt)
				d=abs(d)
				dt.append(d)
	
	doc.set('total_qty',0)
	doc.set('total_qty',sum(s))
	doc.set('atotal',0)
	doc.set('td',sum(dt))
	doc.set('atotal',sum(a))
