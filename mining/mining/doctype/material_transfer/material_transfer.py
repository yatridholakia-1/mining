# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..enums import Stock, Stock_Purpose, Material_Transfer_Type
from ..api import create_stock_entry, check_stock_balance


class MaterialTransfer(Document):
	def after_insert(self):
		self.date = nowdate()
		self.save()

	def on_submit(self):
		#Validate Stock is present in source warehosue
		#Check if balance exists
		if self.type == Material_Transfer_Type.MATERIAL_ISSUE.value:
			validate_transfer(self.batch, self)
			
		for row in self.material_transfer:
				is_qty_available = check_stock_balance(
					entry_for="Material",
					entry_item= row.material,
					warehouse = row.source_warehouse,
					check_for_quantity=row.quantity)
				
				if not is_qty_available:
					frappe.throw(f"Quantity Not Available In Warehouse: '{row.source_warehouse}' for Material: '{row.material}'")
				
				stock_transfer_entry = create_stock_entry(
				stock_entry_for = "Material",
				stock_entry_item = row.material,
				stock_entry_type = Stock.STOCK_TRANSFER.value,
				stock_entry_purpose = Stock_Purpose.MATERIAL_TRANSFER.value if self.type == "Material Issue" else Stock_Purpose.MATERIAL_RETURN.value,
				source_warehouse = row.source_warehouse,
				target_warehouse = row.target_warehouse,
				quantity = row.quantity,
				created_from_doc = "Material Transfer",
				doc_link = self.name
			)
				row.stock_entry = stock_transfer_entry.name
				self.save()


	
	def on_cancel(self):
		for row in self.material_transfer:
			try:
				frappe.get_doc("Stock Management", row.stock_entry).cancel()
			except Exception as e:
				frappe.throw(f"Failed to cancel Stock Management Document: {e}")
	
def validate_transfer(batch, doc):
	"""
	Check if the material being transfer is actually listed as required material against the batch.
	"""
	batch_doc = frappe.get_doc("Batch", batch)
	for item in doc.material_transfer:
		found = False
		for batch_item in batch_doc.batch_materials_required:
			if item.material_type == batch_item.material_type:
				if item.material == batch_item.material:
					found = True
		if not found:
			frappe.throw(f"Material: {item.material} is not listed as required material in batch: {batch}")






