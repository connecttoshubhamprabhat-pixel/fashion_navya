import frappe



@frappe.whitelist()
def make_notification_logs(doc=None, user=None):
	if doc and user:
		notification = frappe.new_doc("Notification Log")
		notification.update(doc)
		notification.for_user = user
		notification.insert(ignore_permissions=True)

