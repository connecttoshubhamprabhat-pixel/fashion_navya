import frappe
from erpnext.stock.dashboard.item_dashboard import get_data


@frappe.whitelist()
def warehouse_check_se(doc,method):
    if not doc.get("__islocal"):
        getitems=[]
        for i in doc.items:
            row=i.idx
            if doc.stock_entry_type in ["Material Transfer for Manufacture","Material Transfer"]:
                data_w=get_data(item_code=i.item_code,warehouse=i.s_warehouse)
                if len(data_w)!=0:
                    if data_w[0]['actual_qty']<0:
                        msg=" {}/row No:- {} Out of Stock".format(i.item_code,row)
                        frappe.throw(msg)

                    if data_w[0]['actual_qty']>0:
                        if data_w[0]['actual_qty']<i.qty:
                            msg=" {}/row No:- {} Out of Stock".format(i.item_code,row)
                            frappe.throw(msg)
                else:
                    msg=" {}/row No:- {} Out of Stock".format(i.item_code,row)
                    frappe.throw(msg)




@frappe.whitelist()
def check_work_flow(doc,method):
    if doc.stock_entry_type in ["Repack",'Material Transfer for Manufacture','Manufacture','Material Transfer'] and  not doc.get("__islocal"):
        olddoc=doc.get_doc_before_save()
        user=frappe.session.user
        if olddoc.workflow_state in ['Authorised','Received']:
            print(olddoc.workflow_state,'olddoc.workflow_state')
            if olddoc.workflow_state=="Authorised" and doc.workflow_state=="Received":
                if olddoc.owner==user:
                    print(olddoc.owner,doc.owner)
                    msg="Sorry You cannot proceed,because If you have authorised this Record then you can not receive ."
                    frappe.throw(msg)


@frappe.whitelist()
def check_warehouse_wise_wrkflw(doc,method):
    user=frappe.session.user
    roles=frappe.get_roles(user)
    t_warehouse=[]
    stock_t_warehouse=[]
    sales_roles=['Sales Manager','Sales Team']
    stock_roles=['Stock Team','Manufacturing team']
    se=frappe.get_all("Permitted Files", filters ={'document_name':"Stock Entry"},fields = ['name'])
    if se:
        pfdoc=frappe.get_doc("Permitted Files",se[0]['name'])
        for i in doc.items:
            if i.t_warehouse=="SStore - NAVYA":
                t_warehouse.append(i.t_warehouse)

            else:
                stock_t_warehouse.append(i.t_warehouse)


        if t_warehouse:
            get_pf=frappe.db.sql(""" select location,role from `tabLocation Wise Warehoue` where docstatus=0 and warehouse='{}' and parent='{}'  """.format(t_warehouse[0],pfdoc.name),as_dict=1)
            if get_pf:
                if get_pf[0]['role'] not in sales_roles and get_pf[0]['location']=="Santushti":
                    frappe.throw("It will be receive by Sales team")

        if stock_t_warehouse:
            get_pf=frappe.db.sql(""" select location,role from `tabLocation Wise Warehoue` where docstatus=0 and warehouse='{}' and parent='{}'  """.format(stock_t_warehouse[0],pfdoc.name),as_dict=1)
            if get_pf:
                if get_pf[0]['role'] not in stock_roles  and get_pf[0]['location']=="Sainik Farms":
                    frappe.throw("It will be receive by Stock team")



@frappe.whitelist()
def throw_error_se(doc,method):
	user=frappe.session.user
	con_item=[]
	if doc.stock_entry_type in ['Material Receipt','Material Issue']:
		if doc.stock_entry_type=="Material Issue":
			for i in doc.items:
				item=frappe.get_doc("Item",i.item_code)
				if user in ['sujeets@navyacustom.com']:
					if item.item_group!="Consumable":
						con_item.append("aa")
				else:
					con_item.append('aa')
		if not con_item:
			return
		if user not in ["faeemm@navyacustom.com","sujeets@navyacustom.com","prashant@example.com","design@navyacustom.com","Administrator","pawasthy11@gmail.com","amita@navya.biz","erpsupport@uttamenergy.com"]:
			if doc.owner!="amita@navya.biz":
				frappe.throw("Sorry you can't receive")
@frappe.whitelist()
def count_qty_noc(doc,method):
	noc=[0]
	qty_total=[0]
	ip=[0]
	if not doc.get("__islocal") and doc.docstatus<2:
		for i in doc.items:
			idoc=frappe.get_doc("Item",i.item_code)
			val=idoc.noc*i.qty
			i.db_set("noc",val, update_modified=False)
			if i.qty!=None:
				qty_total.append(i.qty)
			if i.noc!=None:
				noc.append(i.noc)
			if i.items_price!=None:
				ip.append(i.items_price)

	doc.set("tnoc",0)
	doc.set("tip",0)
	doc.set("total_qty",0)
	doc.set("tnoc",sum(noc))
	doc.set("tip",sum(ip))
	doc.set("total_qty",sum(qty_total))


@frappe.whitelist(allow_guest=True)
def updte_incharge_wo(doc,method):
    if doc.work_order and doc.stock_entry_type=="Material Transfer for Manufacture":
        frappe.db.set_value('Work Order',doc.work_order, 'incharge',frappe.session.user, update_modified=False)
        frappe.db.commit()



@frappe.whitelist(allow_guest=True)
def create_tag_m(doc,method):
    get_tag=frappe.db.sql(""" select name from `tabItem Tag` where stock_entry='{}'  """.format(doc.name),as_dict=1)
    if len(get_tag)!=0:
        frappe.delete_doc("Item Tag",get_tag[0]['name'])

    if doc.stock_entry_type=="Manufacture":
        d={"doctype":"Item Tag","stock_entry":doc.name}
        d['automated']=1
        tag=frappe.get_doc(d)
        for i in doc.items:
            if i.is_finished_item==1:
                chec_qty=int(i.qty)
                for k in range(chec_qty):
                    item_doc=frappe.get_doc("Item",i.item_code)
                    ip=frappe.db.sql("""select price_list_rate from `tabItem Price` where workflow_state="Approved" and  item_code='{}'  ORDER BY modified DESC """.format(i.item_code),as_dict=1)
                    row = tag.append("items", {})
                    row.item_code=i.item_code
                    row.item_name=i.item_name
                    row.qty=1
                    row.item_group=item_doc.item_group
                    if len(ip)!=0:
                        row.rate=ip[0]['price_list_rate']
                    else:
                        row.rate=0.0


        if tag.items:
            tag.insert(ignore_permissions=True)
            frappe.msgprint("Item tag is Created")



@frappe.whitelist(allow_guest=True)
def check_item_is_ma(doc,method):
    if doc.items:
        for i in doc.items:
            indx=i.idx
            item=i.item_code
            msg="Sorry Item is not manufactured yet,row no {}".format(indx)
            check_exists=frappe.db.sql(""" select name from `tabStock Entry` where docstatus=1 and stock_entry_type='Manufacture' and name in (select parent from `tabStock Entry Detail` where docstatus=1 and item_code='{}' )  """.format(item),as_dict=1)
            if not check_exists:
                frappe.throw(msg)




@frappe.whitelist(allow_guest=True)
def set_val_rate_item(doc,method):
	if doc.stock_entry_type=="Manufacture":
		for i in doc.items:
			doc_item=frappe.get_doc("Item",i.item_code)
			doc_item.db_set("valuation_rate",i.valuation_rate, update_modified=False)
			doc_item.save(ignore_permissions=True)




@frappe.whitelist(allow_guest=True)
def check_capacity_qty(doc,method):
	if doc.stock_entry_type in ["Manufacture","Send to Subcontractor"]:
		return
	for i in doc.items:
		cp=frappe.db.sql("""select capacity from `tabWarehouse` where name='{}' """.format(i.t_warehouse),as_dict=1)
		if i.t_warehouse:
			data=get_data(item_code=i.item_code,warehouse=i.t_warehouse)
			qty=0
			if len(data)!=0:
				for j in data:
					if j['actual_qty']>0:
						qty +=j['actual_qty']

			qty_t=qty+i.qty
			if int(cp[0]['capacity'])<qty_t:
				frappe.throw("Sorry ,No space left on Warehouse row - {}".format(i.idx))

@frappe.whitelist(allow_guest=True)
def fetch_price_sed(doc,method):
	for i in doc.items:
		rate=frappe.db.sql("""select price_list_rate from `tabItem Price` where workflow_state="Approved" and item_code='{}' ORDER BY modified DESC   """.format(i.item_code),as_dict=1)
		if len(rate)!=0:
			i.set("items_price",rate[0]['price_list_rate'])





@frappe.whitelist(allow_guest=True)
def create_tag_m_all(name=None):
    if name:
        doc=frappe.get_doc("Stock Entry",name)
        get_tag=frappe.db.sql(""" select name from `tabItem Tag` where stock_entry='{}'  """.format(doc.name),as_dict=1)
        if len(get_tag)!=0:
            frappe.delete_doc("Item Tag",get_tag[0]['name'])

        if doc.stock_entry_type!="Manufacture":
            d={"doctype":"Item Tag","stock_entry":doc.name}
            d['automated']=1
            tag=frappe.get_doc(d)
            for i in doc.items:
                chec_qty=int(i.qty)
                for k in range(chec_qty):
                    item_doc=frappe.get_doc("Item",i.item_code)
                    ip=frappe.db.sql("""select price_list_rate from `tabItem Price` where workflow_state="Approved" and  item_code='{}'  ORDER BY modified DESC """.format(i.item_code),as_dict=1)
                    row = tag.append("items", {})
                    row.item_code=i.item_code
                    row.item_name=i.item_name
                    row.qty=1
                    row.item_group=item_doc.item_group
                    if len(ip)!=0:
                        row.rate=ip[0]['price_list_rate']
                    else:
                        row.rate=0.0

            if tag.items:
                tag.insert(ignore_permissions=True)
                frappe.msgprint("Item tag is Created")









@frappe.whitelist(allow_guest=True)
def create_phy(name=None):
	doc=frappe.get_doc("Stock Entry",name)
	if doc.stock_entry_type=="Material Transfer":
		d={"doctype":"Physical Stock Count","stock_entry":doc.name}
		tag=frappe.get_doc(d)
		for i in doc.items:
			item_doc=frappe.get_doc("Item",i.item_code)
			row = tag.append("items", {})
			row.item_code=i.item_code
			row.warehouse=i.s_warehouse
			row.aqty=i.qty
		if tag.items:
			tag.insert(ignore_permissions=True)
			frappe.msgprint("Physical is Created")

