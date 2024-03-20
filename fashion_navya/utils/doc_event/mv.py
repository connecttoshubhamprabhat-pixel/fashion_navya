import frappe
from erpnext.stock.dashboard.item_dashboard import get_data


@frappe.whitelist(allow_guest=True)
def fetch_attribues(doc,method):
	if doc.sales_order:
		#frappe.throw("hello")
		so=frappe.get_doc("Sales Order",doc.sales_order)

		items=[]
		for i in so.items:
			items.append(i.item_code)
		for j in  doc.purposes:
			if j.item_code  not in items:
				frappe.throw("This is not an item on the sales order")
				
			j.set("prevdoc_doctype","Sales Order")
			j.set("prevdoc_docname",doc.sales_order)
			get_mr=frappe.db.sql("""select parent from `tabMaterial Request Item` where docstatus<2 and item_code='{}' and sales_order='{}' and parent in (select name from `tabMaterial Request`  where docstatus<2 and material_request_type='Manufacture' )  """.format(j.item_code ,doc.sales_order),as_dict=1)
			if len(get_mr)!=0:
				for  mr in get_mr:
					doc.set('custom_material_request',mr['parent'])

			get_val=frappe.db.sql("""select * from `tabSales Order Item` where docstatus=1 and item_code='{}' and parent='{}'  """.format(j.item_code,so.name),as_dict=1)
			if get_val:
				for m in get_val:
					j.set("custom_bust",m['custom_bust'])
					j.set("custom_top_waist",m['custom_top_waist'])
					j.set("custom_top_hip",m['custom_top_hip'])
					j.set("custom_lower_waist",m['custom_lower_waist'])
					j.set("custom_lower_hip",m['custom_lower_hip'])
					j.set("custom_sleeve_length",m['custom_sleeve_length'])
					j.set("custom_bottom_length",m['custom_bottom_length'])
					j.set("custom_shoulder",m['custom_shoulder'])
			j.set("custom_sales_order",so.name)
			for j in  doc.purposes:
				if not j.prevdoc_docname:
					frappe.throw("Source Doctype is missing")


@frappe.whitelist(allow_guest=True)
def custom_maintence_visit(doc,method):
	for i in doc.purposes:
		if i.custom_sales_order:
			so=frappe.get_doc("Sales Order",i.custom_sales_order)
			for j in so.items:
				if j.item_code==i.item_code:
					frappe.db.sql("""update `tabSales Order Item` set custom_maintenance_visit='{}' where parent='{}' and docstatus=1  """.format(doc.name,so.name))
					frappe.db.commit()
@frappe.whitelist(allow_guest=True)
def make_mr_from_mv(doc,method):
	if doc.custom_visit_for=="Alteration":
		d={"doctype":"Material Request","material_request_type":"Material Transfer"}
		mr=frappe.get_doc(d)
		for i in doc.purposes:
			row = mr.append("items", {})
			row.item_code=i.item_code
			row.qty=1
			row.conversion_factor=1
			row.uom="Nos"

		mr.insert()
		mr.submit()
		frappe.msgprint("MR is created")



@frappe.whitelist(allow_guest=True)
def make_se_entry_mv(doc,method):
	if doc.custom_visit_for=="Alteration":
		if doc.sales_order:
			so=frappe.get_doc("Sales Order",doc.sales_order)
			santushti_w=[]
			so_items=[]
			for sitem in so.items:
				if sitem.item_code not in so_items:
					so_items.append(sitem.item_code)

			if so.custom_shop_location=="Sainik Farms":
				get_warehouses=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Santushti - NAVYA'  """,as_dict=1)
				if get_warehouses:
					for w in get_warehouses:
						print(w,"wwwwwwwwwwwwwwwwwwwwwwwwww")
						if w['name'] not in santushti_w:
							santushti_w.append(w['name'])

			d={"doctype":"Stock Entry","stock_entry_type":"Material Transfer"}
			d['rfse']="Return of Alterations"
			yes_make=[]
			se=frappe.get_doc(d)
			for k in doc.purposes:
				itemdoc=frappe.get_doc("Item",k.item_code)
				if k.item_code in so_items and itemdoc.item_group=="Ready Stock":
					datas=get_data(item_code=k.item_code)
					if datas:
						count=0
						for  n in datas:
							print(n,'n')
							print(santushti_w)
							print(n['warehouse'])
							if count==1:
								continue

							if n['warehouse'] in santushti_w and n['actual_qty']>0 and n['item_code']==k.item_code and count==0:
								count+=1
								print("no")
								row=se.append("items", {})
								row.item_code=itemdoc.name
								row.uom=itemdoc.stock_uom
								row.conversion_factor=1
								row.s_warehouse=n['warehouse']
								row.t_warehouse="Navya Store Office - NAVYA"
								yes_make.append("aa")

			if yes_make:
				try:
					se.insert(ignore_permissions=True)
					frappe.msgprint("Stock Entry is created successfully")
				except:
					frappe.msgprint("Not Created Entry")


	