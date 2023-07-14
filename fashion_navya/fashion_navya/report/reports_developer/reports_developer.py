# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe

from fashion_navya.utils.employee_summries import get_columns, get_data


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()

	data = get_data(filters)
	return columns, data

