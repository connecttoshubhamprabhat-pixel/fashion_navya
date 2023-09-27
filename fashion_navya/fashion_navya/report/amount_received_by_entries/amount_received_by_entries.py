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
	get_pe=frappe.db.sql("""select * from `tabPayment Entry` where docstatus=1 and posting_date between '{}' and '{}' and unallocated_amount>0 """.format(from_date,to_date),as_dict=1)
	if len(get_pe)!=0:
		for i in get_pe:
			d={}
			doc_pe=frappe.get_doc("Payment Entry",i['name'])
			d['mop']=doc_pe.mode_of_payment
			d['amt']=doc_pe.paid_amount
			d['ped']=doc_pe.posting_date
			d['tid']=doc_pe.reference_no
			d['td']=doc_pe.reference_date
			d['pe']=doc_pe.name

			data.append(d)













	return data




def get_columns():
	return [
		{
			"label": _("Payment Entry"),
			"fieldtype": "Link",
			"fieldname": "pe",
			"options":"Payment Entry",
			"width":150,
		},
		{
			"label": _("Payment Date"),
			"fieldtype": "Data",
			"fieldname": "ped",
			"width":110,
		},
		{
			"label": _("Mode of Payment"),
			"fieldtype": "Data",
			"fieldname": "mop",
			"width":100,
		},
		{
			"label": _("Payment Amount"),
			"fieldtype": "Float",
			"fieldname": "amt",
			"width":160,
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
