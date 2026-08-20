from erpnext.stock.doctype.item_price.item_price import ItemPrice


class CustomItemPrice(ItemPrice):
	"""Allow prices on item templates, matching the ERPNext v15 behavior."""

	def validate_item_template(self):
		pass
