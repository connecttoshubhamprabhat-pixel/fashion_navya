import frappe
import datetime
import json
from frappe import utils
from frappe import _, bold
from frappe.utils import date_diff
from frappe.model.mapper import get_mapped_doc
from erpnext.manufacturing.doctype.job_card.job_card import  JobCard

class OverlapError(frappe.ValidationError): pass

class OperationMismatchError(frappe.ValidationError): pass
class OperationSequenceError(frappe.ValidationError): pass
class JobCardCancelError(frappe.ValidationError): pass


class CustomJobCard(JobCard):
	def add_start_time_log(self, args):
		seq_flow = check_sequence(self.work_order, self.operation)
		if seq_flow:
			frappe.throw(f"Operation {seq_flow}: पहले complete करना होगा")
			
		self.append("time_logs", args)


def check_sequence(work_order, op):
	
	wo_doc = frappe.get_doc("Work Order", work_order)
	operations = [operation.operation for operation in wo_doc.operations]
	current_operation_index = operations.index(op)
	
	if current_operation_index != 0:
		
		previous_operation = operations[current_operation_index - 1]
		incomplete_job_cards = frappe.db.sql("""
            SELECT name 
            FROM `tabJob Card`
									    
            WHERE work_order = %s 
            AND operation = %s 
            AND status != 'Completed'
        """, (work_order, previous_operation), as_dict=True)
		
		if incomplete_job_cards:
			return previous_operation
			
	return None