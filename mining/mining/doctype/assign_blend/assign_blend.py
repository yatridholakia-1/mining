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
		
	def before_cancel(self):
		batch = frappe.get_doc('Batch', self.batch)
		if batch.batch_state == "Blend Assigned":
			batch.batch_state = "Created"
			batch.save()
