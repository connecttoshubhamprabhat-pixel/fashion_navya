import frappe
from erpnext.stock.doctype.item_price.item_price import ItemPrice

class CustomItemPrice(ItemPrice):
    def validate_item_template(self):
        pass
        # if frappe.get_cached_value("Item", self.item_code, "has_variants"):
        #     msg = f"Item Price cannot be created for the template item {bold(self.item_code)}"

        #     frappe.throw((msg))