import frappe
from frappe.utils import getdate
from frappe import utils

#jul 12/2023
@frappe.whitelist()
def create_pe_for_internal(doc,method):
	if doc.payment_type=="Receive" and doc.mode_of_payment=="Cash":
		d={"doctype":"Payment Entry","mode_of_payment":"Cash"}
		d['payment_transfer']="Cash to Bank"
		d['payment_type']="Internal Transfer"
		d['paid_to']="1102010203 - STATE BANK OF INDIA - NAVYA"
		d['paid_from']=doc.paid_to
		d['received_amount']=doc.paid_amount
		d['reference_no']=doc.name
		d['automated']=1
		d['customer_pe']=doc.name
		d['paid_amount']=doc.paid_amount
		pe_new=frappe.get_doc(d)
		pe_new.insert()


@frappe.whitelist()
def cancel_pe_cash(doc,method):
    if not  doc.customer_pe:
        pe_old=frappe.db.sql("""select name from `tabPayment Entry` where docstatus <2 and customer_pe='{}'  """.format(doc.name),as_dict=1)
        if len(pe_old)!=0:
            customer_pe=pe_old[0]['name']
            docpe=frappe.get_doc("Payment Entry",customer_pe)
            if docpe.docstatus==0:
                docpe.delete()
                frappe.db.commit()

            if docpe.docstatus==1:
                docpe.cancel()
                frappe.db.commit()




@frappe.whitelist()
def check_duplicate_entry(doc,method):
	if doc.customer_pe:
		pe_old=frappe.db.sql("""select name from `tabPayment Entry` where docstatus <2 and customer_pe='{}' and name!='{}'  """.format(doc.customer_pe,doc.name),as_dict=1)
		if len(pe_old)!=0:
			msg="Sorry The Cash entry is being duplicated,for {}".format(doc.customer_pe)
			frappe.throw(msg)



#-------------link estimate sheet to sales order---------
@frappe.whitelist()
def update_reference_in_payment_entry(name=None):
    #d, payment_entry
    do_not_save=False
    skip_ref_details_update_for_pe=False

    if not name:
        return

    so=frappe.get_doc("Sales Order",name)
    payment_amt=[0]
    pe_name=[]
    if so.estimate_sheet:
        get_name_pe=frappe.db.sql("""select name,paid_amount from `tabPayment Entry` where docstatus=1 and estimate_sheet='{}'  """.format(so.estimate_sheet),as_dict=1)
        if len(get_name_pe)!=0:
            for pe in get_name_pe:
                pe_name.append(pe['name'])
                payment_amt.append(pe['paid_amount'])
    else:
        get_estimate=frappe.db.sql(""" select name from `tabEstimate Sheet` where docstatus <2 and sales_order='{}' """.format(so.name),as_dict=1)
        if len(get_estimate)!=0:
            get_name_pe=frappe.db.sql("""select name,paid_amount from `tabPayment Entry` where docstatus=1 and estimate_sheet='{}'  """.format(get_estimate[0]['name']),as_dict=1)
            if len(get_name_pe)!=0:
                for pe in get_name_pe:
                    pe_name.append(pe['name'])
                    payment_amt.append(pe['paid_amount'])


    if pe_name:
        for p in pe_name:
            payment_entry=frappe.get_doc("Payment Entry",p)
            d={'voucher_type':'Payment Entry','account':'1101010000 - Debtors - NAVYA'}
            d['party_type']='Customer'
            d['voucher_no']=p
            d['party']=so.customer
            d['against_voucher_type']="Sales Order"
            d['against_voucher']=so.name
            d['is_advance']="Yes"
            d['precision']=2
            d['exchange_rate']=1
            d['difference_account']='4408000000 - Exchange Gain/Loss - NAVYA'
            d['exchange_gain_loss']=0.0
            d['grand_total']=so.grand_total
            #d['outstanding_amount']=so.outstanding_amount
            d['dr_or_cr']='credit_in_account_currency'
            d['unadjusted_amount']=payment_entry.paid_amount
            d['allocated_amount']=payment_entry.paid_amount
            d['unreconciled_amount']=payment_entry.paid_amount


            reference_details = {
        		"reference_doctype":"Sales Order",
        		"reference_name":so.name,
        		"total_amount": so.grand_total,
        		"outstanding_amount":0.0,
        		"allocated_amount":payment_entry.paid_amount,
        		"exchange_rate":1
        		if not d.get('exchange_gain_loss')
        		else payment_entry.get_exchange_rate(),
        		"exchange_gain_loss": d.get('exchange_gain_loss'),  # only populated from invoice in case of advance allocation
        	}

            if d.get('voucher_detail_no'):
                existing_row = payment_entry.get("references", {"name": d["voucher_detail_no"]})[0]
                original_row = existing_row.as_dict().copy()
                existing_row.update(reference_details)


                if d.get('allocated_amount') < original_row.allocated_amount:
                    new_row = payment_entry.append("references")
                    new_row.docstatus = 1
                    for field in list(reference_details):
                        new_row.set(field, original_row[field])

                    new_row.allocated_amount = original_row.allocated_amount - d.allocated_amount

            else:
                new_row = payment_entry.append("references")
                new_row.docstatus = 1
                new_row.update(reference_details)


            payment_entry.flags.ignore_validate_update_after_submit = True
            payment_entry.setup_party_account_field()
            payment_entry.set_missing_values()
            payment_entry.set_amounts()


            if d.get('difference_amount') and d.get('difference_account'):
                account_details = {
        			"account": d.get('difference_account'),
        			"cost_center": payment_entry.cost_center
        			or frappe.get_cached_value("Company", payment_entry.company, "cost_center"),
        		}

                if d.get('difference_amount'):
                    account_details["amount"] = d.get('difference_amount')

                payment_entry.set_gain_or_loss(account_details=account_details)


            payment_entry.flags.ignore_validate_update_after_submit = True
            payment_entry.setup_party_account_field()
            payment_entry.set_missing_values()
            if not skip_ref_details_update_for_pe:
                payment_entry.set_missing_ref_details()

            payment_entry.set_amounts()

            if not do_not_save:
                payment_entry.save(ignore_permissions=True)
                #update_advance_paid(payment_entry.name)
                frappe.db.commit()




def update_advance_paid(name=None):
    if not name:
        pe=frappe.get_doc("Payment Entry",name)
        if pe.payment_type in ("Receive", "Pay") and pe.party:
            for d in pe.get("references"):
                if d.allocated_amount and d.reference_doctype in frappe.get_hooks("advance_payment_doctypes"):
                    frappe.get_doc(
                    d.reference_doctype, d.reference_name, for_update=True
                    ).set_total_advance_paid()
            frappe.db.commit()


#------------------end------------------------

@frappe.whitelist()
def set_account_by_user(doc,method):
    user=frappe.session.user
    if doc.mode_of_payment in  ['Cash']  and user in ['sosowon@navyacustom.com','neha@navyacustom.com']:
        if doc.payment_type=="Receive" and doc.party_type=="Customer":
            if doc.paid_to!="1102020500 - Cash - Santushti - NAVYA":
                doc.set("paid_to","1102020500 - Cash - Santushti - NAVYA")





#jul 12/2023
@frappe.whitelist()
def create_pe_for_internal_si(doc,method):
	p=frappe.db.sql(""" select name from `tabPOS Invoice` where docstatus <2 and consolidated_invoice='{}'  """.format(doc.name),as_dict=1)
	if len(p)!=0:
		pdoc=frappe.db.sql("""select parent from `tabSales Invoice Payment` where mode_of_payment="Cash POS" and docstatus=1 and parent='{}' and amount>0  """.format(p[0]['name']),as_dict=1)
		if doc.is_consolidated==1 and doc.is_pos==1 and len(pdoc)!=0:
			d={"doctype":"Payment Entry","mode_of_payment":"Cash"}
			d['payment_transfer']="Cash to Bank"
			d['payment_type']="Internal Transfer"
			d['paid_to']="1102010203 - STATE BANK OF INDIA - NAVYA"
			d['paid_from']='1102020500 - Cash - Santushti - NAVYA'
			d['received_amount']=doc.grand_total
			d['reference_no']=doc.name
			d['automated']=1
			d['pos_si']=doc.name
			d['paid_amount']=doc.grand_total
			pe_new=frappe.get_doc(d)
			pe_new.insert()


@frappe.whitelist()
def cancel_pe_si(doc,method):
	pe=frappe.db.sql("""select name from `tabPayment Entry` where pos_si='{}' and docstatus <2  """.format(doc.name),as_dict=1)
	if len(pe)!=0:
		pedoc=frappe.get_doc("Payment Entry",pe[0]['name'])
		if pedoc.docstatus==0:
			pedoc.delete()
			frappe.db.commit()
		if pedoc.docstatus==1:
			pedoc.cancel()
			frappe.db.commit()






@frappe.whitelist()
def make_payment(customer=None,amount=None,mode_of_payment=None,ref=None,name=None):
	if not customer:
		frappe.msgprint("Please Select customer first")
		return

	default_account=frappe.db.sql("""select default_account  from `tabMode of Payment Account` where parent='{}'  """.format(mode_of_payment),as_dict=1)
	if len(default_account)==0:
		frappe.msgprint("Default aAccount is not set")
		frappe.msgprint("Not Created")
		return


	d={'doctype':'Payment Entry',"payment_type":"Receive","party_type":"Customer"}
	d['party']=customer
	d['mode_of_payment']=mode_of_payment
	d['paid_amount']=amount
	d['received_amount']=amount
	d['source_exchange_rate']=1
	d['target_exchange_rate']=1
	d['pes']="Sales"
	d["reference_date"]=str(getdate())
	d['reference_no']=ref
	d['so']=name
	if len(default_account)!=0:
		d['paid_to']=default_account[0]['default_account']

	pe=frappe.get_doc(d)
	pe.insert()
	pe.reload()
	docso=frappe.get_doc("Sales Order",name)
	docso.db_set("advancepe",1, update_modified=False)
	docso.reload()
	#pe.submit()
	frappe.msgprint("Payment Entry Created")



@frappe.whitelist()
def submit_pe_entry(name=None):
	if not name:
		return

	frappe.msgprint("aaw")
	get_pe=frappe.db.sql("""select name from `tabPayment Entry` where docstatus=0 and so='{}'  """.format(name),as_dict=1)
	if len(get_pe)!=0:
		frappe.msgprint("aa")
		pe=frappe.get_doc("Payment Entry",get_pe[0]['name'])
		row = pe.append("references", {})
		row.reference_doctype="Sales Order"
		row.reference_name=name
		row.allocated_amount=pe.paid_amount
		pe.submit()
		frappe.db.commit()
		frappe.msgprint("Entry Submitted")



@frappe.whitelist()
def check_pe(name=None):
	if not name:
		return

	get_pe=frappe.db.sql("""select name,paid_amount from `tabPayment Entry` where docstatus <2 and so='{}'  """.format(name),as_dict=1)
	if len(get_pe)!=0:
		amt=int(get_pe[0]['paid_amount'])
		p=40/100*amt
		if p>amt:
			#advance fully not paid
			return 1
		else:
			#advance fully paid
			return 2
	else:
		return 1



@frappe.whitelist()
def not_submit_so(doc,method):
	pe=frappe.db.sql("""select name from `tabPayment Entry` where docstatus < 2 and so='{}'  """.format(doc.name),as_dict=1)
	if len(pe)==0:
		frappe.throw("Sorry Without Payment you can't proceed")
