import frappe
from frappe import utils
from erpnext.accounts.utils import get_balance_on
from datetime import datetime # from python std library
from frappe.utils import add_to_date

@frappe.whitelist()
def today_cash_amount():
	#today="2023-09-05"
	#lday="2023-09-04"
	today = datetime.now().strftime('%Y-%m-%d')
	lday=add_to_date(datetime.now(), days=-1, as_string=True)
	get_accounts=frappe.db.sql("""select DISTINCT name  from `tabAccount` where custom_cash_account=1 """,as_dict=1)
	if get_accounts:
		for account in get_accounts:
			account_name=account['name']
			last_day_bl=get_balance_on(account=account_name,date=lday)
			todaybl=get_balance_on(account=account_name,date=today)
			final_bal=todaybl-last_day_bl
			custom_logs(sub="automated no bal")
			if int(final_bal)==0 or final_bal <0:
				continue

			d={"doctype":"Payment Entry","mode_of_payment":"Cash"}
			d['payment_transfer']="Cash to Bank"
			d['payment_type']="Internal Transfer"
			d['paid_to']="1102010204 - HDFC - NAVYA"
			d['paid_from']=account_name
			d['received_amount']=final_bal
			d['automated']=1
			d['reference_no']=today
			d['reference_date']=today
			d['paid_amount']=final_bal
			pe_new=frappe.get_doc(d)
			pe_new.insert()

			#pe_new.submit()
			subs="created,day entry:{},last day:-{},final_bal:{},lastbl:{},tdaybal:{}".format(today,lday,final_bal,last_day_bl,todaybl)
			custom_logs(sub=subs)
			frappe.db.commit()


@frappe.whitelist()
def custom_logs(doctype=None,name=None,sub=None):
	d={"doctype":"Custom Logs","info":sub}
	doc=frappe.get_doc(d)
	doc.insert()
	frappe.db.commit()
