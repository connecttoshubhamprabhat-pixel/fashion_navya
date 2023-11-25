import frappe
from datetime import datetime # from python std library
from frappe.utils import add_to_date
from erpnext.stock.dashboard.item_dashboard import get_data

@frappe.whitelist()
def check_sample_items(doc,method):
	for i in doc.items:
		item=frappe.get_doc("Item",i.item_code)
		if item.item_group=="Sample":
			frappe.throw("Sample product is not for sale")



@frappe.whitelist()
def get_items(name=None):
	if not name:
		return

	doc=frappe.get_doc("Estimate Sheet",name)
	items=[]
	if doc.so_items:
		for i in doc.so_items:
			d={}
			item=frappe.get_doc("Item",i.item_code)
			d['item_code']=i.item_code
			d['item_name']=item.item_name
			d['qty']=1
			items.append(d)
	if items:
		return items



@frappe.whitelist()
def delete_item_so(doc,method):
	for i in doc.items:
		if i.item_type in ['Customize','Measure']:
			item=frappe.get_doc("Item",i.item_code)
			if not item.variant_of:
				get_ptt=frappe.db.sql("""select name,docstatus from `tabPattern` where docstatus<2 and item_code='{}'  """.format(item.name),as_dict=1)
				get_bom=frappe.db.sql("""select name,docstatus from `tabBOM` where docstatus <2 and item='{}'  """.format(item.name),as_dict=1)
				if len(get_ptt)!=0:
					for p in get_ptt:
						pt=frappe.get_doc("Pattern",p['name'])
						if p['docstatus']==1:
							pt.cancel()
						else:
							pt.delete()
				if len(get_bom)!=0:
					for b in get_bom:
						bm=frappe.get_doc("BOM",b['name'])
						if b['docstatus']==1:
							bm.cancel()
						else:
							bm.delete()

				item.delete()
				frappe.db.commit()





#make mr request if out of stock
@frappe.whitelist()
def make_mr_so(doc,method):
	so=[]
	if doc.references:
		if doc.references[0].reference_doctype=="Sales Order":
			so.append(doc.references[0].reference_name)
	if so:
		sodoc=frappe.get_doc("Sales Order",so[0])
		get_percent=40/100*sodoc.grand_total
		amt_adv=doc.paid_amount+sodoc.advance_paid
		if get_percent>amt_adv:
			frappe.msgprint("Payment is less then 40 percent")
			return
		maintenance_visit(so=so[0],pe=doc.name)

		target_w=["Navya Store Office - NAVYA"]
		if sodoc.custom_shop_location:
			if frappe.db.exists("Shop Location",sodoc.custom_shop_location):
				wt=frappe.get_doc("Shop Location",sodoc.custom_shop_location)
				if wt.default_warehouse:
					target_w.append(wt.default_warehouse)
		d={"doctype":"Material Request"}
		all_warehouses=[]
		m_req=[]
		t_req=[]
		dd=str(sodoc.delivery_date)
		b_2_days = add_to_date(dd, days=2, as_string=True)
		warehouse=frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse='Santushti - NAVYA'  """,as_dict=1)
		if warehouse:
			for w in warehouse:
				all_warehouses.append(w['name'])
		for i in sodoc.items:
			item=frappe.get_doc("Item",i.item_code)
			qty=[0]
			santushti=[0]
			stock=get_data(item_code=item.name)
			if len(stock)!=0:
				for j in stock:
					if j['actual_qty']>0 and j['warehouse'] in all_warehouses:
						santushti.append(j['actual_qty'])
					if j['actual_qty']>0 and j['warehouse'] not in all_warehouses:
						qty.append(j['actual_qty'])

			remain_qty_santushti=sum(santushti)-i.qty
			subtract_with_total=sum(qty)-abs(remain_qty_santushti)
			if sum(santushti)==0 and sum(qty)==0:
				m_req.append(i.item_code)
				t_req.append(i.item_code)

			if sum(santushti)==0 and sum(qty)!=0:
				t_req.append(i.item_code)

			if remain_qty_santushti<0 and subtract_with_total<0:
				m_req.append(i.item_code)
				t_req.append(i.item_code)

			if remain_qty_santushti<0 and subtract_with_total>=0:
				t_req.append(i.item_code)


		#make MR code per item
		if t_req:
			mr_item_t=list(set(t_req))
			for i in mr_item_t:
				qty=0
				get_id_soi=frappe.db.sql("""select * from `tabSales Order Item` where parent='{}' and docstatus<2 and item_code='{}'  """.format(sodoc.name,i),as_dict=1)
				if len(get_id_soi)!=0:
					for item_qty in get_id_soi:
						qty +=item_qty['qty']


				d={"doctype":"Material Request","material_request_type":"Material Transfer"}
				d['schedule_date']=sodoc.delivery_date
				d['custom_automated']=1
				mr=frappe.get_doc(d)
				row = mr.append("items", {})
				row.warehouse=target_w[-1]
				row.qty=qty
				row.sales_order=sodoc.name
				row.schedule_date=get_id_soi[0]['delivery_date']
				row.item_code=i
				if len(get_id_soi)!=0:
					row.sales_order_item=get_id_soi[0]['name']
					row.custom_delivery_date=get_id_soi[0]['delivery_date']

				mr.insert()
				mr.submit()
				frappe.msgprint("MR created for Transfer")

		if m_req:
			mr_items_m=list(set(m_req))
			for i in mr_items_m:
				qty=0
				get_id_soi=frappe.db.sql("""select * from `tabSales Order Item` where parent='{}' and docstatus<2 and item_code='{}'  """.format(sodoc.name,i),as_dict=1)
				if len(get_id_soi)!=0:
					for item_qty in get_id_soi:
						qty +=item_qty['qty']

				#get_id_soi=frappe.db.sql("""select * from `tabSales Order Item` where parent='{}' and docstatus<2 and item_code='{}'  """.format(sodoc.name,i),as_dict=1)
				m={"doctype":"Material Request","material_request_type":"Manufacture"}
				m['schedule_date']=sodoc.delivery_date
				m['custom_payment_entry']=doc.name
				m['custom_automated']=1
				mrm=frappe.get_doc(m)
				row = mrm.append("items", {})
				row.qty=qty
				row.schedule_date=get_id_soi[0]['delivery_date']
				row.item_code=i
				row.sales_order=sodoc.name
				row.warehouse=target_w[-1]
				if len(get_id_soi)!=0:
					row.sales_order_item=get_id_soi[0]['name']
					row.custom_delivery_date=get_id_soi[0]['delivery_date']

				mrm.insert()
				mrm.submit()
				frappe.msgprint("MR created for Manufacture")

@frappe.whitelist()
def maintenance_visit(so=None,pe=None):
	if not so:
		return

	doc=frappe.get_doc("Sales Order",so)
	d={"doctype":"Maintenance Visit","customer":doc.customer,"completion_status":"Partially Completed"}
	d['sales_order']=doc.name
	d['custom_payment_entry']=pe
	d['custom_visit_for']="Customise"
	mv=frappe.get_doc(d)
	cus=[]
	for i in doc.items:
		item=frappe.get_doc("Item",i.item_code)
		if i.custom_customise_item==1:
			cus.append("yes")
			row=mv.append("purposes", {})
			row.item_code=i.item_code
			row.description=item.name
			row.custom_sales_order=doc.name
			row.custom_bust=i.custom_bust
			row.custom_top_waist=i.custom_top_waist
			row.custom_top_hip=i.custom_top_hip
			row.custom_lower_waist=i.custom_lower_waist
			row.custom_lower_hip=i.custom_lower_hip
			row.custom_sleeve_length=i.custom_sleeve_length
			row.custom_bottom_length=i.custom_bottom_length


	if cus:
		mv.insert(ignore_permissions=True)
		frappe.msgprint("Maintenance Visit created")



@frappe.whitelist()
def make_mr_manual_so(doc,method):
	for i in doc.items:
		if i.sales_order and doc.custom_automated==0:
			user=frappe.session.user
			admin_roles=['Administrator','Managing Director','Amintegral item manager']
			#admin_roles=['aa','edd']
			logged_user=frappe.get_roles(frappe.session.user)
			logged_user_dict,admin_roles_dict=set(logged_user),set(admin_roles)
			super_role=list(admin_roles_dict.intersection(logged_user_dict))
			if not super_role:
				frappe.throw("Sorry,It won't be created manually.")


@frappe.whitelist()
def delete_mr_so(doc,method):
	print(doc.docstatus,"saaaaaaaaaaaaaaa")
	frappe.throw("aaaaaaaaaaaaaa")
	for i in doc.items:
		if i.sales_order and doc.custom_automated==0:
			frappe.msgprint("aa")
			user=frappe.session.user
			#admin_roles=['Administrator','Managing Director','Amintegral item manager']
			admin_roles=['aa','edd']
			logged_user=frappe.get_roles(frappe.session.user)
			logged_user_dict,admin_roles_dict=set(logged_user),set(admin_roles)
			super_role=list(admin_roles_dict.intersection(logged_user_dict))
			if not super_role:
				frappe.throw("Sorry,You cannot cancel.")
