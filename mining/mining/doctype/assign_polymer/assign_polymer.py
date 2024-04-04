# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document
from ..api import update_polymer_insigts, delete_polymer_insigts

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
			#Validate Re-Assign
			for polymer_item in self.polymers:
				if frappe.db.exists("Batch Polymer Insights", {"polymer": polymer_item.polymer, "required_qty": polymer_item.quantity, "parent": self.batch}):
					frappe.throw(f"Combination Of Polymer and Quantity Must Be Unique For Batch: {self.batch}")

			old_polymer_assignment = frappe.get_doc("Assign Polymer", self.reassigned_from)
			old_polymer_assignment.enabled = 0
			old_polymer_assignment.save()
			update_polymer_insigts(batch=self.batch, doc=old_polymer_assignment)
		
	
	def on_submit(self):
		update_polymer_insigts(self.batch, self)

	def before_cancel(self):
		#Enable Old Polymer Assignment
		if self.reassigned_from:
			old_polymer_assignment = frappe.get_doc("Assign Polymer", self.reassigned_from)
			old_polymer_assignment.enabled = 1
			old_polymer_assignment.save()
			update_polymer_insigts(batch=self.batch, doc=old_polymer_assignment)
			
		delete_polymer_insigts(self.batch, self)


	def after_insert(self):
		self.date=nowdate()
		self.save()
