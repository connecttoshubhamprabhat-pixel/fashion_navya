# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
	if filters.from_date >= filters.to_date:
		frappe.msgprint(_("To Date must be greater than From Date"))

	data = []
	columns = get_columns(filters)
	get_data(data, filters)
	return columns, data


def get_columns(filters):
	return [
        {
			"label": _("Purchase Order"),
			"fieldtype": "Link",
			"fieldname": "po",
			"options":"Purchase Order",
			"width": 150,
		},
        {
			"label": _("Work Order"),
			"fieldtype": "Link",
			"fieldname": "wo",
			"options":"Work Order",
			"width": 150,
		},
        {
			"label": _("W/o QTY"),
			"fieldtype": "Int",
			"fieldname": "wo_qty",
			"width": 150,
		},
		{
			"label": _("Subcontract Order"),
			"fieldtype": "Link",
			"fieldname": "subcontract_order",
			"options": filters.order_type,
			"width": 150,
		},
		{"label": _("Date"), "fieldtype": "Date", "fieldname": "date", "hidden": 1, "width": 150},
		{
			"label": _("Supplier"),
			"fieldtype": "Link",
			"fieldname": "supplier",
			"options": "Supplier",
			"width": 150,
		},
		{
			"label": _("Finished Good Item Code"),
			"fieldtype": "Data",
			"fieldname": "fg_item_code",
			"width": 100,
		},
		{"label": _("Item name"), "fieldtype": "Data", "fieldname": "item_name", "width": 100},
		{
			"label": _("Required Quantity"),
			"fieldtype": "Float",
			"fieldname": "required_qty",
			"width": 100,
		},
		{
			"label": _("Received Quantity"),
			"fieldtype": "Float",
			"fieldname": "received_qty",
			"width": 100,
		},
		{"label": _("Pending Quantity"), "fieldtype": "Float", "fieldname": "pending_qty", "width": 100},
	]


def get_data(data, filters):
	orders = get_subcontract_orders(filters)
	orders_name = [order.name for order in orders]
	subcontracted_items = get_subcontract_order_supplied_item(filters.order_type, orders_name)
	for item in subcontracted_items:
		for order in orders:
			if order.name == item.parent and item.received_qty < item.qty:
				row = {
					"subcontract_order": item.parent,
					"date": order.transaction_date,
					"supplier": order.supplier,
					"fg_item_code": item.item_code,
					"item_name": item.item_name,
					"required_qty": item.qty,
					"received_qty": item.received_qty,
					"pending_qty": item.qty - item.received_qty,
                    "po":item.po,
                    "wo":item.wo,
                    "wo_qty":item.wqty,
				}
				data.append(row)


def get_subcontract_orders(filters):
	record_filters = [
		["supplier", "=", filters.supplier],
		["transaction_date", "<=", filters.to_date],
		["transaction_date", ">=", filters.from_date],
		["docstatus", "=", 1],
	]

	if filters.order_type == "Purchase Order":
		record_filters.append(["is_old_subcontracting_flow", "=", 1])

	return frappe.get_all(
		filters.order_type, filters=record_filters, fields=["name", "transaction_date", "supplier"]
	)


def get_subcontract_order_supplied_item(order_type, orders):
    if order_type=="Purchase Order":
        return frappe.get_all(
    		f"{order_type} Item",
    		filters=[("parent", "IN", orders)],
    		fields=["parent", "item_code", "item_name", "qty", "received_qty"],
    	)
    if order_type=="Subcontracting Order":
        data=frappe.get_all(
    		f"{order_type} Item",
    		filters=[("parent", "IN", orders)],
    		fields=["parent", "item_code", "item_name", "qty", "received_qty"],
    	)
        #print(data,'data')
        for i in data:
            print(i)
            sodoc=frappe.get_doc("Subcontracting Order",i['parent'])
            i['po']=sodoc.purchase_order
            get_po=frappe.db.sql("""select work_order from `tabPurchase Order Item` where docstatus=1 and parent='{}' """.format(sodoc.purchase_order),as_dict=1)
            if get_po:
                if frappe.db.exists("Work Order",get_po[0]['work_order']):
                    wodoc=frappe.get_doc("Work Order",get_po[0]['work_order'])
                    i['wo']=wodoc.name
                    i['wqty']=wodoc.qty
        return data
