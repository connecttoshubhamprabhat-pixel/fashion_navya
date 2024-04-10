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
	record_filters = [
		["transaction_date", "<=", filters.to_date],
		["transaction_date", ">=", filters.from_date],
		['material_request_type',"=","Manufacture"],
		['docstatus',"=",1],
	]
	if filters.project:
		project_filter=["project", "=", filters.project]
		record_filters.append(project_filter)

	get_mr= frappe.get_all(
		"Material Request", filters=record_filters, fields=["name", "project", "custom_is_so","custom_customer"]
	)
	if get_mr:
		for mr in get_mr:
			mr_doc=frappe.get_doc("Material Request",mr.name)
			count_name=0
			for item in mr_doc.items:
				d={}
				if count_name==0:
					d['mr']=mr.name

				count_name+=1
				item_name=item.item_code
				itemdoc=frappe.get_doc("Item",item_name)
				d['item_name']=itemdoc.item_name
				d['item']=item_name
				if mr.custom_is_so:
					d['is_so']="Yes"
					get_mr_ts=frappe.db.sql("""select parent from `tabMaterial Request Item` where docstatus=1 and sales_order='{}' and parent in (select name from `tabMaterial Request`  where docstatus=1 and material_request_type='Material Transfer')  """.format(item.sales_order),as_dict=1)
					if len(get_mr_ts)!=0:
						mr_tsered=get_mr_ts[0]['parent']
						get_se=frappe.db.sql("""select parent from `tabStock Entry Detail` where material_request='{}' and docstatus=1 and item_code='{}' """.format(mr_tsered,item_name),as_dict=1)
						if len(get_se)!=0:
							sedoc=frappe.get_doc("Stock Entry",get_se[0]['parent'])
							if sedoc.add_to_transit==1:
								get_se_out=frappe.db.sql("""select name from `tabStock Entry` where docstatus=1 and outgoing_stock_entry='{}'  """.format(sedoc.name),as_dict=1)
								if len(get_se_out)!=0:
									d['mr_ts']="Transferred"
								else:
									d['mr_ts']="No"
							else:
								d['mr_ts']="Transferred"
						else:
							d['mr_ts']="No"
					else:
						d['mr_ts']="No MR made"
				else:
					d['is_so']="No"
				if mr.custom_is_so:
					d['customer']=mr.custom_customer
				#mr_doc=frappe.get_doc("Material Request",mr.name)
				get_wo=frappe.db.sql("""select name,status from `tabWork Order` where material_request='{}' and docstatus=1 and production_item='{}'  """.format(mr.name,item_name),as_dict=1)
				if len(get_wo)!=0:
					d['is_wo']="Yes"
					d['wo_status']=get_wo[0]['status']
					get_po=frappe.db.sql("""select parent,item_code,fg_item from `tabPurchase Order Item` where docstatus=1 and work_order='{}'  """.format(get_wo[0]['name']),as_dict=1)
					if len(get_po)!=0:
						d['is_po']="Yes"
					else:
						d['is_po']="No"
				else:
					d['is_wo']="No"
				data.append(d)


	return data




def get_columns():
	return [
		{
			"label": _("MR name"),
			"fieldtype": "Link",
			"fieldname": "mr",
			"options":"Material Request",
			"width":190,
		},

		{
			"label": _("Item"),
			"fieldtype": "Link",
			"fieldname": "item",
			"options":"Item",
			"width":200,
		},
		{
			"label": _("Item Name"),
			"fieldtype": "Data",
			"fieldname": "item_name",
			"width":190,
		},
		{
			"label": _("Is Sales Order"),
			"fieldtype": "Data",
			"fieldname": "is_so",
			"width":110,
		},
		{
			"label": _("is W/o"),
			"fieldtype": "Data",
			"fieldname": "is_wo",
			"width":100,
		},
		{
			"label": _("W/o Status"),
			"fieldtype": "Data",
			"fieldname": "wo_status",
			"width":150,
		},
		{
			"label": _("is/po"),
			"fieldtype": "Data",
			"fieldname": "is_po",
			"width":160,
		},
		{
			"label": _("Customer"),
			"fieldtype":"Link",
			"fieldname":"customer",
			"options":"Customer",
			"width":150,
		},
		{
			"label": _("MR/Transferred"),
			"fieldtype": "Data",
			"fieldname": "mr_ts",
			"width":230,
		},


]
