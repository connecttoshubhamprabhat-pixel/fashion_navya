import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_hours
from frappe import utils



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
	#calculate for pos
	total_pos=[0]
	posc=frappe.db.sql("""select name,grand_total from `tabPOS Closing Entry` where docstatus=1 and  posting_date between '{}' and '{}'  """.format(from_date,to_date),as_dict=1)
	if len(posc)!=0:
		for p in posc:
			total_pos.append(p['grand_total'])
			# pos_amt=0
			# pos_doc=frappe.get_doc("POS Closing Entry",p['name'])
			# if pos_doc.pos_transactions:
			# 	for a in pos_doc.pos_transactions:
	pdic={"pos":sum(total_pos)}
	data.append(pdic)



	get_pe=frappe.db.sql("""select * from `tabPayment Entry` where payment_type="Receive" and  docstatus=1 and posting_date between '{}' and '{}'  """.format(from_date,to_date),as_dict=1)
	if len(get_pe)!=0:
		for i in get_pe:
			d={}
			doc_pe=frappe.get_doc("Payment Entry",i['name'])
			ref=doc_pe.references
			d['ped']=doc_pe.posting_date
			d['pe']=doc_pe.name
			d['mop']=doc_pe.mode_of_payment
			d['tid']=doc_pe.reference_no
			d['td']=doc_pe.reference_date
			d['customer']=doc_pe.party
			d['mop']=doc_pe.mode_of_payment
			if not ref:
				d['uamt']=doc_pe.paid_amount
			if ref:
				if ref[0].reference_doctype=="Sales Order":
					so=frappe.get_doc("Sales Order",ref[0].reference_name)
					d['sales_order']=so.name
					d['samt']=so.grand_total
					d['sonet']=so.net_total
					d['pamt']=doc_pe.paid_amount
				if ref[0].reference_doctype=="Sales Invoice":
					si=frappe.get_doc("Sales Invoice",ref[0].reference_name)
					d['si']=si.name
					d['siamt']=si.grand_total
					d['sinet']=si.net_total
					d['pamt']=doc_pe.paid_amount




			# si=frappe.get_doc("Sales Invoice",ref[0].reference_name)
			# d['si']=ref[0].reference_name
			# d['customer']=si.customer
			# d['mop']=doc_pe.mode_of_payment
			# d['amt']=doc_pe.paid_amount
			# d['ped']=doc_pe.posting_date
			# d['samt']=si.grand_total
			# d['tid']=doc_pe.reference_no
			# d['td']=doc_pe.reference_date
			data.append(d)













	return data




def get_columns():
	return [
		{
			"label": _("Payment Date"),
			"fieldtype": "Data",
			"fieldname": "ped",
			"width":110,
		},
		{
			"label": _("Payment Entry"),
			"fieldtype": "Link",
			"fieldname": "pe",
			"options":"Payment Entry",
			"width":150,
		},
		{
			"label": _("Sales Order"),
			"fieldtype": "Link",
			"fieldname": "sales_order",
			"options": "Sales Order",
			"width":160,
		},
		{
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"fieldname": "si",
			"options": "Sales Invoice",
			"width":170,
		},

		{
			"label": _("Sales Order/Gross amount"),
			"fieldtype": "Float",
			"fieldname": "samt",
			"width":200,
		},

		{
                        "label": _("Sales Order/Net amount"),
                        "fieldtype": "Float",
                        "fieldname": "sonet",
                        "width":200,
                },


		{
			"label": _("Sales Invoice/ Gross amount"),
			"fieldtype": "Float",
			"fieldname": "siamt",
			"width":200,
		},
		{
                        "label": _("Sales Invoice/Net amount"),
                        "fieldtype": "Float",
                        "fieldname": "sinet",
                        "width":200,
                },


		{
			"label": _("Unallocated Amount"),
			"fieldtype": "Float",
			"fieldname": "uamt",
			"width":200,
		},

		{
                        "label": _("Advance payment"),
                        "fieldtype": "Float",
                        "fieldname": "pamt",
                        "width":200,
                },

		{
			"label": _("Customer"),
			"fieldtype": "Link",
			"fieldname": "customer",
			"options":"Customer",
			"width":100,
		},
		{
			"label": _("Mode of Payment"),
			"fieldtype": "Data",
			"fieldname": "mop",
			"width":100,
		},
		{
			"label": _("Mode of Payment"),
			"fieldtype": "Data",
			"fieldname": "mop",
			"width":100,
		},
		{
			"label": _("POS Amount"),
			"fieldtype": "Data",
			"fieldname": "pos",
			"width":100,
		},

		{
			"label": _("Transaction/ID"),
			"fieldtype": "Data",
			"fieldname": "tid",
			"width":150,
		},
		{
			"label": _("Transaction/Date"),
			"fieldtype": "Data",
			"fieldname": "td",
			"width":150,
		},

		]
