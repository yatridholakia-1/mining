# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class Batch(Document):
	def after_insert(self):
		self.batch_state = "Created"
		self.date = nowdate()
		self.clear_batch_insights()
		self.save()
	
	def clear_batch_insights(self):
		self.total_required_qty = 0
		self.total_produced_qty = 0
		self.total_delivered_qty = 0
		self.batch_bag_insights = []
		self.batch_polymer_insights = []
		self.blend_insights = []
		self.pallet_code = ""
		self.pallet_required_qty = 0
		self.pallet_issued_qty = 0
		self.pallet_consumed_qty = 0
		self.pallet_remaining_qty = 0
		self.internal_production_insights = []
		self.external_production_insights = []
		self.quality_insights = []
		self.delivery_insights = []

	
	def on_submit(self):
		#Setting Req fields in Batch Insights
		self.total_required_qty = self.product_quantity
		for material in self.batch_materials_required:
			if material.material_type == "Bag":
				self.append("batch_bag_insights", {
                    "bag": material.material,  
                    "required_qty": material.quantity,
					"bag_size": material.bag_size
                })

			if material.material_type == "Pallet":
				self.pallet_code = material.material
				self.pallet_required_qty = material.quantity
		
		
		self.save()



	



