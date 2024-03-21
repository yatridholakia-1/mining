# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class Blend(Document):
	def before_submit(self):
		if self.total_percentage != 100:
			frappe.throw("Total Percentage is not equal to 100!")
	
	def after_insert(self):
		self.date = nowdate()
		self.save()

