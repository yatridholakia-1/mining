# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document
from ..api import add_polymer_insigts

class AssignPolymer(Document):
	def before_submit(self):
		#Validate Assign
		batch_assignment_exists = frappe.db.exists(
            'Assign Polymer',
            {
                'batch': self.batch,
                'docstatus': 1,
				'enabled': 1 ,
				'reassigned_from': ""
            },
        )
		
		if batch_assignment_exists:
			frappe.throw("Polymer is already assided to this batch!")

		#Disable Old Polymer Assignment 
		if self.reassigned_from:
			old_polymer_assignment = frappe.get_doc("Assign Polymer", self.reassigned_from)
			old_polymer_assignment.enabled = 0
			old_polymer_assignment.save()
	
	def on_submit(self):
		add_polymer_insigts(self.batch, self)

	def before_cancel(self):
		frappe.db.delete("Batch Polymer Insights", {
    	"parent": self.batch
		})

	def after_insert(self):
		self.date=nowdate()
		self.save()
