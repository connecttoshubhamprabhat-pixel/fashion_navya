import frappe


@frappe.whitelist()
def set_product_name_correct():
	get_wodoc = frappe.get_all('WooCommerce Product', fields=['name','sku'])
	if get_wodoc:
		for i in get_wodoc:
			items = i.get('sku')
			name=i.get('name')
			if frappe.db.exists("Item",items):
				item = frappe.get_doc("Item",items)
				item_name = item.item_name
				print(item_name)
				frappe.db.set_value('WooCommerce Product', name, 'woocommerce_name', item_name)
				frappe.db.set_value('WooCommerce Product', name, 'sku', name)
				frappe.db.commit()

