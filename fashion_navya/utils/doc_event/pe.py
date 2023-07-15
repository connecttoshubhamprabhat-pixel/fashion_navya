import frappe


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
