# Copyright (c) 2022, Indictrans and contributors
# For license information, please see license.txt
import frappe
from frappe import _
from frappe.utils import today
from datetime import datetime # from python std library
from frappe.utils import add_to_date
from datetime import date
from erpnext.accounts.utils import get_fiscal_year
from datetime import date, timedelta
from frappe.utils import (flt, getdate, get_first_day, add_months,get_last_day, add_days, formatdate, cstr, cint)






def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	
	frappe.logger().debug(f"reportsss...... {data}")
	return columns, data






def get_conditions(filters):
	conditions = ""
	today =datetime.now().strftime('%Y-%m-%d')
	first_day_of_this_month = date.today().replace(day=1) 
	last_day_prev_month =str(first_day_of_this_month - timedelta(days=1))
		
	start_date=str(get_first_day(today))
	start_date_last=str(get_first_day(last_day_prev_month))
	plast =str(add_to_date(datetime.now(), days=-1, as_string=True))
	
	if filters.get("employee"):
		conditions += "  and employee = %(employee)s"
	
	if filters.get("item"):
		conditions += "  and item = %(item)s"
	
	
	if filters.get("range"):
		if filters.get("range")=="Last Day":
			conditions += " and start_date>='{}' ".format(plast)
			conditions += " and start_date<='{}' ".format(plast)

			
		if filters.get("range")=="Today":
			from_time=today
			conditions += " and start_date>='{}' ".format(today)
			conditions += " and start_date<='{}' ".format(today)
		
		if filters.get("range")=="Current Month":
			from_time=today
			conditions += " and start_date>='{}' ".format(start_date)
			conditions += " and start_date<='{}' ".format(today)
		
		if filters.get("range")=="Last Months":
			from_time=today
			conditions += " and start_date>='{}' ".format(start_date_last)
			conditions += " and start_date<='{}' ".format(last_day_prev_month)
		
		
		






	return conditions



def get_data(filters):
	data = []
	
	conditions = get_conditions(filters)
	records=frappe.db.sql(
		"""select item, name,employee,start_date,employee_name,
		total_hours
		from `tabTimesheet`
		where docstatus=1 %s order by start_date  """
		% conditions,
		filters,
		as_dict=1,
	)

	for i in records:
		d={}
		if not frappe.db.exists("Item",i.item):
			continue
		if  not filters.get("item_type"):
			d['item']=i.item
			d['hours']=i.total_hours
			d['employee']=i.employee
			d['employee_name']=i.employee_name
			d['ts']=i.name
			data.append(d)
			
		if  filters.get("item_type") and i.item:
			itemdoc=frappe.get_doc("Item",i.item)
			if itemdoc.has_variants==1 and filters.get("item_type")=="template":
				d['item']=i.item
				d['hours']=i.total_hours
				d['employee']=i.employee
				d['employee_name']=i.employee_name
				data.append(d)
			
			if itemdoc.has_variants==0 and itemdoc.variant_of and filters.get("item_type")=="variant":
				d['item']=i.item
				d['hours']=i.total_hours
				d['employee']=i.employee
				d['employee_name']=i.employee_name
				data.append(d)
			
			if itemdoc.has_variants==0 and not itemdoc.variant_of and filters.get("item_type")=="Enabled" :
				d['item']=i.item
				d['hours']=i.total_hours
				d['employee']=i.employee
				d['employee_name']=i.employee_name
				data.append(d)







	
	return data
def get_columns():
	return [
		{
			"label": _("Timesheet"),
			"fieldtype": "Link",
			"fieldname": "ts",
			"options": "Timesheet",
			"hidden":1,
			"width": 300,
		},
		{
			"label": _("Item"),
			"fieldtype": "Link",
			"fieldname": "item",
			"options": "Item",
			"width": 300,
		},
		{
			"label": _("Total Hours"),
			"fieldtype": "Float",
			"fieldname": "hours",
			"width": 150,
		},
		{
			"label": _("Employee ID"),
			"fieldtype": "Link",
			"fieldname": "employee",
			"options": "Employee",
			"width": 300,
		},
		{
			"label": _("Employee Name"),
			"fieldtype": "data",
			"fieldname": "employee_name",
			#"hidden": 1,
			"width": 200,
		},
		
			
	]




