import copy
import json
from collections import defaultdict


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, cstr, floor, flt, nowdate

from erpnext.stock.utils import get_stock_balance




@frappe.whitelist()
def apply_putaway_rule(doctype, items, company, sync=None, purpose=None):
	"""Applies Putaway Rule on line items.

	items: List of Purchase Receipt/Stock Entry Items
	company: Company in the Purchase Receipt/Stock Entry
	doctype: Doctype to apply rule on
	purpose: Purpose of Stock Entry
	sync (optional): Sync with client side only for client side calls
	"""
	if isinstance(items, str):
		items = json.loads(items)


	items_not_accomodated, updated_table = [], []
	item_wise_rules = defaultdict(list)

	for item in items:
		if isinstance(item, dict):
			item = frappe._dict(item)

		source_warehouse = item.get("s_warehouse")
		item.conversion_factor = flt(item.conversion_factor) or 1.0
		pending_qty, item_code = flt(item.qty), item.item_code
		pending_stock_qty = flt(item.transfer_qty) if doctype == "Stock Entry" else flt(item.stock_qty)
		uom_must_be_whole_number = frappe.db.get_value("UOM", item.uom, "must_be_whole_number")

		if not pending_qty or not item_code:
			updated_table = add_row(item, pending_qty, source_warehouse or item.warehouse, updated_table)
			continue

		at_capacity, rules = get_ordered_putaway_rules(
			item_code, company, source_warehouse=source_warehouse
		)

		if not rules:
			warehouse = source_warehouse or item.get("warehouse")
			if at_capacity:
				# rules available, but no free space
				items_not_accomodated.append([item_code, pending_qty])
			else:
				updated_table = add_row(item, pending_qty, warehouse, updated_table)
			continue

		# maintain item/item-warehouse wise rules, to handle if item is entered twice
		# in the table, due to different price, etc.
		key = item_code
		if doctype == "Stock Entry" and purpose == "Material Transfer" and source_warehouse:
			key = (item_code, source_warehouse)

		if not item_wise_rules[key]:
			item_wise_rules[key] = rules

		for rule in item_wise_rules[key]:
			if pending_stock_qty > 0 and rule.free_space:
				stock_qty_to_allocate = (
					flt(rule.free_space) if pending_stock_qty >= flt(rule.free_space) else pending_stock_qty
				)
				qty_to_allocate = stock_qty_to_allocate / item.conversion_factor

				if uom_must_be_whole_number:
					qty_to_allocate = floor(qty_to_allocate)
					stock_qty_to_allocate = qty_to_allocate * item.conversion_factor

				if not qty_to_allocate:
					break

				updated_table = add_row(item, qty_to_allocate, rule.warehouse, updated_table, rule.name)

				pending_stock_qty -= stock_qty_to_allocate
				pending_qty -= qty_to_allocate
				rule["free_space"] -= stock_qty_to_allocate

				if not pending_stock_qty > 0:
					break

		# if pending qty after applying all rules, add row without warehouse
		if pending_stock_qty > 0:
			items_not_accomodated.append([item.item_code, pending_qty])

	if items_not_accomodated:
		show_unassigned_items_message(items_not_accomodated)

	if updated_table and _items_changed(items, updated_table, doctype):
		items[:] = updated_table
		frappe.msgprint(_("Applied putaway rules."), alert=True)

	if sync and json.loads(sync):  # sync with client side
		return items
