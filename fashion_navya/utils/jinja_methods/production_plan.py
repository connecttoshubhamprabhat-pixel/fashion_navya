
import frappe
from collections import defaultdict

def get_grouped_items(item_data):
    consolidated_items = defaultdict(lambda: {"quantity": 0, "item_name": "", "item_code": "", "item_group": ""})

    for item in item_data:
        item_code = item.item_code
        item_name = item.item_name
        quantity = item.quantity

        item_group = frappe.db.get_value("Item", item_code, "item_group")

        if item_code in consolidated_items:
            consolidated_items[item_code]["quantity"] += quantity
        else:
            consolidated_items[item_code] = {
                "item_code": item_code,
                "item_name": item_name,
                "item_group": item_group,
                "quantity": quantity
            }

    consolidated_list = [
        {
            "item_group": item["item_group"],
            "item_code": item["item_code"],
            "item_name": item["item_name"],
            "quantity": round(item["quantity"], 2)
        }
        for item in consolidated_items.values()
    ]

    sorted_result = sorted(consolidated_list, key=lambda x: x["item_group"])

    print("sorted result---------------------------------",sorted_result)

    return sorted_result



from collections import defaultdict

def consolidate_items(item_data):
    consolidated_items = defaultdict(lambda: {"qty": 0, "item_name": "", "production_item": ""})

    for item in item_data:
        production_item = item.production_item
        item_name = item.item_name
        qty = item.qty

        if production_item in consolidated_items:
            consolidated_items[production_item]["qty"] += qty
        else:
            consolidated_items[production_item] = {
                "production_item": production_item,
                "item_name": item_name,
                "qty": qty
            }

    result = []
    for item in consolidated_items.values():
        result.append({
            "production_item": item["production_item"],
            "item_name": item["item_name"],
            "qty": item["qty"]
        })

    print('consolidate---------------',result)
    return result
