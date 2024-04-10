################ Script is fecting the item-code and Quantity in the table rows
from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def fetch_items_from_request_for_quotation(request_for_quotation):
    if not request_for_quotation:
        return {"message": "Request for Quotation value is missing"}
        
    items = frappe.db.get_list("Request for Quotation Item",
                               filters={"parent": request_for_quotation},
                               fields=["item_code", "item_code", "item_name",  "item_name", "schedule_date", "qty"],ignore_permissions=True)
                               
    
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
        purchase_order_items = frappe.get_all("Purchase Order Item",
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





