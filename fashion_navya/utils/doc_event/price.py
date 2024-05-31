import frappe


def create_variant_prices(doc, method):
    if doc.workflow_state=="Approved":
        # Fetch variants of the item
        variants = frappe.get_all('Item', filters={'variant_of': doc.item_code}, fields=['name'])
        
        for variant in variants:
            # Check if a price already exists for the variant in the same price list
            existing_price = frappe.get_all('Item Price', filters={
                'item_code': variant.name,
                'price_list': doc.price_list
                
            })
            
            if not existing_price:
                # Create a new Item Price document for the variant
                item_price = frappe.get_doc({
                    'doctype': 'Item Price',
                    'price_list': doc.price_list,
                    'item_code': variant.name,
                    'price_list_rate': doc.price_list_rate,
                    'currency': doc.currency,
                    'workflow_state': doc.Approved
                })
                
                item_price.insert()
                frappe.msgprint(f'Price created for variant: {variant.name}')
