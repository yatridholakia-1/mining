# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssignBlend(Document):
	def before_submit(self):
		#Validate Assign
		batch_assignment_exists = frappe.db.exists(
            'Assign Blend',
            {
                'batch': self.batch,
                'docstatus': 1,
				'blend': self.blend,
				'enabled': 1
                
            },
        )
		
		if batch_assignment_exists:
			frappe.throw("The Batch Already Has an Assigned Blend!")

		#Change Status of Batch
		batch = frappe.get_doc('Batch', self.batch)
		if batch.batch_state == "Created":
			batch.batch_state = "Blend Assigned"
			batch.save()

		#Disable Old Blend 
		if self.reassigned_from:
			old_blend_assignment = frappe.get_doc("Assign Blend", self.reassigned_from)
			old_blend_assignment.enabled = 0
			old_blend_assignment.save()
		
	def before_cancel(self):
		batch = frappe.get_doc('Batch', self.batch)
		if batch.batch_state == "Blend Assigned":
			batch.batch_state = "Created"
			batch.save()

		#Enable Old Blend 
		if self.reassigned_from:
			old_blend_assignment = frappe.get_doc("Assign Blend", self.reassigned_from)
			old_blend_assignment.enabled = 1
			old_blend_assignment.save()

		# #Disable current blend
		# self.enabled = 0
		# self.save()
				
	def after_submit(self):
		frappe.msgprint("After Submit Triggered")
	
	def after_cancel(self):
		frappe.msgprint("After Cancel Triggered")
	
			
		
