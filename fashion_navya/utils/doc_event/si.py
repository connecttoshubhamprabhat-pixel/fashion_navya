import frappe
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def make_new_si_id(doc,method):
    split_date=str(doc.posting_date).split("-")
    cyr=split_date[0]
    next_year=str(int(cyr[2:])+1)
    fyear=cyr+"-"+next_year
    prefix="SINV"
    used_no=[]
    get_max=frappe.db.sql("""select max(nos) as no from `tabInvoice No series`  """,as_dict=1)
    if get_max:
        used_no.append(get_max[0]['no'])

    if not doc.custom_invoice_no:
        no_f=[]
        cint=int(used_no[-1])+1
        if len(str(cint))==3:
            fno="00{}".format(cint)
            no_f.append(fno)
        if len(str(cint))==4:
            fno="0{}".format(cint)
            no_f.append(fno)

        if len(str(cint))>4:
            no_f.append(str(fno))

        if not no_f:
            no_f.append("000001")

        final=prefix+"-"+fyear+"-"+no_f[0]
        used_no.append(no_f[0])
        get_si=frappe.db.sql("""select name from `tabSales Invoice` where custom_invoice_no='{}' """.format(final),as_dict=1)
        if len(get_si)!=0:
            frappe.throw("Invoice Series Error")

        print(doc.name,"name")
        print(doc.posting_date)
        doc.set("custom_invoice_no",final)
        get_s=frappe.db.sql("""select name from `tabInvoice No series` where series_no='{}'  """.format(final),as_dict=1)
        if not get_s:
            make_record_in(no=fno,status=doc.docstatus,name=doc.name,commit=0)
            #frappe.db.commit()






@frappe.whitelist(allow_guest=True)
def make_new_si_id_old(year=0,months=0):
    prefix="SINV"
    fyear="2023-24"
    used_no=["00497"]
    get_all_in=frappe.db.sql("""select * from `tabSales Invoice`  where  custom_invoice_no is null and docstatus>0 and year(posting_date)='{}' and month(posting_date) ='{}'   ORDER BY posting_date """.format(year,months),as_dict=1)
    if get_all_in:
        for i in get_all_in:
            si_doc=frappe.get_doc("Sales Invoice",i['name'])
            #print(si_doc.name)
            if not si_doc.custom_invoice_no:
                get_no=[]
                cint=int(used_no[-1])+1
                if len(str(cint))==3:
                    fno="00{}".format(cint)
                if len(str(cint))==4:
                    fno="0{}".format(cint)
                final=prefix+"-"+fyear+"-"+fno
                used_no.append(fno)
                get_si=frappe.db.sql("""select name from `tabSales Invoice` where custom_invoice_no='{}' """.format(final),as_dict=1)
                if len(get_si)!=0:
                    frappe.throw("error")

                print(si_doc.name,"name")
                print(si_doc.posting_date)
                frappe.db.sql(""" update `tabSales Invoice` set custom_invoice_no='{}' where name='{}'   """.format(final,si_doc.name))
                #frappe.db.commit()

                get_s=frappe.db.sql("""select name from `tabInvoice No series` where series_no='{}'  """.format(final),as_dict=1)
                if not get_s:
                    make_record_in(no=fno,status=si_doc.docstatus,name=si_doc.name,commit=1)
                    frappe.db.commit()

                print(final)


@frappe.whitelist(allow_guest=True)
def make_record_in(no=None,status=0,name=None,commit=0):
    final="SINV-2023-24-{}".format(no)
    d={"doctype":"Invoice No series","series_no":final}
    d['prefix']="SINV"
    d['fiscal_year']="2023-24"
    d['nos']=str(no)
    d['si_no']=name
    d['booked']=1
    if status==0:
        d['series_status']="Draft"
    if status==1:
        d['series_status']="Submitted"
    if status==2:
        d['series_status']="cancelled"


    doc=frappe.get_doc(d)
    doc.insert(ignore_permissions=True)
    if commit==1:
        frappe.db.commit()



#status update
@frappe.whitelist(allow_guest=True)
def cancel_doc_si_series(doc,method):
    if doc.custom_invoice_no:
        get_name=frappe.db.sql("""select name from `tabInvoice No series` where series_no='{}' and si_no='{}'  """.format(doc.custom_invoice_no,doc.name),as_dict=1)
        if get_name:
            frappe.db.sql("""update `tabInvoice No series` set series_status="cancelled"  where series_no='{}' and si_no='{}' """.format(doc.custom_invoice_no,doc.name))
            frappe.db.commit()


@frappe.whitelist(allow_guest=True)
def set_si_custom_series(doc,method):
    prefix_list=[]
    if doc.is_pos==1:
        if doc.pos_profile in ['Pune Ready To Wear']:
            prefix_list.append("PI/")

        else:
            prefix_list.append("SI/")

    else:
        so=[]
        for i in doc.items:
            if i.sales_order:
                so.append(i.sales_order)
                break
        if so:
            sodoc=frappe.get_doc("Sales Order",so[-1])
            if sodoc.custom_shop_location=="Pune":
                prefix_list.append("PI/")
            else:
                prefix_list.append("SI/")
        else:
            prefix_list.append("SI/")


    if not prefix_list:
        frappe.throw("Naming series issues ,contact to Technical team")
        #return
    #get fiscal year
    get_fiscal_yr=str(get_current_financial_year())
    # Define the naming series
    #series_name = "SI/24-25/"
    prefix=prefix_list[-1]
    pre_name=get_fiscal_yr.split("-")
    pre_1=str(pre_name[0][2:])+"-"+str(pre_name[1])+"/"
    series_name=prefix+pre_1
    print(series_name,"series_name111")
    counter_no=['0001q']
    #get max counter
    print(get_fiscal_yr,'get_fiscal_yr')
    get_max_counter=frappe.db.sql("""select MAX(custom_sicounter) as nos from `tabSales Invoice` where custom_sifiscal='{}' and custom_prefix='{}'  """.format(get_fiscal_yr,prefix),as_dict=1)
    if len(get_max_counter)!=0:
        if get_max_counter[0]['nos']!=None:
            counter_int=int(get_max_counter[0]['nos'])
            # Increment current value
            next_value= int(counter_int) + 1
            print(next_value,'next_value')
            # Pad with leading zeros
            next_value_padded = str(next_value).zfill(4)
            counter_no.append(next_value_padded)
        else:
            counter_no.append("0001")
    else:
        counter_no.append("0001")

    #series name final
    name_series=series_name+counter_no[-1]
    doc.name=name_series
    print(name_series,"name_series")
    doc.set("custom_sifiscal",get_fiscal_yr)
    doc.set("custom_sicounter",counter_no[-1])
    doc.set("custom_prefix",prefix)


# Function to get the current financial year
@frappe.whitelist(allow_guest=True)
def get_current_financial_year():
    today = datetime.now()
    if today.month < 4:
        return f"{today.year - 1}-{today.year % 100:02d}"
    else:
        return f"{today.year}-{(today.year + 1) % 100:02d}"
