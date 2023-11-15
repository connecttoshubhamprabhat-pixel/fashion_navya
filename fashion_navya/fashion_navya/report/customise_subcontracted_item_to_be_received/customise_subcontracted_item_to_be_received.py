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
			"label": _("wo/Date"),
			"fieldtype": "Data",
			"fieldname": "wodate",
			"width": 100,
		},

        {
			"label": _("Work Order"),
			"fieldtype": "Link",
			"fieldname": "wo",
			"options":"Work Order",
			"width":200,
		},
        {
			"label": _("SE/Date"),
			"fieldtype": "Data",
			"fieldname": "sedate",
			"width": 100,
		},

        {
			"label": _("SUB/Stock Entry"),
			"fieldtype": "Link",
			"fieldname": "se",
			"options":"Stock Entry",
			"width":100,
		},
        {
			"label": _("SE/status"),
			"fieldtype": "Data",
			"fieldname": "sestatus",
			"width":100,
		},





        {
			"label": _("Purchase Order"),
			"fieldtype": "Link",
			"fieldname": "po",
			"options":"Purchase Order",
			"width":150,
		},

        		{
			"label": _("Subcontract Order"),
			"fieldtype": "Link",
			"fieldname": "subcontract_order",
			"options": filters.order_type,
			"width":150,
		},
		{"label": _("Date"), "fieldtype": "Date", "fieldname": "date", "hidden": 1, "width": 150},
		{
			"label": _("Supplier"),
			"fieldtype": "Link",
			"fieldname": "supplier",
			"options": "Supplier",
			"width": 100,
		},
		{
			"label": _("Finished Good Item Code"),
			"fieldtype": "Data",
			"fieldname": "fg_item_code",
			"width": 100,
		},
		{"label": _("Item name"), "fieldtype": "Data", "fieldname": "item_name", "width":200},
        {
			"label": _("W/o QTY"),
			"fieldtype": "Int",
			"fieldname": "wo_qty",
			"width":40,
		},
        {
			"label": _("Required Quantity"),
			"fieldtype": "Float",
			"fieldname": "required_qty",
			"width": 80,
		},
		{
			"label": _("Received Quantity"),
			"fieldtype": "Float",
			"fieldname": "received_qty",
			"width": 80,
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
                    "se":item.se,
                    "sedate":item.sedate,
                    "sestatus":item.sestatus,
                    "wodate":item.wodate
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
            #get_scr=frappe.db.sql("""sel  """)
            i['po']=sodoc.purchase_order
            get_se=frappe.db.sql("""select * from `tabStock Entry` where docstatus<2 and subcontracting_order='{}' """.format(i['parent']),as_dict=1)
            if get_se:
                i['se']=get_se[0]['name']
                i['sedate']=get_se[0]['posting_date']
                i['sestatus']=get_se[0]['workflow_state']

            get_po=frappe.db.sql("""select * from `tabPurchase Order Item` where docstatus<2 and parent='{}' """.format(sodoc.purchase_order),as_dict=1)
            if get_po:
                if frappe.db.exists("Work Order",get_po[0]['work_order']):
                    wodoc=frappe.get_doc("Work Order",get_po[0]['work_order'])
                    i['wo']=wodoc.name
                    i['wqty']=wodoc.qty
                    i['wodate']=wodoc.planned_start_date
        return data
