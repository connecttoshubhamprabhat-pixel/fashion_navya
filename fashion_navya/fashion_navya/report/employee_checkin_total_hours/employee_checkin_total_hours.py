import frappe
from frappe import _
from frappe.utils import flt, time_diff_in_hours
from frappe import utils
from datetime import datetime, timedelta



def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data




def get_data(filters):

	data = []
	if not filters.from_date or not filters.to_date:
		return []


	from_date = str(filters.from_date)
	to_date = str(filters.to_date)
	branch=filters.branch


	checkins = frappe.get_all("Employee Checkin",
                              filters={"log_type": ("IN", "Out"),
                                       "time": [">=", from_date],
                                       "time": ["<=", to_date],
                                         "custom_branch":["=",branch]},
                              fields=["employee", "log_type", "time"],
                              order_by="employee, time")



	print(checkins,'checkins')
	# Initialize variables to store employee-wise hours
	current_employee = None
	hours_worked = timedelta()
	# Calculate hours worked for each employee

	for checkin in checkins:
		employee = checkin.employee
		log_type = checkin.log_type
		log_time = str(checkin.time)

		if current_employee != employee:
			if current_employee:
				data.append({
                    			"employee": current_employee,
                    			"hours_worked": hours_worked.total_seconds() / 3600})
			current_employee = employee
			hours_worked = timedelta()


		if log_type == "IN":
			checkin_time = log_time
		elif log_type == "Out":
			hours_worked += log_time - checkin_time



	# Add data for the last employee
	if current_employee:
		data.append({
            "employee": current_employee,
            "hours_worked": hours_worked.total_seconds() / 3600
        })

	return data




def get_columns():
	return [
		{
			"label": _("Employee"),
			"fieldtype": "Link",
			"fieldname": "employee",
			"options":"Employee",
			"width":150,
		},
		{
			"label": _("Hours"),
			"fieldtype": "Float",
			"fieldname": "hours_worked",
			"width":110,
		},
		
]
