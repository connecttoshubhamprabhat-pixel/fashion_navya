import frappe
import json
from datetime import datetime, timedelta




@frappe.whitelist()
def get_last_day_stock_balance_for_group_warehouse(group_warehouse):
	# Get yesterday's date
	today = datetime.today()
	yesterday = today - timedelta(days=1)
	last_day = yesterday.strftime('%Y-%m-%d')

	# Get all child warehouses of the group warehouse
	child_warehouses = get_child_warehouses(group_warehouse)


	# Initialize a dictionary to hold the stock balances
	stock_balances=[0]
	total_stock_balance=0


	# Fetch the stock balance for each child warehouse
	for warehouse in child_warehouses:
		print(warehouse,'warehouse')
		stock_balance = frappe.db.sql("""
            	SELECT sum(qty_after_transaction) as qty
            FROM `tabStock Ledger Entry`
            WHERE 
                warehouse = %s AND 
                posting_date = %s AND 
                is_cancelled = 0
            ORDER BY posting_date DESC, posting_time DESC, creation DESC
            LIMIT 1
        """, (warehouse, last_day), as_dict=True)


		if stock_balance and stock_balance[0].qty is not None:
			print(stock_balance,'stock_balance')
			total_stock_balance += stock_balance[0].qty


	return total_stock_balance






@frappe.whitelist()
def get_shop_wise_balance():
	# Replace 'Group Warehouse - Company' with your actual group warehouse name
	shops=['Pune - NAVYA','Santushti - NAVYA']
	for s in shops:
		totals=[0]
		stock_balance = get_group_warehouse_stock_balance(s)
		if stock_balance:
			for qty in stock_balance:
				if qty.qty>0:
					totals.append(qty.qty)

		total_sum=sum(totals)
		print(s,total_sum)




def get_group_warehouse_stock_balance(group_warehouse):
	# Get all child warehouses of the group warehouse
	child_warehouses = get_child_warehouses(group_warehouse)
	if not child_warehouses:
		return []



	# Get stock balance for all child warehouses
	stock_balance = frappe.db.sql("""
        	SELECT SUM(actual_qty) as qty
        	FROM `tabBin`
        		WHERE actual_qty>0 and  warehouse IN (%s)    GROUP BY warehouse  """ % ','.join(['%s'] * len(child_warehouses)), tuple(child_warehouses), as_dict=True)

	return stock_balance



def get_child_warehouses(parent_warehouse):
	# Function to get all child warehouses for a given parent warehouse
	warehouses = [parent_warehouse]
	child_warehouses = frappe.db.get_all('Warehouse', filters={'parent_warehouse': parent_warehouse}, fields=['name'])
	for warehouse in child_warehouses:
		warehouses.extend(get_child_warehouses(warehouse.name))

	return warehouses
