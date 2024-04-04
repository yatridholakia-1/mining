# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class Production(Document):
		def after_insert(self):
			self.date=nowdate()
			self.save()


				


