import frappe


@frappe.whitelist()
def fetch_work_order(doc,method):
	for i in doc.items:
		wk=frappe.db.sql("""select name from `tabWork Order` where docstatus < 2 and bom_no='{}'    """.format(i.bom),as_dict=1)
		if len(wk)!=0:
			doc.set("work_order",wk[0]['name'])


#rate change after submit
@frappe.whitelist()
def update_rate_after_submit(doc,method):
	if doc.docstatus==1:
		get_sub_order=frappe.db.sql("""select name from `tabSubcontracting Order` where docstatus=1 and purchase_order='{}' """.format(doc.name),as_dict=1)
		if get_sub_order:
			so=get_sub_order[0]['name']
			for i in doc.items:
				frappe.db.sql("""update `tabSubcontracting Order Item` set service_cost_per_qty={} where parent='{}' and item_code='{}'  """.format(i.rate,so,i.fg_item))
				frappe.db.commit()

#apr 1 15:30/2024
@frappe.whitelist()
def update_subcontracting_order_item(doc, method):
	# Get fg_parent value from Purchase Order Item for items in doc.purchase_order
	fg_parent_dict = frappe.db.sql("""
        SELECT fg_name_parent, fg_parent
        FROM `tabPurchase Order Item`
        WHERE parent = %(purchase_order)s
    """, {"purchase_order": doc.purchase_order}, as_dict=True)

	# Get item_names associated with doc.name in Subcontracting Order Item
	so_items = frappe.db.sql("""
        SELECT name, item_name
        FROM `tabSubcontracting Order Item`
        WHERE parent = %(subcontracting_order)s
    """, {"subcontracting_order": doc.name}, as_dict=True)


	for so_item in so_items:
		item_name = so_item.get("item_name")
		fg_parent = next((item.get("fg_parent") for item in fg_parent_dict if item.get("fg_name_parent") == item_name), None)

		if fg_parent:
			frappe.db.sql("""UPDATE `tabSubcontracting Order Item`
                SET custom_mitem = %(fg_parent)s
                WHERE name = %(name)s
            """, {"fg_parent": fg_parent, "name": so_item.name})
		else:
			frappe.throw("No fg_parent found for item_name {}".format(item_name))



@frappe.whitelist()
def update_subcontracting_order_and_total(doc, method):
	update_subcontracting_order_item(doc, method)
	calculating_total_miquantity(doc, method)

@frappe.whitelist()
def update_subcontracting_order_item(doc, method):
    # Get fg_parent and custom_qtywo values from Purchase Order Item for items in doc.purchase_order
	 po_items = frappe.db.sql("""
        SELECT fg_parent, custom_qtywo
        FROM `tabPurchase Order Item`
        WHERE parent = %(purchase_order)s
    """, {"purchase_order": doc.purchase_order}, as_dict=True)

    # Update fg_parent and custom_qtywo values for Subcontracting Order Item
	for po_item in po_items:
		fg_parent = po_item.get("fg_parent")
		custom_qtywo = po_item.get("custom_qtywo")
        
        # Update fg_parent and custom_qtywo values for Subcontracting Order Item
		frappe.db.sql("""
            UPDATE `tabSubcontracting Order Item`
            SET custom_mitem = %(fg_parent)s,
                custom_qtywo = %(custom_qtywo)s
            WHERE parent = %(subcontracting_order)s
        """, {"fg_parent": fg_parent, "custom_qtywo": custom_qtywo, "subcontracting_order": doc.name})

@frappe.whitelist()
def calculating_total_miquantity(doc, method):
    # Update total_custom_qtywo value in the document
	total_custom_qtywo = frappe.db.sql("""
        SELECT SUM(custom_qtywo) as total_qty
        FROM `tabPurchase Order Item`
        WHERE parent = %(purchase_order)s
    """, {"purchase_order": doc.purchase_order}, as_dict=True)[0].get('total_qty') or 0
	
	frappe.db.set_value("Subcontracting Order", doc.name, "custom_total_custom_qtywo", total_custom_qtywo)