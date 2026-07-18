################ Script is fecting the item-code and Quantity in the table rows
from __future__ import unicode_literals
from datetime import date
import frappe
from frappe.utils import today
from frappe import _

@frappe.whitelist()
def fetch_items_from_request_for_quotation(request_for_quotation):
    if not request_for_quotation:
        return {"message": "Request for Quotation value is missing"}
        
    items = frappe.db.get_list("Request for Quotation Item",
                               filters={"parent": request_for_quotation},
                               fields=["item_code", "item_name", "schedule_date", "qty","uom"],ignore_permissions=True)
                               
    
    if not items:
        return {"message": "No items found for the specified Request for Quotation."}
        
    return {"item_details": items}
    
################ Above Script is fecting the item-code and Quantity in the table rows
















############ Final code ###############
# @frappe.whitelist()
# def populate_estimate_sheet_prices(docname):

#     from frappe.utils import getdate

#     # =========================================================
#     # FETCH PURCHASE ESTIMATE
#     # =========================================================

#     estimate_sheet = frappe.get_doc("Purchase Estimate", docname)

#     # =========================================================
#     # CHILD TABLE
#     # =========================================================

#     estimate_sheet_items = estimate_sheet.get("estimate_sheet_item_price")

#     today_date = getdate()

#     for row in estimate_sheet_items:

#         # =====================================================
#         # PURCHASE RECEIPT PRICE FETCH
#         # =====================================================

#         purchase_receipt_items = frappe.get_all(
#             "Purchase Receipt Item",
#             filters={
#                 "item_code": row.item_code,
#                 "uom": row.uom,
#                 "rate": [">", 0],
#                 "docstatus": 1
#             },
#             fields=[
#                 "item_code",
#                 "uom",
#                 "rate"
#             ],
#             order_by="creation DESC"
#         )

#         if purchase_receipt_items:

#             # =================================================
#             # LATEST PURCHASE PRICE
#             # =================================================

#             row.last_purchase_price = purchase_receipt_items[0].rate

#             # =================================================
#             # LOWEST PURCHASE PRICE
#             # =================================================

#             lowest_price = min(
#                 pr_item.rate for pr_item in purchase_receipt_items
#             )

#             row.lowest_purchase_price = lowest_price

#         else:

#             row.last_purchase_price = 0
#             row.lowest_purchase_price = 0

#         # =====================================================
#         # ITEM VALUATION RATE FETCH
#         # =====================================================

#         valuation_rate = frappe.db.get_value(
#             "Item",
#             row.item_code,
#             "valuation_rate"
#         )

#         row.valuation_rate = valuation_rate or 0

#         # =====================================================
#         # ITEM PRICE FETCH
#         # =====================================================

#         item_prices = frappe.get_all(
#             "Item Price",
#             filters={
#                 "item_code": row.item_code,
#                 "uom": row.uom,
#                 "price_list": "Standard buying",
#                 "currency": "INR"
#             },
#             fields=[
#                 "name",
#                 "item_code",
#                 "uom",
#                 "price_list",
#                 "currency",
#                 "price_list_rate",
#                 "valid_from",
#                 "valid_upto"
#             ],
#             order_by="valid_from DESC"
#         )

#         valid_price = None

#         for price in item_prices:

#             # =================================================
#             # SKIP FUTURE VALID_FROM
#             # =================================================

#             if (
#                 price.valid_from
#                 and price.valid_from > today_date
#             ):
#                 continue

#             # =================================================
#             # SKIP EXPIRED VALID_UPTO
#             # =================================================

#             if (
#                 price.valid_upto
#                 and price.valid_upto < today_date
#             ):
#                 continue

#             # =================================================
#             # FIRST VALID RECORD
#             # =================================================

#             valid_price = price
#             break

#         # =====================================================
#         # SET ITEM PRICE
#         # =====================================================

#         if valid_price:
#             row.item_price = valid_price.price_list_rate
#         else:
#             row.item_price = 0

#     # =========================================================
#     # SAVE DOCUMENT
#     # =========================================================

#     estimate_sheet.save(ignore_permissions=True)

#     # return "Prices populated successfully! 1. Latest Purchase Rate, 2. Lowest Purchase Rate, 3. Valuation Rate, 4. Item Price"
#     return "Prices populated successfully! Updated fields: Latest Purchase Rate, Lowest Purchase Rate, Valuation Rate, and Item Price."




######### Final-2 ##############
import frappe


@frappe.whitelist()
def populate_estimate_sheet_prices(doc=None, method=None, docname=None):

    from frappe.utils import getdate

    # =========================================================
    # HANDLE BUTTON CALL
    # =========================================================

    if docname:

        estimate_sheet = frappe.get_doc(
            "Purchase Estimate",
            docname
        )

    # =========================================================
    # HANDLE DOC EVENT CALL
    # =========================================================

    else:

        estimate_sheet = doc

    # =========================================================
    # CHILD TABLE
    # =========================================================

    estimate_sheet_items = estimate_sheet.get(
        "estimate_sheet_item_price"
    )

    today_date = getdate()

    for row in estimate_sheet_items:

        # =====================================================
        # PURCHASE RECEIPT PRICE FETCH
        # =====================================================

        purchase_receipt_items = frappe.get_all(
            "Purchase Receipt Item",
            filters={
                "item_code": row.item_code,
                "uom": row.uom,
                "rate": [">", 0],
                "docstatus": 1
            },
            fields=[
                "item_code",
                "uom",
                "rate"
            ],
            order_by="creation DESC"
        )

        if purchase_receipt_items:

            # =================================================
            # LATEST PURCHASE PRICE
            # =================================================

            row.last_purchase_price = (
                purchase_receipt_items[0].rate
            )

            # =================================================
            # LOWEST PURCHASE PRICE
            # =================================================

            lowest_price = min(
                pr_item.rate
                for pr_item in purchase_receipt_items
            )

            row.lowest_purchase_price = lowest_price

        else:

            row.last_purchase_price = 0
            row.lowest_purchase_price = 0

        # =====================================================
        # ITEM VALUATION RATE FETCH
        # =====================================================

        valuation_rate = frappe.db.get_value(
            "Item",
            row.item_code,
            "valuation_rate"
        )

        row.valuation_rate = valuation_rate or 0

        # =====================================================
        # ITEM PRICE FETCH
        # =====================================================

        item_prices = frappe.get_all(
            "Item Price",
            filters={
                "item_code": row.item_code,
                "uom": row.uom,
                "price_list": "Standard buying",
                "currency": "INR"
            },
            fields=[
                "name",
                "item_code",
                "uom",
                "price_list",
                "currency",
                "price_list_rate",
                "valid_from",
                "valid_upto"
            ],
            order_by="valid_from DESC"
        )

        valid_price = None

        for price in item_prices:

            # =================================================
            # SKIP FUTURE VALID_FROM
            # =================================================

            if (
                price.valid_from
                and price.valid_from > today_date
            ):
                continue

            # =================================================
            # SKIP EXPIRED VALID_UPTO
            # =================================================

            if (
                price.valid_upto
                and price.valid_upto < today_date
            ):
                continue

            # =================================================
            # FIRST VALID RECORD
            # =================================================

            valid_price = price
            break

        # =====================================================
        # SET ITEM PRICE
        # =====================================================

        if valid_price:
            row.item_price = (
                valid_price.price_list_rate
            )
        else:
            row.item_price = 0

    # =========================================================
    # SAVE ONLY FOR BUTTON CALL
    # =========================================================

    if docname:

        estimate_sheet.save(
            ignore_permissions=True
        )

        return (
            "Prices populated successfully! "
            "Updated fields: Latest Purchase Rate, "
            "Lowest Purchase Rate, Valuation Rate, "
            "and Item Price."
        )


























# def calculate_total_amount_fields(doc, method):
#     calculate_total_last_purchase_price(doc, method)
#     calculate_total_lowest_purchase_price(doc, method)


# def calculate_total_last_purchase_price(doc, method):
#     total_last_purchase_price = 0

#     # Iterate over each row in the child table "estimate_sheet_item_price"
#     for row in doc.estimate_sheet_item_price:
#         # Calculate subtotal for each row by multiplying last_purchase_price with qty
#         subtotal = row.last_purchase_price * row.qty
#         total_last_purchase_price += subtotal

#     # Update the total_last_purchase_price field in the parent document
#     doc.total_last_purchase_price = total_last_purchase_price



# def calculate_total_lowest_purchase_price(doc, method):
#     total_lowest_purchase_price = 0

#     # Iterate over each row in the child table "estimate_sheet_item_price"
#     for row in doc.estimate_sheet_item_price:
#         # Calculate subtotal for each row by multiplying lowest_purchase_price with qty
#         subtotal = row.lowest_purchase_price * row.qty
#         total_lowest_purchase_price += subtotal

#     # Update the total_lowest_purchase_price field in the parent document
#     doc.total_lowest_purchase_price = total_lowest_purchase_price
















def calculate_total_amount_fields(doc, method):
    calculate_total_last_purchase_price(doc, method)
    calculate_total_lowest_purchase_price(doc, method)
    calculate_total_price_list_amount(doc, method)
    calculate_total_valuation_rate_amount(doc, method)


def calculate_total_last_purchase_price(doc, method):
    total_last_purchase_price = 0

    for row in doc.estimate_sheet_item_price:
        subtotal = (row.last_purchase_price or 0) * (row.qty or 0)
        total_last_purchase_price += subtotal

    doc.total_last_purchase_price = total_last_purchase_price


def calculate_total_lowest_purchase_price(doc, method):
    total_lowest_purchase_price = 0

    for row in doc.estimate_sheet_item_price:
        subtotal = (row.lowest_purchase_price or 0) * (row.qty or 0)
        total_lowest_purchase_price += subtotal

    doc.total_lowest_purchase_price = total_lowest_purchase_price


def calculate_total_price_list_amount(doc, method):
    total_price_list_amount = 0

    for row in doc.estimate_sheet_item_price:
        subtotal = (row.item_price or 0) * (row.qty or 0)
        total_price_list_amount += subtotal

    doc.total_price_list_amount = total_price_list_amount


def calculate_total_valuation_rate_amount(doc, method):
    total_valuation_rate_amount = 0

    for row in doc.estimate_sheet_item_price:
        subtotal = (row.valuation_rate or 0) * (row.qty or 0)
        total_valuation_rate_amount += subtotal

    doc.total_valuation_rate_amount = total_valuation_rate_amount

























@frappe.whitelist()
def create_purchase_order(docname):
    doc = frappe.get_doc("Purchase Estimate", docname)
    purchase_orders = {}  

    for items in doc.estimate_sheet_item_price:
        item_data = frappe.get_doc("Item", {"name": items.item_code})
        supplier = None

        for data in item_data.item_defaults:
            if data.default_supplier:
                supplier = data.default_supplier
                break  

        if not supplier:
            frappe.msgprint(_("No supplier found for item {0}").format(items.item_code), alert=True)
            continue

        if supplier not in purchase_orders:
            new_doc = frappe.new_doc("Purchase Order")
            new_doc.supplier = supplier
            new_doc.schedule_date = today()
            new_doc.custom_is_invoice = 1
            purchase_orders[supplier] = new_doc  

        purchase_orders[supplier].append("items", {
            "item_code": items.item_code,
            "rate": items.actual_rate,
            "qty": items.qty,
        })

    for supplier, po_doc in purchase_orders.items():
        po_doc.insert(ignore_permissions=True)
        po_doc.submit()
        frappe.msgprint(_("New Purchase Order {0} created for Supplier {1}").format(po_doc.name, supplier))




def purchase_invoice(purchase_order_name, target_doc=None):
    purchase_order = frappe.get_doc("Purchase Order", purchase_order_name)

    if not purchase_order.items:
        frappe.throw(_("Purchase Order {0} has no items").format(purchase_order_name))

    purchase_invoice = frappe.new_doc("Purchase Invoice")
    purchase_invoice.supplier = purchase_order.supplier
    purchase_invoice.company = purchase_order.company
    purchase_invoice.due_date = today()
    purchase_invoice.purchase_order = purchase_order.name

    for item in purchase_order.items:
        purchase_invoice.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate,
            "purchase_order": purchase_order.name,
            "po_detail": item.name,
        })

    purchase_invoice.insert(ignore_permissions=True)
    purchase_invoice.submit()
    frappe.msgprint(_("Purchase Invoice {0} created for Purchase Order {1}").format(purchase_invoice.name, purchase_order_name))


























