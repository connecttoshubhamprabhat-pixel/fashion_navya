# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters=None):
	if filters.from_date >= filters.to_date:
		frappe.msgprint(_("To Date must be greater than From Date"))

	columns = get_columns(filters)
	data=get_data(filters) or []
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
			"label": _("wo/status"),
			"fieldtype": "Data",
			"fieldname": "wos",
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
			"label": _("MT/SE/Date"),
			"fieldtype": "Data",
			"fieldname": "mtdate",
			"width": 100,
		},
		{
			"label": _("MT/SE/status"),
			"fieldtype": "Data",
			"fieldname": "mtstatus",
			"width": 100,
		},

		{
			"label": _("MT/SE"),
			"fieldtype": "Link",
			"fieldname": "mtse",
			"options":"Stock Entry",
			"width":200,
		},

        {
			"label": _("sub/SE/Date"),
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
			"label": _("sub/SE/status"),
			"fieldtype": "Data",
			"fieldname": "sestatus",
			"width":100,
		},

		{
			"label": _("PO/date"),
			"fieldtype": "Data",
			"fieldname": "podate",
			"width":100,
		},





        {
			"label": _("Purchase Order/sub"),
			"fieldtype": "Link",
			"fieldname": "po",
			"options":"Purchase Order",
			"width":150,
		},

        		{
			"label": _("Subcontract Order"),
			"fieldtype": "Link",
			"fieldname": "subcontract_order",
			"options":"Subcontracting Order",
			"width":150,
		},

		{
	"label": _("Subcontracting Receipt"),
	"fieldtype": "Link",
	"fieldname": "sr",
	"options":"Subcontracting Receipt",
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
		{
            "label": _("Wo/Item"),
            "fieldtype": "Link",
            "fieldname": "woitem",
            "options":"Item",
            "width":200,
        },
		{"label": _("Item name"), "fieldtype": "Data", "fieldname": "item_name", "width":200},
        {
			"label": _("W/oQTY"),
			"fieldtype": "Float",
			"fieldname": "wo_qty",
			"width":100,
		},
		{
			"label": _("W/oQTY/pending"),
			"fieldtype": "Float",
			"fieldname": "wo_qty_p",
			"width":100,
		},
		{
			"label": _("Net/Stock"),
			"fieldtype": "Float",
			"fieldname": "net_qty",
			"width":100,
		},
		{
			"label": _("Sold Stock"),
			"fieldtype": "Float",
			"fieldname": "sold",
			"width":100,
		},
		{
			"label": _("W/produced/qty"),
			"fieldtype": "Float",
			"fieldname": "wopqty",
			"width":120,
		},
		{
			"label": _("PO/FG QTY"),
			"fieldtype": "Float",
			"fieldname": "pofg",
			"width":100,
		},
        {
			"label": _("Required/qty"),
			"fieldtype": "Float",
			"fieldname": "required_qty",
			"width": 80,
		},
		{
			"label": _("Received/qty"),
			"fieldtype": "Float",
			"fieldname": "received_qty",
			"width":100,
		},
		{"label": _("Pending Quantity"), "fieldtype": "Float", "fieldname": "pending_qty", "width": 100},
	]


def get_data(filters):
	data=[]
	record_filters = [
		["planned_start_date", "<=", filters.to_date],
		["planned_start_date", ">=", filters.from_date],
		["docstatus", "=", 1],
		["qty",">","produced_qty"],
		["status","=",filters.status]]

	if filters.project:
		record_filters.append(["project","=",filters.project])


	get_alls=frappe.get_all(
        "Work Order", filters=record_filters, fields=["production_item","status","produced_qty","name","planned_start_date","qty"]
    )
	if get_alls:
		si_item_dup=[]
		net_item_duplicate=[]
		for i in get_alls:
			row={}
			itemdoc=frappe.get_doc("Item",i['production_item'])
			if filters.item_group:
				if filters.item_group!=itemdoc.item_group:
					continue
			sup=filters.supplier
			if sup:
				get_po=frappe.db.sql("""select * from `tabPurchase Order Item` where docstatus=1 and work_order='{}' and parent in (select name from `tabPurchase Order` where docstatus=1 and supplier='{}' )  """.format(i['name'],sup),as_dict=1)
				
			else:
				get_po=frappe.db.sql("""select * from `tabPurchase Order Item` where docstatus=1 and work_order='{}'   """.format(i['name']),as_dict=1)

			if get_po:
				for p in get_po:
					po_doc=frappe.get_doc("Purchase Order",p['parent'])
					get_so=frappe.db.sql("""select name from `tabSubcontracting Order` where docstatus=1 and purchase_order='{}' """.format(po_doc.name),as_dict=1)
					get_sr=frappe.db.sql("""select name from `tabSubcontracting Receipt` where docstatus=1 and purchase_order='{}' """.format(po_doc.name),as_dict=1)
					if get_sr:
						row['sr']=get_sr[0]['name']
					if get_so:
						for s in get_so:
							sub_doc=frappe.get_doc("Subcontracting Order",s['name'])
							row['subcontract_order']=s['name']
							for s_item in sub_doc.items:
								if s_item.item_code==p['fg_item']:
									row['required_qty']=s_item.qty
									row['received_qty']=s_item.received_qty
									row['pending_qty']=s_item.qty-s_item.received_qty
							get_se=frappe.db.sql("""select name from `tabStock Entry` where docstatus<2 and subcontracting_order='{}' """.format(sub_doc.name),as_dict=1)
							if get_se:
								for se in get_se:
									se_doc=frappe.get_doc("Stock Entry",se['name'])
									row['se']=se_doc.name
									row['sedate']=se_doc.posting_date
									row['sestatus']=se_doc.workflow_state

					if po_doc.is_subcontracted:
						row['po']=po_doc.name
						row['supplier']=po_doc.supplier
						row['fg_item_code']=p['fg_item']
						row['pofg']=p['fg_item_qty']
						row['item_name']=p['item_name']
						row['podate']=po_doc.transaction_date

			row['wo']=i['name']
			row['wodate']=i['planned_start_date']
			row['wopqty']=i['produced_qty']
			row['wo_qty']=i['qty']
			row['wos']=i['status']
			row['woitem']=i['production_item']
			penwo=i['qty']-i['produced_qty']
			row['wo_qty_p']=penwo
			sold_qty=[0]
			si_item_dup=[]
			net_item_duplicate=[]
			si_sold=frappe.db.sql(""" select sum(qty) as qty from `tabSales Invoice Item`  where  docstatus=1 and item_code='{}'  and parent in (select name from `tabSales Invoice` where docstatus=1 and is_consolidated=1 ) """.format(i['production_item']),as_dict=1)
			dn_sold=frappe.db.sql(""" select sum(qty) as qty from `tabDelivery Note Item`  where  docstatus=1 and item_code='{}'  and parent in (select name from `tabDelivery Note` where docstatus=1) """.format(i['production_item']),as_dict=1)
			if i['production_item'] not in si_item_dup:
				if si_sold:
					if si_sold[0]['qty']!=None:
						sold_qty.append(si_sold[0]['qty'])
						si_item_dup.append(i['production_item'])


						
				if dn_sold:
					if dn_sold[0]['qty']!=None:
						sold_qty.append(dn_sold[0]['qty'])
						si_item_dup.append(i['production_item'])
						
				row['sold']=sum(sold_qty)


			
			get_qty=frappe.db.sql("""select sum(actual_qty) as qty  from `tabBin` where actual_qty>0 and item_code='{}'   """.format(i['production_item']),as_dict=1)
			if get_qty and i['production_item'] not in net_item_duplicate:
				if get_qty[0]['qty']!=None:
					row['net_qty']=get_qty[0]['qty']
					net_item_duplicate.append(i['production_item'])





			get_set_mt=frappe.db.sql("""select * from `tabStock Entry` where docstatus<2 and stock_entry_type='Material Transfer for Manufacture' and work_order='{}' """.format(i['name']),as_dict=1)
			if get_set_mt:
				row['mtstatus']=get_set_mt[0]['workflow_state']
				row['mtdate']=get_set_mt[0]['posting_date']
				row['mtse']=get_set_mt[0]['name']
			data.append(row)


	return data
