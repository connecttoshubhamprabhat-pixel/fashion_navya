import frappe
import json


@frappe.whitelist()
def make_events(smpl=None,rtw=None,event=None):
    smpl=json.loads(smpl)
    rtw=json.loads(rtw)
    events=json.loads(event)
    doc=frappe.get_doc("Events",events.get('event_name'))
    if smpl:
        for i in smpl:
            row = doc.append("event_item", {})
            row.item_code=i
    if rtw:
        for j in rtw:
            row = doc.append("event_items", {})
            row.item_code=j
    doc.save()
    frappe.msgprint("Event Updated")
