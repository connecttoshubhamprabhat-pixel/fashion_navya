import frappe
from frappe import utils
import json
from erpnext.stock.dashboard.item_dashboard import get_data
from frappe.utils import cint, cstr, flt
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import *
from erpnext.accounts.utils import get_company_default
from erpnext.controllers.stock_controller import StockController
from erpnext.stock.doctype.batch.batch import get_batch_qty
from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.utils import get_stock_balance
from fashion_navya.utils.doc_event.oldstockb import (get_item_warehouse_map,get_items,get_stock_ledger_entries)

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
	items=[]
	for i in doc.items:
		if i.item_code not in items:
			diff=i.sqty-i.aqty
			item=i.item_code
			p=frappe.db.sql("""select price_list_rate,name from `tabItem Price` where item_code='{}' ORDER BY modified  """.format(item),as_dict=1)
			if len(p)!=0:
				i.set('price',p[0]['price_list_rate'])

			i.set('dqty',diff)
			a.append(i.aqty)
			s.append(i.sqty)
			items.append(i.item_code)



	diff_all=sum(s)- sum(a)
	doc.set('td',0)
	doc.set('total_qty',0)
	doc.set('total_qty',sum(s))
	doc.set('atotal',0)
	doc.set('td',diff_all)
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
	warehouse=None,item_group=None, posting_date=None, posting_time=None, company=None, item_code=None, ignore_empty_stock=False
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
		item_doc=frappe.get_doc("Item",d.item_code)
		if item_group:
			if item_doc.item_group!=item_group:
				continue
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



@frappe.whitelist()
def merge_entry(items=None):
	items=json.loads(items)
	if items:
		d={"doctype":"Physical Stock Count"}
		all_items=[]
		duplicate=[]
		for i in items:
			print(i,'qqqqqqqqqqqq')
			doc=frappe.get_doc("Physical Stock Count",i)
			for j in doc.items:
				print(j.item_code,'11111111')
				fdic={}
				if j.item_code not in duplicate:
					fdic['item_code']=j.item_code
					fdic['sqty']=j.sqty
					fdic['aqty']=j.aqty
					duplicate.append(j.item_code)
				if fdic:
					all_items.append(fdic)
		phy=frappe.get_doc(d)
		for k in all_items:
			row = doc.append("items", {})
			row.sqty=k['sqty']
			row.aqty=k['aqty']
		phy.insert()
		frappe.msgprint("created")




@frappe.whitelist()
def collab_items(doc,method):
	if doc.items and doc.warehouse:
		w=frappe.get_doc("Warehouse",doc.warehouse)
		items=[]
		dup=[]
		ilist=[]
		if w.is_group==1:
			for i  in doc.items:
				if i.item_code not in ilist:
					dc=i.as_dict()
					items.append(dc)
					ilist.append(i.item_code)

				else:
					dup.append('es')
					for k in items:
						if k['item_code']==i.item_code:
							k['aqty']+=i.aqty
		if dup:
			doc.items=[]
			for j in items:
				row = doc.append("items", {})
				row.item_code=j.item_code
				row.aqty=j.aqty






@frappe.whitelist()
def remove_other_wstock(doc,method):
	return
	if doc.warehouse and doc.items:
		wlist=[]
		wdoc=frappe.get_doc("Warehouse",doc.warehouse)
		if wdoc.is_group==1:
			get_w=frappe.db.sql("""select name from `tabWarehouse` where disabled=0 and parent_warehouse='{}'  """.format(doc.warehouse),as_dict=1)
			if get_w:
				for i in get_w:
					wlist.append(i['name'])

		else:
			wlist.append(doc.warehouse)


		wlist=list(set(wlist))
		items_list=[]
		for item in doc.items:
			for w in wlist:
				data=get_data(item_code=item.item_code,warehouse=w)
				if not data and item.item_code not in items_list:
					doc.get('items').remove(item.item_code)
			items_list.append(item.item_code)





@frappe.whitelist()
def fetch_items_from_stock_entry(stock_entry_name, physical_stock_review):
	stock_entry_doc = frappe.get_doc('Stock Entry', stock_entry_name)
	physical_stock_review_doc = frappe.get_doc('Physical Stock Count', physical_stock_review)

    # Clear existing items in physical stock review
	physical_stock_review_doc.set('items', [])

    # Loop through items in the stock entry and add them to the physical stock review
	for item in stock_entry_doc.items:
		physical_stock_review_doc.append('items', {
            'item_code': item.item_code,
            'item_name': item.item_name,
            'aqty': item.qty,
            # Add other necessary fields
			})

	physical_stock_review_doc.save()



@frappe.whitelist()
def consolidated_entry(items=None):
	items=json.loads(items)
	if items:
		d={"doctype":"Consolidated physical  Stock Count"}
		aqty=[0]
		sqty=[0]
		itemdoc=frappe.get_doc(d)
		for  i in items:
			doc=frappe.get_doc("Physical Stock Count",i)
			sqty.append(doc.total_qty)
			aqty.append(doc.atotal)
			print(doc.total_qty,"aaaaaaaaaaaaaaaaa")
			for j in doc.items:
				item=frappe.get_doc("Item",j.item_code)
				row = itemdoc.append("items", {})
				row.item_code=j.item_code
				row.item_name=j.item_name
				row.sqty=j.sqty
				row.aqty=j.aqty
				row.warehouse=j.warehouse
				row.dqty=j.dqty
				row.price=j.price
				row.image=j.image
				row.remarks=j.remarks


		diff=sum(sqty)-sum(aqty)
		d['dqty']=diff
		itemdoc.set("aqty",sum(aqty))
		itemdoc.set("sqty",sum(sqty))
		itemdoc.set("dqty",diff)
		itemdoc.insert(ignore_permissions=True)
		frappe.msgprint("Created")
