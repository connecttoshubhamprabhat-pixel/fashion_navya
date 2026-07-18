# # # Copyright (c) 2026, pawasthy11@gmail.com and contributors
# # # For license information, please see license.txt

# # # import frappe


# # def execute(filters=None):
# # 	columns, data = [], []
# # 	return columns, data
































# import frappe
# from frappe import _
# from frappe.utils import getdate
# from erpnext.stock.report.stock_balance.stock_balance import StockBalanceReport


# def execute(filters=None):

#     filters = frappe._dict(filters or {})

#     # ---------------- VALIDATION ----------------
#     if not filters.get("user"):
#         frappe.throw(_("Please select User"))

#     if not filters.get("from_date"):
#         frappe.throw(_("From Date is required"))

#     if not filters.get("to_date"):
#         frappe.throw(_("To Date is required"))

#     filters.from_date = getdate(filters.from_date)
#     filters.to_date = getdate(filters.to_date)

#     # ---------------- USER WAREHOUSES ----------------
#     warehouses = frappe.get_all(
#         "Location Wise Warehoue",
#         filters={"user": filters.user},
#         pluck="warehouse"
#     )

#     warehouses = sorted({w for w in warehouses if w})

#     if not warehouses:
#         return get_columns([]), []

#     # ---------------- IMPORTANT FIX ----------------
#     # DO NOT pass warehouse into StockBalanceReport
#     filters.pop("warehouse", None)

#     # ---------------- RUN REPORT ----------------
#     stock_report = StockBalanceReport(filters)
#     columns, stock_data = stock_report.run()

#     # ---------------- FILTER AFTER ----------------
#     filtered_data = [
#         row for row in stock_data
#         if row.get("warehouse") in warehouses
#     ]

#     # ---------------- PIVOT ----------------
#     item_map = {}

#     for row in filtered_data:

#         item_code = row.get("item_code")
#         warehouse = row.get("warehouse")
#         qty = row.get("bal_qty") or 0

#         if not item_code or not warehouse:
#             continue

#         if item_code not in item_map:

#             item_map[item_code] = {
#                 "user": filters.user,
#                 "item_code": item_code,
#                 "item_name": row.get("item_name")
#             }

#             for wh in warehouses:
#                 item_map[item_code][frappe.scrub(wh)] = 0

#         item_map[item_code][frappe.scrub(warehouse)] = qty

#     return get_columns(warehouses), list(item_map.values())


# def get_columns(warehouses):

#     columns = [
#         {
#             "label": _("User"),
#             "fieldname": "user",
#             "fieldtype": "Link",
#             "options": "User",
#             "width": 180
#         },
#         {
#             "label": _("Item Code"),
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 180
#         },
#         {
#             "label": _("Item Name"),
#             "fieldname": "item_name",
#             "fieldtype": "Data",
#             "width": 250
#         }
#     ]

#     for wh in warehouses:
#         columns.append({
#             "label": wh,
#             "fieldname": frappe.scrub(wh),
#             "fieldtype": "Float",
#             "width": 140
#         })

#     return columns



















































# ##################################################
# import frappe
# from frappe import _
# from frappe.utils import getdate
# from erpnext.stock.report.stock_balance.stock_balance import StockBalanceReport


# def execute(filters=None):

#     filters = frappe._dict(filters or {})

#     # ---------------- VALIDATION ----------------

#     if not filters.get("user"):
#         frappe.throw(_("Please select User"))

#     if not filters.get("from_date"):
#         frappe.throw(_("From Date is required"))

#     if not filters.get("to_date"):
#         frappe.throw(_("To Date is required"))

#     filters.from_date = getdate(filters.from_date)
#     filters.to_date = getdate(filters.to_date)

#     # ---------------- MULTISELECT WAREHOUSE ----------------

#     warehouses = filters.get("warehouse")

#     if not warehouses:
#         frappe.throw(_("Please select Warehouse"))

#     # MultiSelectList returns comma separated string
#     if isinstance(warehouses, str):

#         warehouses = [
#             d.strip()
#             for d in warehouses.split(",")
#             if d.strip()
#         ]

#     warehouses = sorted(set(warehouses))

#     if not warehouses:
#         return get_columns([]), []

#     # ---------------- IMPORTANT FIX ----------------
#     # DO NOT pass warehouse directly
#     filters.pop("warehouse", None)

#     # ---------------- RUN STOCK REPORT ----------------

#     stock_report = StockBalanceReport(filters)

#     columns, stock_data = stock_report.run()

#     # ---------------- FILTER SELECTED WAREHOUSES ----------------

#     filtered_data = [

#         row for row in stock_data

#         if row.get("warehouse") in warehouses

#     ]

#     # ---------------- PIVOT ----------------

#     item_map = {}

#     for row in filtered_data:

#         item_code = row.get("item_code")
#         warehouse = row.get("warehouse")
#         qty = row.get("bal_qty") or 0

#         if not item_code or not warehouse:
#             continue

#         if item_code not in item_map:

#             item_map[item_code] = {

#                 "user": filters.user,
#                 "item_code": item_code,
#                 "item_name": row.get("item_name")

#             }

#             # Initialize all selected warehouses
#             for wh in warehouses:

#                 item_map[item_code][
#                     frappe.scrub(wh)
#                 ] = 0

#         item_map[item_code][
#             frappe.scrub(warehouse)
#         ] = qty

#     data = list(item_map.values())

#     return get_columns(warehouses), data


# def get_columns(warehouses):

#     columns = [

#         {
#             "label": _("User"),
#             "fieldname": "user",
#             "fieldtype": "Link",
#             "options": "User",
#             "width": 180
#         },

#         {
#             "label": _("Item Code"),
#             "fieldname": "item_code",
#             "fieldtype": "Link",
#             "options": "Item",
#             "width": 180
#         },

#         {
#             "label": _("Item Name"),
#             "fieldname": "item_name",
#             "fieldtype": "Data",
#             "width": 250
#         }

#     ]

#     # Dynamic warehouse columns
#     for wh in warehouses:

#         columns.append({

#             "label": wh,
#             "fieldname": frappe.scrub(wh),
#             "fieldtype": "Float",
#             "width": 140

#         })

#     return columns
# ##############################################################################    # 















######### fashion_navya.fashion_navya.report.user_warehouse_stock_balance.user_warehouse_stock_balance.get_user_warehouses

import frappe
from frappe import _
from frappe.utils import getdate
from erpnext.stock.report.stock_balance.stock_balance import StockBalanceReport


@frappe.whitelist()
def get_user_warehouses(user):

    warehouses = frappe.get_all(
        "Location Wise Warehoue",
        filters={
            "parenttype": "Permitted Files",
            "user": user
        },
        fields=["warehouse"]
    )

    unique_warehouses = sorted(
        list(
            {
                d.warehouse
                for d in warehouses
                if d.warehouse
            }
        )
    )

    return unique_warehouses


def execute(filters=None):

    filters = frappe._dict(filters or {})

    if not filters.get("user"):
        frappe.throw(_("Please select User"))

    if not filters.get("from_date"):
        frappe.throw(_("From Date is required"))

    if not filters.get("to_date"):
        frappe.throw(_("To Date is required"))

    filters.from_date = getdate(filters.from_date)
    filters.to_date = getdate(filters.to_date)

    warehouses = filters.get("warehouse")

    if not warehouses:

        warehouses = get_user_warehouses(
            filters.user
        )

    if isinstance(warehouses, str):

        warehouses = [
            d.strip()
            for d in warehouses.split(",")
            if d.strip()
        ]

    warehouses = sorted(set(warehouses))

    if not warehouses:
        return get_columns([]), []

    filters.pop("warehouse", None)

    stock_report = StockBalanceReport(filters)

    columns, stock_data = stock_report.run()

    filtered_data = [

        row for row in stock_data

        if row.get("warehouse") in warehouses

    ]

    item_map = {}

    for row in filtered_data:

        item_code = row.get("item_code")
        warehouse = row.get("warehouse")
        qty = row.get("bal_qty") or 0

        if not item_code or not warehouse:
            continue

        if item_code not in item_map:

            item_map[item_code] = {

                "user": filters.user,
                "item_code": item_code,
                "item_name": row.get("item_name")

            }

            for wh in warehouses:

                item_map[item_code][
                    frappe.scrub(wh)
                ] = 0

        item_map[item_code][
            frappe.scrub(warehouse)
        ] = qty

    data = list(item_map.values())

    return get_columns(warehouses), data


def get_columns(warehouses):

    columns = [

        {
            "label": _("User"),
            "fieldname": "user",
            "fieldtype": "Link",
            "options": "User",
            "width": 180
        },

        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 180
        },

        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 250
        }

    ]

    for wh in warehouses:

        columns.append({

            "label": wh,
            "fieldname": frappe.scrub(wh),
            "fieldtype": "Float",
            "width": 140

        })

    return columns