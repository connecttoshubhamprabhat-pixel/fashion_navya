import frappe

# Server script for creating an Item from Pattern DocType
@frappe.whitelist()
def create_item_from_pattern(pattern_name, item_group):
	try:
		# Create a new Item document
		item = frappe.get_doc({
            "doctype": "Item",
            "is_stock_item": 0,
            "item_code": pattern_name,
            "item_name": pattern_name,
            "item_group": item_group,
            "asset_category": item_group,
            "stock_uom": "Nos",  # Assuming default stock uom is Nos
            "is_fixed_asset": 1,  # Set default value for is_fixed_asset field
            "is_purchase_item": 1,  # Set default value for is_purchase_item field
            "is_sales_item": 1,  # Set default value for is_sales_item field
            "country_of_origin": "India",  # Set default country_of_origin
            "pattern": pattern_name
        })


		# Save the Item document
		item.insert()

		# Update Pattern doctype field doc.custom_item with doc.name of item
		frappe.db.set_value("Pattern", pattern_name, "custom_item", item.name)

		# Notify user about successful creation and provide a redirect link

		item_redirect_link = frappe.utils.get_url_to_form("Item", item.name)
		msg = f"Item created successfully. <a href='{item_redirect_link}'>{item.name}</a>"
		frappe.msgprint(msg)
		return item.name


	except Exception as e:
		# Print error message if any exception occurs
		# frappe.msgprint(f"Error creating Item: {str(e)}")
		return None


