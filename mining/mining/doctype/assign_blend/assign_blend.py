# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..api import update_blend_insigts, delete_blend_insigts


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
			batch.save(ignore_permissions=True)

		#Disable Old Blend 
		if self.reassigned_from:
			old_blend_assignment = frappe.get_doc("Assign Blend", self.reassigned_from)
			old_blend_assignment.enabled = 0
			update_blend_insigts(batch=old_blend_assignment.batch, blend=old_blend_assignment.blend, enabled=old_blend_assignment.enabled)
			old_blend_assignment.save(ignore_permissions=True)
		
	def before_cancel(self):
		batch = frappe.get_doc('Batch', self.batch)
		if batch.batch_state == "Blend Assigned":
			batch.batch_state = "Created"
			batch.save(ignore_permissions=True)
		
		#Enable Old Blend 
		if self.reassigned_from:
				old_blend_assignment = frappe.get_doc("Assign Blend", self.reassigned_from)
				old_blend_assignment.enabled = 1
				update_blend_insigts(batch=old_blend_assignment.batch, blend=old_blend_assignment.blend, enabled=old_blend_assignment.enabled)
				old_blend_assignment.save(ignore_permissions=True)

		delete_blend_insigts(self.batch, self.blend)

	def on_submit(self):
		update_blend_insigts(batch=self.batch, blend=self.blend, enabled=self.enabled)

	def after_insert(self):
		self.date=nowdate()
		self.save()
		
		
