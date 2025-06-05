import frappe
from collections import defaultdict

def get_grouped_mr_items(item_data):
    consolidated_items = defaultdict(lambda: {"qty": 0, "item_name": "", "item_code": "", "item_group": ""})

    for item in item_data:
        item_code = item.item_code
        item_name = item.item_name
        qty = item.qty

        item_group = frappe.db.get_value("Item", item_code, "item_group")

        if item_code in consolidated_items:
            consolidated_items[item_code]["qty"] += qty
        else:
            consolidated_items[item_code] = {
                "item_code": item_code,
                "item_name": item_name,
                "item_group": item_group,
                "qty": qty
            }

    consolidated_list = [
        {
            "item_group": item["item_group"],
            "item_code": item["item_code"],
            "item_name": item["item_name"],
            "qty": round(item["qty"], 2)
        }
        for item in consolidated_items.values()
    ]

    sorted_result = sorted(consolidated_list, key=lambda x: x["item_group"])

    return sorted_result