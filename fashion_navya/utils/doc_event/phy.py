import frappe
from frappe import utils
from erpnext.stock.dashboard.item_dashboard import get_data
from frappe.utils import cint, cstr, flt
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import *
from erpnext.accounts.utils import get_company_default
from erpnext.controllers.stock_controller import StockController
from erpnext.stock.doctype.batch.batch import get_batch_qty
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.utils import get_stock_balance
from erpnext.stock.report.stock_balance.stock_balance import (get_item_details,get_item_warehouse_map,get_items,get_stock_ledger_entries)

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



@frappe.whitelist()
def get_items(date=None,warehouse=None):
	if not date or  not warehouse:
		return
	filter_sb={}
	filter_sb['from_date']=date
	filter_sb['to_date']=date
	filter_sb['company']="NAVYA"
	filter_sb['warehouse']=warehouse
	items = get_items(filter_sb)
	sle = get_stock_ledger_entries(filter_sb, items)
	if not sle:
		return []

	iwb_map = get_item_warehouse_map(filter_sb, sle)
	#item_map = get_item_details(items, sle, filters)
	item_list=[]
	for group_by_key in iwb_map:
		item = group_by_key[1]
		warehouse = group_by_key[2]
		val=iwb_map[group_by_key]
		bal=val['bal_val']
		if bal>0:
			if item not in item_list:
				item_list.append(item)

	item_lists=list(set(item_list))
	if item_lists:
		return item_lists
	else:
		return []




@frappe.whitelist()
def get_items_core(
	warehouse=None, posting_date=None, posting_time=None, company=None, item_code=None, ignore_empty_stock=False
):

	posting_date=str(utils.today())
	ps=str(utils.now())
	psit=ps.split(" ")
	psinx=psit[-1][:5]
	posting_time=psinx
	company="NAVYA"

	ignore_empty_stock =1
	items = [frappe._dict({"item_code": item_code, "warehouse": warehouse})]

	if not item_code:
		items = get_items_for_stock_reco(warehouse, company)

	res = []
	itemwise_batch_data = get_itemwise_batch(warehouse, posting_date, company, item_code)

	for d in items:
		if d.item_code in itemwise_batch_data:
			valuation_rate = get_stock_balance(
				d.item_code, d.warehouse, posting_date, posting_time, with_valuation_rate=True
			)[1]

			for row in itemwise_batch_data.get(d.item_code):
				if ignore_empty_stock and not row.qty:
					continue

				args = get_item_data(row, row.qty, valuation_rate)
				res.append(args)
		else:
			stock_bal = get_stock_balance(
				d.item_code,
				d.warehouse,
				posting_date,
				posting_time,
				with_valuation_rate=True,
				with_serial_no=cint(d.has_serial_no),
			)
			qty, valuation_rate, serial_no = (
				stock_bal[0],
				stock_bal[1],
				stock_bal[2] if cint(d.has_serial_no) else "",
			)

			if ignore_empty_stock and not stock_bal[0]:
				continue

			args = get_item_data(d, qty, valuation_rate, serial_no)

			res.append(args)

	return res
