# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Production(Document):
	def on_submit(self):
		if self.status != "Finished":
			frappe.throw("Finish Production to Submit.")

