# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Batch(Document):
	def after_insert(self):
		self.batch_state = "Created"
		self.save()
