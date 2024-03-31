import frappe
from erpnext.accounts.doctype.pos_invoice.pos_invoice import POSInvoice
from frappe import _
from frappe.utils import cint, flt, get_link_to_form, getdate, nowdate
from fashion_navya.utils.overides.pos import get_stock_availability_custom


class CustomPOSInvoice(POSInvoice):
	def validate_stock_availablility(self):
		if self.is_return:
			return

		if self.docstatus.is_draft() and not frappe.db.get_value(
			"POS Profile", self.pos_profile, "validate_stock_on_save"
		):
			return


		from erpnext.stock.stock_ledger import is_negative_stock_allowed
		for d in self.get("items"):
			if d.serial_no:
				print()
				#self.validate_pos_reserved_serial_nos(d)
				#self.validate_delivered_serial_nos(d)
				#self.validate_invalid_serial_nos(d)

			elif d.batch_no:
				self.validate_pos_reserved_batch_qty(d)
			else:
				if is_negative_stock_allowed(item_code=d.item_code):
					return


				available_stock, is_stock_item = get_stock_availability_custom(d.item_code, d.warehouse)


				item_code, warehouse, qty = (
					frappe.bold(d.item_code),
					frappe.bold(d.warehouse),
					frappe.bold(d.qty),
				)
				if is_stock_item and flt(available_stock) <= 0:
					frappe.throw(
						_("Row #{}: Item Code: {} is not available under warehouse {}.").format(
							d.idx, item_code, warehouse
						),
						title=_("Item Unavailable"),)



				elif is_stock_item and flt(available_stock) < flt(d.stock_qty):
					frappe.throw(
						_(
							"Row #{}: Stock quantity not enough for Item Code: {} under warehouse {}. Available quantity {}."
						).format(d.idx, item_code, warehouse, available_stock),
						title=_("Item Unavailable"),
					)

