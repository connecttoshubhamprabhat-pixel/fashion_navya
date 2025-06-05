import frappe

@frappe.whitelist()
def consolidate_pick_lists(pick_list_names):
    print("consolidate_pick_lists")
    if isinstance(pick_list_names, str):
        pick_list_names = frappe.parse_json(pick_list_names)
    
    consolidated_items = {}

    for pick_list_name in pick_list_names:
        pick_list = frappe.get_doc('Pick List', pick_list_name)

        if pick_list and pick_list.locations:
            for item in pick_list.locations:
                item_code = item.item_code

                if item_code not in consolidated_items:
                    consolidated_items[item_code] = {
                        'item_code': item.item_code,
                        'item_name': item.item_name,
                        'qty': item.qty,
                        'stock_qty': item.stock_qty,
                        'picked_qty': item.picked_qty,
                        'uom': item.uom,
                        'warehouse': item.warehouse
                    }
                else:
                    consolidated_items[item_code]['qty'] += item.qty

    consolidated_pick_list = frappe.new_doc('Pick List')
    consolidated_pick_list.purpose = "Material Transfer"
    consolidated_pick_list.naming_series = 'CONSOL-PICK-.YYYY.-'
    consolidated_pick_list.custom_pick_list_name = 'Consolidated Pick List'
    # consolidated_pick_list.parent_warehouse = 'Courier Station - NAVYA'

    for item in consolidated_items.values():
        consolidated_pick_list.append('locations', {
            'item_code': item['item_code'],
            'item_name': item['item_name'],
            'qty': item['qty'],
            'stock_qty' : item['stock_qty'],
            'picked_qty': item['picked_qty'],
            'uom': item['uom'],
            'warehouse': item['warehouse']
        })
    print('consolidated_pick_list-----',consolidated_pick_list.__dict__)

    consolidated_pick_list.flags.ignore_validate = True
    consolidated_pick_list.insert()
    print("SAVED--------------")
    return consolidated_pick_list.name