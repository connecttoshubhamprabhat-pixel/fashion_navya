import frappe
from frappe import utils
from datetime import date, timedelta
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_existing_salary_slips


#schdule salary Slip
@frappe.whitelist()
def salary_slip_automate():
    today=str(utils.today())
    split_date=today.split("-")[-1]
    if split_date!="13":
        return

    get_emp=frappe.db.sql("""select DISTINCT employee from `tabTimesheet`  where YEAR(start_date) = YEAR(CURDATE() - INTERVAL 1 MONTH) and  docstatus=1 and month(start_date)=month(now())-1 ORDER BY start_date """,as_dict=1)
    employee_list=[]
    if get_emp:
        for e in get_emp:
            employee_list.append(e['employee'])

    employees=list(set(employee_list))
    print(employees,'oooooo')
    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
    start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
    print("First day of prev month:", start_day_of_prev_month)
    print("Last day of prev month:", last_day_of_prev_month)
    if employees:
        args = frappe._dict(
				{
					"salary_slip_based_on_timesheet":1,
					"payroll_frequency":"Monthly",
					"start_date":start_day_of_prev_month,
					"end_date":last_day_of_prev_month,
					"company":frappe.defaults.get_user_default("company"),
					"posting_date":str(utils.today()),

				}
			)
        if len(employees) > 30:
            self.db_set("status", "Queued")
            frappe.enqueue(
					create_slip_automate,
					timeout=600,
					employees=employees,
					args=args,
					publish_progress=False,
				)
            frappe.msgprint(
					_("Salary Slip creation is queued. It may take a few minutes"),
					alert=True,
					indicator="blue",
				)
        else:
            create_slip_automate(employees, args, publish_progress=False)





@frappe.whitelist()
def create_slip_automate(employees, args, publish_progress=True):
    try:

        count = 0

        for emp in employees:
            check_sl=frappe.db.sql("""select name from `tabSalary Slip` where docstatus <2 and start_date='{}' """.format(args.start_day_of_prev_month),as_dict=1)
            if len(check_sl)==0:
                args.update({"doctype": "Salary Slip", "employee": emp})
                frappe.get_doc(args).insert()
                count += 1





    except Exception as e:
        continue

    finally:
        frappe.db.commit()
