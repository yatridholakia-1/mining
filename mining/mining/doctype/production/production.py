# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class Production(Document):
		def after_insert(self):
			cleanup(self)

		def on_update_after_submit(self):
			pass

def cleanup(doc):
	doc.date=nowdate()
	doc.status="Scheduled"
	doc.actual_hours = 0
	doc.actual_quantity = 0
	doc.machines_used = []
	doc.save()


				


