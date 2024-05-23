import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_hours
from frappe import utils
from fashion_navya.utils.doc_event.stock_bal import *
from datetime import date
from frappe.utils import flt



def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_data(filters):
	data=[]
	date_lists=[]
	
	if filters.from_date and filters.to_date and filters.day_type=='No Time':
		date_lists.append(str(filters.from_date))
		date_lists.append(str(filters.to_date))
		
	if filters.day_type:
		date_final=get_day_date(filters.day_type)
		date_lists.append(date_final)
		date_lists.append(date_final)
		print(date_final,'date_final')
	else:
		return []



		
	from_date=str(date_lists[0])
	to_date=str(date_lists[1])
	if not filters.shop:
		shops=['Pune - NAVYA','Santushti - NAVYA']
		
		for s in shops:
			#group_warehouse=['Pune - NAVYA','Santushti - NAVYA']
			child_warehouses = get_child_warehouses(s)
			entries = get_stock_ledger_entries(from_date, to_date, child_warehouses)
			balance = calculate_balance(entries)
			bal=final_balance(balance)
			
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
			received=get_stock_entry_qty_today(s,from_date,to_date)
			print(received,'received')
			d['rstock']=received
			d['dstock']=get_out_qty(s)
			d['rnstock']=get_today_sales_return_qty()
			d['mstock']=get_stock_entry_qty_today_return(s,from_date,to_date)
			data.append(d)

		
	return data




def get_columns():
	return [
		
		
		{
			"label": _("Shop"),
			"fieldtype": "Data",
			"fieldname": "shop",
			"width":150,
		},
		{
			"label": _("Total Stock"),
			"fieldtype": "Float",
			"fieldname":"stock",
			"width":150,
		},
		{
			"label": _("Today Received"),
			"fieldtype": "Float",
			"fieldname":"rstock",
			"width":150,
		},
		{
			"label": _("Today Deliver"),
			"fieldtype": "Float",
			"fieldname":"dstock",
			"width":150,
		},
		{
			"label": _("Today Customer Return"),
			"fieldtype": "Float",
			"fieldname":"rnstock",
			"width":150,
		},
		{
			"label": _("Today Manual Return"),
			"fieldtype": "Float",
			"fieldname":"mstock",
			"width":150,
		},
	]




def get_stock_entry_qty_today(group_warehouse,from_date,to_date):
	child_warehouses = get_child_warehouses(group_warehouse)
	qty_list=[0]
	if child_warehouses:
		for i in child_warehouses:
			qty=get_se_balance(i,from_date,to_date)
			if qty>0:
				qty_list.append(qty)
			
	return sum(qty_list)
	
def get_se_balance(w,from_date,to_date):
	sql_query = """
        SELECT 
            se.name, 
            SUM(sed.qty) AS balance,
            DATE(se.modified) AS date
        FROM 
            `tabStock Entry` se   ,`tabStock Entry Detail` sed
        
		WHERE 
            
			sed.t_warehouse ='{}'
			and se.name = sed.parent
            AND se.docstatus = 1
            AND se.stock_entry_type IN ('Material Transfer', 'Material Receipt', 'Manufacture','Repack')
            AND DATE(se.modified) between '{}' and '{}'
        GROUP BY 
            se.name
    """.format("".join(w),from_date,to_date)
	get_se = frappe.db.sql(sql_query, as_dict=True)
	if get_se:
		print(get_se,"seqqq")
	if len(get_se)!=0:
		all_qty=[0]
		for k in get_se:
			if k.balance:
				all_qty.append(k.balance)
		
		print(all_qty,'all_qty')
		return sum(all_qty)
	else:
		return 0




def get_out_qty(w):
	qtys = [0]
	shops_dict = {'Santushti - NAVYA': "Santushti", 'Pune - NAVYA': "Pune"}
	si_dict = {'Santushti - NAVYA': "Santushti Ready To Wear", 'Pune - NAVYA': "Pune Ready To Wear"}
	
	# Get today's delivery notes
	get_dn = frappe.db.sql("""
        SELECT name 
        FROM `tabDelivery Note` 
        WHERE docstatus = 1 AND DATE(modified) = CURDATE()
    """, as_dict=True)
	
	if get_dn:
		for dn in get_dn:
			so_list=[]
			dndoc = frappe.get_doc("Delivery Note", dn['name'])
			for q in dndoc.items:
				if q.against_sales_order:
					so_list.append(q.against_sales_order)
					break


			if so_list and shops_dict.get(w):
				get_so = frappe.db.sql("""
                    SELECT name 
                    FROM `tabSales Order` 
                    WHERE docstatus = 1 AND name = %s AND custom_shop_location = %s
                """, (so_list[-1], shops_dict.get(w)), as_dict=True)
				
				if get_so:
					qtys.append(dndoc.total_qty)
    
    # Get today's sales invoices
	get_si = frappe.db.sql("""
        SELECT name 
        FROM `tabSales Invoice` 
        WHERE is_consolidated = 1 AND docstatus = 1 AND DATE(modified) = CURDATE()
    """, as_dict=True)
	
	if get_si:
		for si in get_si:
			sidoc = frappe.get_doc("Sales Invoice", si['name'])
			if si_dict.get(w) and sidoc.pos_profile == si_dict.get(w):
				qtys.append(sidoc.total_qty)  # Assuming you want to sum Sales Invoice quantities as well
				
	return sum(qtys)



def get_stock_ledger_entries(from_date, to_date, child_warehouses):
	warehouse_placeholders = ', '.join(['%s'] * len(child_warehouses))
	query = f"""
        SELECT
            item_code,
            warehouse,
            posting_date,
            SUM(qty_after_transaction) as qty_after_transaction
        FROM
            `tabStock Ledger Entry`
        WHERE
            posting_date BETWEEN %s AND %s AND
			is_cancelled = 0 and
            warehouse IN ({warehouse_placeholders})
        ORDER BY
            posting_date DESC, posting_time DESC, creation DESC
		
    """
	
	values = [from_date, to_date] + child_warehouses
	entries = frappe.db.sql(query, values, as_dict=True)
	
	return entries

def calculate_balance(entries):
	balance = {}
	
	for entry in entries:
		warehouse = entry.warehouse
		item_code = entry.item_code
		qty = flt(entry.qty_after_transaction)
		
		if warehouse not in balance:
			balance[warehouse] = {}
			
		if item_code not in balance[warehouse]:
			balance[warehouse][item_code] = 0
			
		balance[warehouse][item_code] += qty
		
	return balance






def get_child_warehouses(parent_warehouse):
	# Function to get all child warehouses for a given parent warehouse
	warehouses = [parent_warehouse]
	child_warehouses = frappe.db.get_all('Warehouse', filters={'parent_warehouse': parent_warehouse}, fields=['name'])
	for warehouse in child_warehouses:
		warehouses.extend(get_child_warehouses(warehouse.name))
		
	return warehouses


def final_balance(balance):
	total_qty=[0]
	for warehouse, items in balance.items():
		for item_code,qty in items.items():
			if qty>0:
				total_qty.append(qty)
				
	return total_qty


def get_day_date(date_type):
	today = datetime.today()
	yesterday = today - timedelta(days=1)
	last_day = yesterday.strftime('%Y-%m-%d')
	
	if date_type=="Today":
		return str(today)
	if date_type=="Yesterday":
		return str(last_day)
	
	return str(today)



import frappe
from frappe.utils import nowdate

def get_today_sales_return_qty():
	today = str(datetime.today())
	print(today,"qqqqqqqqqqqqqqqqqqqqqqqqq2")
	
	query = """
        SELECT
            SUM(total_qty) as total_return_qty
        FROM
            `tabSales Invoice`
        WHERE
            posting_date = %s AND
            is_return = 1 AND
            docstatus = 1
    """
	
	values = [today]
	result = frappe.db.sql(query, values, as_dict=True)
	total_return_qty = result[0].total_return_qty if result and result[0].total_return_qty else 0
	return total_return_qty


def get_stock_entry_qty_today_return(group_warehouse,from_date,to_date):
	child_warehouses = get_child_warehouses(group_warehouse)
	qty_list=[0]
	if child_warehouses:
		for i in child_warehouses:
			qty=get_se_balance_return(i,from_date,to_date)
			if qty>0:
				qty_list.append(qty)
			
	return sum(qty_list)


def get_se_balance_return(w,from_date,to_date):
	sql_query = """
        SELECT 
            se.name, 
            SUM(sed.qty) AS balance,
            DATE(se.modified) AS date
        FROM 
            `tabStock Entry` se   ,`tabStock Entry Detail` sed
        
		WHERE 
            
			sed.s_warehouse ='{}'
			and se.name = sed.parent
            AND se.docstatus = 1
            AND se.stock_entry_type IN ('Material Transfer', 'Material Receipt', 'Manufacture','Repack')
            AND DATE(se.modified) between '{}' and '{}'
        GROUP BY 
            se.name
    """.format("".join(w),from_date,to_date)
	get_se = frappe.db.sql(sql_query, as_dict=True)
	if get_se:
		print(get_se,"seqqq")
	if len(get_se)!=0:
		all_qty=[0]
		for k in get_se:
			if k.balance:
				all_qty.append(k.balance)
		
		print(all_qty,'all_qty')
		return sum(all_qty)
	else:
		return 0
