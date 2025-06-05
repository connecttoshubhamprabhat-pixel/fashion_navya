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


@frappe.whitelist()
def populate_estimate_sheet_prices(docname):
    # Fetching Estimate Sheet document
    estimate_sheet = frappe.get_doc("Purchase Estimate", docname)

    # Fetching all Estimate Sheet Items
    estimate_sheet_items = estimate_sheet.get("estimate_sheet_item_price")

    for item in estimate_sheet_items:
        # Fetching Purchase Order Items for the respective item_code
        purchase_order_items = frappe.get_all("Purchase Receipt Item",
                                              filters={"item_code": item.item_code},
                                              fields=["item_code", "rate"],
                                              order_by="creation DESC")

        if purchase_order_items:
            # Setting last_purchase_price to the rate of the latest Purchase Order Item
            item.last_purchase_price = purchase_order_items[0].rate

            # Finding the lowest_purchase_price
            lowest_price = min(po_item.rate for po_item in purchase_order_items)
            item.lowest_purchase_price = lowest_price

    # Saving the changes
    estimate_sheet.save()

    # Returning success message
    return "Prices populated successfully!"



def calculate_total_amount_fields(doc, method):
    calculate_total_last_purchase_price(doc, method)
    calculate_total_lowest_purchase_price(doc, method)


def calculate_total_last_purchase_price(doc, method):
    total_last_purchase_price = 0

    # Iterate over each row in the child table "estimate_sheet_item_price"
    for row in doc.estimate_sheet_item_price:
        # Calculate subtotal for each row by multiplying last_purchase_price with qty
        subtotal = row.last_purchase_price * row.qty
        total_last_purchase_price += subtotal

    # Update the total_last_purchase_price field in the parent document
    doc.total_last_purchase_price = total_last_purchase_price



def calculate_total_lowest_purchase_price(doc, method):
    total_lowest_purchase_price = 0

    # Iterate over each row in the child table "estimate_sheet_item_price"
    for row in doc.estimate_sheet_item_price:
        # Calculate subtotal for each row by multiplying lowest_purchase_price with qty
        subtotal = row.lowest_purchase_price * row.qty
        total_lowest_purchase_price += subtotal

    # Update the total_lowest_purchase_price field in the parent document
    doc.total_lowest_purchase_price = total_lowest_purchase_price





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










# @frappe.whitelist()
# def create_purchase_order(docname):
#     doc = frappe.get_doc("Purchase Estimate", docname)
#     for items in doc.estimate_sheet_item_price:
#         item_data = frappe.get_doc("Item", {"name":items.item_code})
#         for data in item_data.item_defaults:
#             if not data.default_supplier:
#                 continue
#             if data.default_supplier:
#                 exist_doc = frappe.get_doc("Purchase Order",{"supplier":data.default_supplier})
#                 if exist_doc and exist_doc.supplier == data.default_supplier:
#                     exist_doc.append("items",{
#                         "item_code":items.item_code,
#                         "qty":items.qty,
#                         })
#                     exist_doc.save()
#             new_doc = frappe.new_doc("Purchase Order")
#             new_doc.schedule_date = date.today()
#             new_doc.supplier = data.default_supplier
#             # new_doc.supplier = "Samsudeen Aakil Khan"
#             new_doc.append("items",{
#                 "item_code":items.item_code,
#                 "rate":items.actual_rate,
#                 "qty":items.qty,
#             })
#             new_doc.insert(ignore_permissions=True)
#             new_doc.save()
#             new_doc.submit()

