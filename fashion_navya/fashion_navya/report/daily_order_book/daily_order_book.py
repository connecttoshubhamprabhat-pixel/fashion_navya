import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_hours
from frappe import utils
from fashion_navya.utils.doc_event.stock_bal import *
from datetime import datetime, timedelta,date



def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_data(filters):
	data=[]
	if not filters.from_date and not filters.to_date:
		return []
		
	from_date=str(filters.from_date)
	to_date=str(filters.to_date)
	if not filters.shop:
		shops=['Pune - NAVYA','Santushti - NAVYA']
		for s in shops:
			totals=[0]
			d={}
			stock_balance = get_group_warehouse_stock_balance(s)
			if len(stock_balance)!=0:
				for qty in stock_balance:
					if qty.qty>0:
						totals.append(qty.qty)

			total_sum=sum(totals)
			d['shop']=s
			d['stock']=total_sum
			received=get_stock_entry_qty_today(s)
			print(received,'received')
			d['rstock']=received
			d['dstock']=get_out_qty(s)
			data.append(d)

		
	return data




def get_columns():
	return [
		
		
		{
			"label": _("Ordered"),
			"fieldtype": "Data",
			"fieldname": "ordered",
			"width":150,
		},
		{
			"label": _("Pos Invoice"),
			"fieldtype": "Float",
			"fieldname":"pos",
			"width":150,
		},
		
	]




